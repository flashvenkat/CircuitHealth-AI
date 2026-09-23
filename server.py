import json
import os
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# Load local RAG knowledge base on startup
DRUGS_FILE = "drugs.json"
drugs_db = {}

if os.path.exists(DRUGS_FILE):
    with open(DRUGS_FILE, "r") as f:
        drugs_db = json.load(f)

def retrieve_drug_facts(ocr_text: str) -> str:
    """Scan incoming OCR text for matched drugs and return verified facts."""
    ocr_lower = ocr_text.lower()
    matched_facts = []

    for drug, info in drugs_db.items():
        if drug in ocr_lower:
            fact_str = (
                f"- Drug: {drug.title()}\n"
                f"  Purpose: {info['purpose']}\n"
                f"  Warning: {info['dosage_warning']}\n"
                f"  Instructions: {info['food_instructions']}"
            )
            matched_facts.append(fact_str)

    if matched_facts:
        return "\n".join(matched_facts)
    return "No exact database match. Apply general safe handling instructions."

def call_ollama(model_name: str, prompt: str) -> str:
    """Helper function to execute Ollama generation requests locally."""
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=30
        )
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"Error calling {model_name}: {str(e)}"

@app.get("/")
def read_root():
    return {
        "status": "CircuitHealth AI Multi-LLM Backend Online",
        "device": "ASUS Vivobook RTX 4050",
        "models_loaded": ["llama3.2:1b", "qwen2.5:1.5b", "llama3.1:8b"],
        "rag_status": "Enabled" if drugs_db else "Disabled"
    }

@app.websocket("/ws/officekit")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Mobile client connected via WebSocket!")
    try:
        while True:
            # Receive raw OCR payload from client
            raw_ocr = await websocket.receive_text()

            # TIER 1: Llama 3.2 1B — Fast OCR Cleaning & Keyword Extraction
            parser_prompt = f"Clean up formatting typos in this prescription OCR text. Output only key drug names and dosages:\n{raw_ocr}"
            cleaned_text = call_ollama("llama3.2:1b", parser_prompt)

            # LOCAL RAG LOOKUP: Match against drugs.json
            verified_facts = retrieve_drug_facts(cleaned_text if cleaned_text else raw_ocr)

            # TIER 2: Qwen 2.5 1.5B — Structured RAG Patient Summarizer
            summarizer_prompt = f"""
            System: You are an expert medical simplifying assistant. Simplify the prescription below for a patient.
            
            VERIFIED CLINICAL FACTS (RAG Context):
            {verified_facts}

            RAW OCR INPUT:
            {raw_ocr}

            Provide a clear 3-bullet-point summary covering:
            1. What the medicine is for
            2. When and how to take it
            3. Safety warnings
            """
            simplified_summary = call_ollama("qwen2.5:1.5b", summarizer_prompt)

            # Return simplified output directly to client
            await websocket.send_text(simplified_summary)

    except WebSocketDisconnect:
        print("Mobile client disconnected.")