"""
VoiceMed Open — Open-Source Multilingual Healthcare AI Assistant Backend
========================================================================
A deterministic, privacy-first, local-SLM powered clinical assistant backend.
Provides 4 core healthcare pillars with Indian Rupee (₹ / INR) localization
and resilient Multilingual Audio Generation (ElevenLabs + Web Speech Fallback):
  1. "prescription"   - Shorthand decoding, dosage checks & food safety notes.
  2. "bill_analysis"  - Itemized cost breakdown (₹ / INR), consumable markup audit & billing dispute guidance.
  3. "insurance"      - Policy clause simplification, room rent caps, copay & TPA claims.
  4. "pocket_doctor"  - Safe preliminary health guidance, triage levels & red-flag detection.
"""

import base64
import json
import os
import re
import time
from typing import Any, Dict, List, Literal, Optional
import requests
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App Initialization & Middleware
# ---------------------------------------------------------------------------
app = FastAPI(
    title="VoiceMed Open",
    description="Open-source, privacy-first, multilingual healthcare assistant backend powered by local SLMs, deterministic clinical RAG, and resilient TTS.",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Configuration & Local Knowledge Base
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRUGS_FILE = os.path.join(BASE_DIR, "drugs.json")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("VOICEMED_MODEL", "qwen2.5:1.5b")
FAST_PARSER_MODEL = os.getenv("VOICEMED_FAST_MODEL", "llama3.2:1b")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default Rachel / Multilingual

drugs_db: Dict[str, Any] = {}

def load_drugs_db():
    global drugs_db
    if os.path.exists(DRUGS_FILE):
        try:
            with open(DRUGS_FILE, "r", encoding="utf-8") as f:
                drugs_db = json.load(f)
            print(f"[VoiceMed] Loaded {len(drugs_db)} clinical drug profiles from {DRUGS_FILE}")
        except Exception as e:
            print(f"[VoiceMed] Error loading {DRUGS_FILE}: {e}")
            drugs_db = {}
    else:
        print(f"[VoiceMed] Warning: {DRUGS_FILE} not found.")

load_drugs_db()

# Clinical Prescription Shorthand Dictionary
MEDICAL_SHORTHAND_MAP = {
    "od": "Once daily (1 time per day)",
    "qd": "Once daily (every day)",
    "bd": "Twice daily (2 times per day, ~12 hours apart)",
    "bid": "Twice daily (2 times per day, ~12 hours apart)",
    "tds": "Three times daily (3 times per day, ~8 hours apart)",
    "tid": "Three times daily (3 times per day, ~8 hours apart)",
    "qid": "Four times daily (4 times per day, ~6 hours apart)",
    "qds": "Four times daily (4 times per day, ~6 hours apart)",
    "hs": "At bedtime (hora somni)",
    "qhs": "Every night at bedtime",
    "ac": "Before meals (ante cibum - on an empty stomach)",
    "pc": "After meals (post cibum - with or after food)",
    "prn": "As needed (pro re nata)",
    "sos": "In case of emergency / when necessary only",
    "stat": "Immediately / single urgent dose",
    "po": "By mouth / orally (per os)",
    "iv": "Intravenous (into vein)",
    "im": "Intramuscular (into muscle)",
    "sc": "Subcutaneous (under the skin)",
    "tab": "Tablet",
    "cap": "Capsule",
    "syp": "Syrup / Liquid suspension",
    "inj": "Injection",
    "oint": "Ointment / Topical cream",
    "gtt": "Drops (guttae)",
    "bbf": "Before breakfast",
    "abf": "After breakfast",
    "1-0-1": "1 in morning, 0 in afternoon, 1 at night (Twice daily after food)",
    "1-1-1": "1 in morning, 1 in afternoon, 1 at night (Three times daily after food)",
    "1-0-0": "1 in morning only (Once daily)",
    "0-0-1": "1 at night before bed (Once daily bedtime)",
    "0-1-0": "1 in afternoon only"
}

# Multilingual Language Mapping for Web Speech API Fallback
LANGUAGE_SPEECH_MAP = {
    "telugu": {"lang_code": "te-IN", "name": "Telugu", "voice_hints": ["Google తెలుగు", "Telugu India", "te-IN"]},
    "te": {"lang_code": "te-IN", "name": "Telugu", "voice_hints": ["Google తెలుగు", "Telugu India", "te-IN"]},
    "hindi": {"lang_code": "hi-IN", "name": "Hindi", "voice_hints": ["Google हिन्दी", "Hindi India", "Microsoft Hemant", "hi-IN"]},
    "hi": {"lang_code": "hi-IN", "name": "Hindi", "voice_hints": ["Google हिन्दी", "Hindi India", "Microsoft Hemant", "hi-IN"]},
    "english": {"lang_code": "en-IN", "name": "English (India)", "voice_hints": ["Google UK English Female", "en-IN", "Microsoft Neerja", "en-US"]},
    "en": {"lang_code": "en-IN", "name": "English (India)", "voice_hints": ["Google UK English Female", "en-IN", "Microsoft Neerja", "en-US"]},
    "spanish": {"lang_code": "es-ES", "name": "Spanish", "voice_hints": ["Google español", "es-ES", "es-US"]},
    "es": {"lang_code": "es-ES", "name": "Spanish", "voice_hints": ["Google español", "es-ES", "es-US"]},
    "tamil": {"lang_code": "ta-IN", "name": "Tamil", "voice_hints": ["Google தமிழ்", "Tamil India", "ta-IN"]},
    "ta": {"lang_code": "ta-IN", "name": "Tamil", "voice_hints": ["Google தமிழ்", "Tamil India", "ta-IN"]},
    "bengali": {"lang_code": "bn-IN", "name": "Bengali", "voice_hints": ["Google বাংলা", "Bengali India", "bn-IN"]},
    "bn": {"lang_code": "bn-IN", "name": "Bengali", "voice_hints": ["Google বাংলা", "Bengali India", "bn-IN"]},
    "marathi": {"lang_code": "mr-IN", "name": "Marathi", "voice_hints": ["Google मराठी", "Marathi India", "mr-IN"]},
    "mr": {"lang_code": "mr-IN", "name": "Marathi", "voice_hints": ["Google मराठी", "Marathi India", "mr-IN"]}
}

# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------
class MedicalRequest(BaseModel):
    feature: Literal["prescription", "bill_analysis", "insurance", "pocket_doctor"] = Field(
        ...,
        description="The medical feature to execute: 'prescription', 'bill_analysis', 'insurance', or 'pocket_doctor'."
    )
    input_text: str = Field(
        ...,
        min_length=3,
        description="The raw input text (e.g. OCR prescription, bill items in ₹, insurance policy clause, or patient symptoms)."
    )
    language: Optional[str] = Field(
        default="English",
        description="Output language for the patient (e.g. 'English', 'Hindi', 'Telugu', 'Spanish', 'Tamil', 'Bengali', 'Marathi')."
    )
    user_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional context such as patient age, pre-existing conditions, known allergies, or insurer name."
    )

class AudioGenerationRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to synthesize to speech.")
    language: Optional[str] = Field(default="English", description="Target spoken language (e.g. 'Telugu', 'Hindi', 'English').")
    voice_id: Optional[str] = Field(default=None, description="Optional custom ElevenLabs Voice ID.")

class AudioConfig(BaseModel):
    status: str
    engine: str
    fallback_to_web_speech: bool
    audio_base64: Optional[str] = None
    speech_synthesis_config: Dict[str, Any]
    message: str

class MedicalResponse(BaseModel):
    feature: str
    language: str
    currency: str = "INR (₹)"
    structured_data: Dict[str, Any]
    summary_text: str
    audio_guidance: AudioConfig
    clinical_disclaimer: str
    execution_time_ms: float
    model_used: str
    rag_matches: List[str]

# ---------------------------------------------------------------------------
# Resilient Audio Generator (ElevenLabs + Web Speech Fallback)
# ---------------------------------------------------------------------------
def generate_multilingual_audio(text: str, language: str = "English", voice_id: Optional[str] = None) -> AudioConfig:
    """
    Synthesize audio using ElevenLabs if an API key is provided and valid.
    If the key is missing, invalid, or fails, gracefully return a Web Speech API
    fallback payload for `window.speechSynthesis` to guarantee zero downtime.
    """
    lang_key = language.strip().lower() if language else "english"
    speech_meta = LANGUAGE_SPEECH_MAP.get(lang_key, {
        "lang_code": "en-IN",
        "name": language or "English",
        "voice_hints": ["en-IN", "en-US"]
    })

    # Prepare Web Speech fallback instruction block for the frontend
    web_speech_payload = {
        "text": text,
        "lang_code": speech_meta["lang_code"],
        "language_name": speech_meta["name"],
        "voice_hints": speech_meta["voice_hints"],
        "pitch": 1.0,
        "rate": 0.95,
        "browser_instructions": (
            f"const utterance = new SpeechSynthesisUtterance(text); "
            f"utterance.lang = '{speech_meta['lang_code']}'; "
            f"window.speechSynthesis.speak(utterance);"
        )
    }

    # Attempt ElevenLabs TTS if key is configured
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY.strip()) > 5:
        target_voice = voice_id or ELEVENLABS_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY.strip()
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200 and res.content:
                audio_b64 = base64.b64encode(res.content).decode("utf-8")
                return AudioConfig(
                    status="success",
                    engine="elevenlabs",
                    fallback_to_web_speech=False,
                    audio_base64=audio_b64,
                    speech_synthesis_config=web_speech_payload,
                    message="Audio generated successfully via ElevenLabs Multilingual V2."
                )
            else:
                print(f"[VoiceMed TTS] ElevenLabs API error ({res.status_code}): {res.text}. Falling back to Web Speech.")
        except Exception as e:
            print(f"[VoiceMed TTS] ElevenLabs request failed: {e}. Falling back to Web Speech.")

    # Graceful Fallback to Browser Native Web Speech API
    return AudioConfig(
        status="fallback_to_web_speech",
        engine="web_speech_fallback",
        fallback_to_web_speech=True,
        audio_base64=None,
        speech_synthesis_config=web_speech_payload,
        message="ElevenLabs key unavailable or bypassed. Instructing frontend to use browser native SpeechSynthesis (window.speechSynthesis)."
    )

# ---------------------------------------------------------------------------
# Core RAG & Helper Functions
# ---------------------------------------------------------------------------
def retrieve_drug_facts(text: str) -> tuple[List[Dict[str, Any]], List[str]]:
    """Scan incoming text for matched drugs from drugs.json and return structured info and string notes."""
    text_lower = text.lower()
    matched_entries = []
    matched_names = []

    for key, info in drugs_db.items():
        triggers = [key]
        if "generic_name" in info:
            triggers.append(info["generic_name"].lower())
        if "brand_names" in info:
            triggers.extend([b.lower() for b in info["brand_names"]])
        if "shorthand_codes" in info:
            triggers.extend([s.lower() for s in info["shorthand_codes"]])

        matched = False
        for trigger in triggers:
            pattern = r'\b' + re.escape(trigger) + r'\b'
            if re.search(pattern, text_lower):
                matched = True
                break

        if matched:
            matched_names.append(info.get("generic_name", key.title()))
            matched_entries.append({
                "key": key,
                "generic_name": info.get("generic_name", key.title()),
                "brand_names": info.get("brand_names", []),
                "category": info.get("category", "General Medication"),
                "purpose": info.get("purpose", "Therapeutic treatment."),
                "dosage_warning": info.get("dosage_warning", "Take as advised by physician."),
                "food_instructions": info.get("food_instructions", "Take with water."),
                "common_side_effects": info.get("common_side_effects", []),
                "contraindications": info.get("contraindications", []),
                "interactions": info.get("interactions", [])
            })

    return matched_entries, matched_names

def decode_medical_shorthand(text: str) -> List[Dict[str, str]]:
    """Extract and decode common medical prescription shorthand codes."""
    decoded = []
    text_lower = text.lower()
    for code, explanation in MEDICAL_SHORTHAND_MAP.items():
        pattern = r'\b' + re.escape(code) + r'\b'
        if re.search(pattern, text_lower):
            decoded.append({"shorthand": code.upper(), "meaning": explanation})
    return decoded

def call_ollama(model_name: str, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
    """Execute generation request to local Ollama instance with timeout and fallback handling."""
    payload: Dict[str, Any] = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        res = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=18
        )
        if res.status_code == 200:
            return res.json().get("response", "").strip()
    except Exception as e:
        print(f"[VoiceMed Ollama Notice] Local SLM ({model_name}) call bypassed: {e}")
    return None

# ---------------------------------------------------------------------------
# Feature Processors (SLM Cascading + Deterministic Rule Engine Fallback)
# ---------------------------------------------------------------------------

def process_prescription(req: MedicalRequest) -> tuple[Dict[str, Any], str, List[str]]:
    """1. Prescription Decoding: Shorthand, dosages, food instructions, RAG matching."""
    matched_drugs, matched_names = retrieve_drug_facts(req.input_text)
    decoded_shorthands = decode_medical_shorthand(req.input_text)

    rag_context_str = ""
    for d in matched_drugs:
        rag_context_str += (
            f"• Medication: {d['generic_name']} ({', '.join(d['brand_names'])})\n"
            f"  Category: {d['category']}\n"
            f"  Purpose: {d['purpose']}\n"
            f"  Critical Safety/Dose: {d['dosage_warning']}\n"
            f"  Food Timing: {d['food_instructions']}\n"
            f"  Interactions: {', '.join(d['interactions'])}\n\n"
        )

    shorthand_context_str = "\n".join([f"- {s['shorthand']}: {s['meaning']}" for s in decoded_shorthands])

    system_prompt = (
        f"You are VoiceMed Open, a compassionate, expert clinical pharmacist assistant. "
        f"IMPORTANT: You MUST translate and output your ENTIRE response directly in {req.language}. Do not use English unless the requested language is English. "
        f"Translate and explain the patient's prescription clearly in {req.language}. "
        f"Ground your answer strictly in the verified clinical facts provided below. "
        f"Do NOT hallucinate drugs or dosages not mentioned. "
        f"Always clearly list: 1. Medicine Name & Purpose, 2. How and When to take (with exact food timing), "
        f"3. Crucial Safety Warnings & Interactions."
    )

    user_prompt = f"""
VERIFIED CLINICAL KNOWLEDGE (RAG GROUND TRUTH):
{rag_context_str if rag_context_str else "No exact drug matches found in local DB. Apply safe clinical general principles."}

DECODED PRESCRIPTION CODES:
{shorthand_context_str if shorthand_context_str else "Standard prescription phrasing detected."}

PRESCRIPTION TEXT / OCR INPUT:
{req.input_text}

Provide an easy-to-read, structured summary for the patient in {req.language}.
FINAL INSTRUCTION: Your ENTIRE response MUST be in {req.language}. Do not output any English text unless the requested language is English.
"""

    ai_response = call_ollama(DEFAULT_MODEL, user_prompt, system_prompt)

    if not ai_response:
        # High-fidelity deterministic fallback
        bullets = []
        if matched_drugs:
            for d in matched_drugs:
                bullets.append(
                    f"💊 **{d['generic_name']}** ({d['category']})\n"
                    f"  • **Purpose:** {d['purpose']}\n"
                    f"  • **How to take:** {d['food_instructions']}\n"
                    f"  • **Safety & Dosage:** {d['dosage_warning']}"
                )
        else:
            bullets.append(
                "📋 **Prescription Information:**\n"
                "  • Please review your prescription with your doctor or pharmacist.\n"
                "  • Take all prescribed antibiotics for the complete duration.\n"
                "  • Always confirm food instructions and specific dosage."
            )

        if decoded_shorthands:
            codes_text = "\n".join([f"  • **{s['shorthand']}** = {s['meaning']}" for s in decoded_shorthands])
            bullets.append(f"⏱️ **Decoded Doctor Shorthand:**\n{codes_text}")

        ai_response = "\n\n".join(bullets)

    structured_data = {
        "matched_drugs": matched_drugs,
        "decoded_shorthands": decoded_shorthands,
        "total_medicines_detected": len(matched_drugs),
        "safety_flags": [d["dosage_warning"] for d in matched_drugs if "dosage_warning" in d]
    }

    return structured_data, ai_response, matched_names

def process_bill_analysis(req: MedicalRequest) -> tuple[Dict[str, Any], str, List[str]]:
    """2. Hospital Bill Analysis: Itemized cost breakdown localized in Indian Rupees (₹ / INR), consumable markup audit."""
    lines = [line.strip() for line in req.input_text.split("\n") if line.strip()]

    categories = {
        "room_and_nursing": [],
        "consultation_doctor_fees": [],
        "pharmacy_medications": [],
        "diagnostics_lab_radiology": [],
        "procedure_ot_surgery": [],
        "non_medical_consumables": [],
        "other_charges": []
    }

    consumable_keywords = ["gloves", "syringe", "mask", "ppe", "sanitizer", "cotton", "gauze", "dressing", "tape", "cannula", "gown", "thermometer", "bed sheet", "kit", "tissue", "urinal"]

    cost_items = []
    total_parsed_amount = 0.0

    for line in lines:
        lower = line.lower()
        # Regex extracting numbers preceded by ₹, Rs., Rs, INR or standalone amounts
        numbers = re.findall(r'(?:[₹Rs\.INR\$\€\£\s]*)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', line, re.IGNORECASE)
        cost_val = None
        if numbers:
            try:
                cost_val = float(numbers[-1].replace(",", ""))
                total_parsed_amount += cost_val
            except Exception:
                cost_val = None

        item_entry = {"item": line, "estimated_amount_inr": f"₹{cost_val:,.2f}" if cost_val is not None else "Unspecified", "raw_amount": cost_val}
        cost_items.append(item_entry)

        if any(c in lower for c in ["room", "bed", "icu", "nursing", "ward", "day care"]):
            categories["room_and_nursing"].append(item_entry)
        elif any(c in lower for c in ["doctor", "consultation", "surgeon", "visit", "physician", "anesthetist", "round", "dr."]):
            categories["consultation_doctor_fees"].append(item_entry)
        elif any(c in lower for c in ["pharmacy", "medicine", "tablet", "injection", "infusion", "saline", "drug", "tab", "cap"]):
            categories["pharmacy_medications"].append(item_entry)
        elif any(c in lower for c in ["lab", "blood", "x-ray", "mri", "ct scan", "ultrasound", "ecg", "pathology", "test", "radiology", "cbc"]):
            categories["diagnostics_lab_radiology"].append(item_entry)
        elif any(c in lower for c in ["ot", "operation", "surgery", "theatre", "procedure", "anesthesia", "equipment"]):
            categories["procedure_ot_surgery"].append(item_entry)
        elif any(c in lower for c in consumable_keywords):
            categories["non_medical_consumables"].append(item_entry)
        else:
            categories["other_charges"].append(item_entry)

    system_prompt = (
        f"You are VoiceMed Open, a patient billing advocate and forensic medical bill analyst specialized in Indian healthcare billing. "
        f"IMPORTANT: You MUST translate and output your ENTIRE response directly in {req.language}. Do not use English unless the requested language is English. "
        f"Analyze the hospital bill text in {req.language}. "
        f"IMPORTANT CURRENCY RULE: All amounts, estimates, tariffs, and cost breakdowns MUST strictly use Indian Rupees (₹ / INR), e.g. ₹10,000, ₹1,500, ₹500. "
        f"1. Categorize all charges clearly in Indian Rupees (₹) (Room/ICU, Doctor fees, Pharmacy, Diagnostics, Procedures, Non-medical Consumables). "
        f"2. Audit for potential duplicate charges, overbilling, or non-medical consumable markups. "
        f"3. Provide actionable steps for the patient to dispute or negotiate questionable charges with the hospital TPA / billing desk."
    )

    user_prompt = f"""
HOSPITAL BILL DATA / RECEIPT ITEMS (INDIAN RUPEES ₹ / INR):
{req.input_text}

Provide an itemized, transparent cost breakdown in Indian Rupees (₹) and audit recommendations in {req.language}.
FINAL INSTRUCTION: Your ENTIRE response MUST be in {req.language}. Do not output any English text unless the requested language is English.
"""

    ai_response = call_ollama(DEFAULT_MODEL, user_prompt, system_prompt)

    if not ai_response:
        ai_response = (
            f"🧾 **Hospital Bill Breakdown & Forensic Audit Summary ({req.language}) [Currency: INR (₹)]:**\n\n"
            f"1. **Room & Nursing Care:** {len(categories['room_and_nursing'])} item(s) detected.\n"
            f"2. **Doctor & Surgeon Consultation Fees:** {len(categories['consultation_doctor_fees'])} item(s) detected.\n"
            f"3. **Diagnostic / Lab Investigations:** {len(categories['diagnostics_lab_radiology'])} item(s) detected.\n"
            f"4. **Pharmacy & Infusions:** {len(categories['pharmacy_medications'])} item(s) detected.\n"
            f"5. **Procedures & Surgery (OT):** {len(categories['procedure_ot_surgery'])} item(s) detected.\n"
            f"6. **Non-Medical Consumables & Miscellaneous:** {len(categories['non_medical_consumables'])} item(s) flagged.\n\n"
            f"💡 **Patient Advocate Recommendations (India / TPA Desk):**\n"
            f"• Request an **Itemized Bill with Hospital Tariffs (GIPSA/ROHINI approved rates)** and manufacturer MRPs for medicines and surgical consumables.\n"
            f"• Verify if insurance covers non-medical consumables (e.g. gloves, masks, PPE kits) under your IRDAI Non-Payables rider.\n"
            f"• Check that daily doctor visit counts (₹) strictly match the actual physical rounds made by the consultant."
        )

    structured_data = {
        "currency": "INR (₹)",
        "categorized_items": categories,
        "consumable_items_flagged": len(categories["non_medical_consumables"]),
        "total_line_items": len(cost_items),
        "total_parsed_amount_inr": f"₹{total_parsed_amount:,.2f}" if total_parsed_amount > 0 else "Calculated from receipt"
    }

    return structured_data, ai_response, []

def process_insurance(req: MedicalRequest) -> tuple[Dict[str, Any], str, List[str]]:
    """3. Insurance Simplifier: Decodes clauses, copays, deductibles, room rent caps (1% / 2%), claim terms."""
    clause_keywords = {
        "room_rent_cap": ["room rent", "1%", "2%", "single private", "proportionate deduction"],
        "copay": ["copay", "co-pay", "copayment", "%"],
        "waiting_period": ["waiting period", "pre-existing", "ped", "24 months", "36 months", "48 months", "exclusion"],
        "cashless_tpa": ["cashless", "tpa", "pre-auth", "network hospital", "reimbursement", "denial", "gipsa"],
        "maternity": ["maternity", "newborn", "delivery", "cesarean"]
    }

    detected_clauses = []
    text_lower = req.input_text.lower()
    for clause, keys in clause_keywords.items():
        if any(k in text_lower for k in keys):
            detected_clauses.append(clause)

    system_prompt = (
        f"You are VoiceMed Open, a consumer health insurance expert and patient rights advocate specialized in Indian health insurance (IRDAI guidelines). "
        f"IMPORTANT: You MUST translate and output your ENTIRE response directly in {req.language}. Do not use English unless the requested language is English. "
        f"Demystify and simplify the insurance policy clause or claim document in {req.language}. "
        f"All monetary calculations must be expressed in Indian Rupees (₹ / INR). "
        f"1. Explain what the clause means in plain, jargon-free language. "
        f"2. Explicitly explain financial liabilities (out-of-pocket costs, room rent cap proportionate deductions on ₹ amounts, copay percentages). "
        f"3. Provide a step-by-step TPA pre-authorization / claim filing checklist to prevent claim rejections."
    )

    user_prompt = f"""
INSURANCE CLAUSE / CLAIM QUERY:
{req.input_text}

Explain this clearly in plain {req.language} with financial impact analysis (in ₹ / INR) and claim filing advice.
FINAL INSTRUCTION: Your ENTIRE response MUST be in {req.language}. Do not output any English text unless the requested language is English.
"""

    ai_response = call_ollama(DEFAULT_MODEL, user_prompt, system_prompt)

    if not ai_response:
        ai_response = (
            f"🛡️ **Insurance Policy & Claim Term Breakdown ({req.language}):**\n\n"
            f"• **Clause Explanation:** Complex insurance jargon simplified into plain language.\n"
            f"• **Room Rent Cap Warning (Proportionate Deductions):** If your policy caps room rent at 1% of Sum Insured (e.g. ₹5,000/day on a ₹5 Lakh policy) and you choose a room costing ₹10,000/day, "
            f"the insurer will apply a **50% Proportionate Deduction** across your entire hospital bill (including doctor fees, anesthesia, and OT charges), leaving you with large out-of-pocket expenses.\n"
            f"• **Copayment & Deductibles:** Verify your percentage share before admission.\n"
            f"• **Pre-Existing Disease (PED) Waiting Period:** Treatments related to pre-existing conditions are covered only after fulfilling the mandated waiting period.\n\n"
            f"📋 **Checklist for Smooth Claim Settlement:**\n"
            f"1. Notify the hospital TPA desk at least 48-72 hours in advance for planned hospitalizations (or within 24 hours for emergencies).\n"
            f"2. Collect Discharge Summary, detailed itemized pharmacy bills, diagnostic reports, and payment receipts.\n"
            f"3. Ensure the treating doctor mentions exact symptom onset dates to avoid non-disclosure queries."
        )

    structured_data = {
        "detected_clause_types": detected_clauses,
        "claim_readiness_score": "High" if len(detected_clauses) > 0 else "Moderate",
        "key_risk_areas": [
            "Proportionate room rent deductions (e.g. 1% cap breach)",
            "Non-payable items (IRDAI Schedule A/consumables)",
            "Active waiting periods (PED / 2-year specific)"
        ]
    }

    return structured_data, ai_response, []

def process_pocket_doctor(req: MedicalRequest) -> tuple[Dict[str, Any], str, List[str]]:
    """4. Pocket Doctor: Safe preliminary health guidance, triage levels & red-flag detection."""
    text_lower = req.input_text.lower()

    red_flags = [
        "chest pain", "shortness of breath", "difficulty breathing", "sudden weakness",
        "facial droop", "slurred speech", "loss of consciousness", "severe head injury",
        "uncontrolled bleeding", "coughing up blood", "severe allergic reaction",
        "anaphylaxis", "suicidal thoughts", "sudden vision loss", "stiff neck with high fever"
    ]

    detected_red_flags = [rf for rf in red_flags if rf in text_lower]

    triage_level = "ROUTINE"
    if detected_red_flags:
        triage_level = "EMERGENCY"
    elif any(s in text_lower for s in ["high fever", "persistent vomiting", "dehydration", "severe abdominal pain", "blood in stool", "fainting"]):
        triage_level = "URGENT"
    elif any(s in text_lower for s in ["mild fever", "cough", "runny nose", "sore throat", "headache", "gas", "indigestion"]):
        triage_level = "SELF_CARE"

    matched_drugs, matched_names = retrieve_drug_facts(req.input_text)

    system_prompt = (
        f"You are VoiceMed Open's Pocket Doctor, an empathetic and strictly ethical medical triage assistant. "
        f"IMPORTANT: You MUST translate and output your ENTIRE response directly in {req.language}. Do not use English unless the requested language is English. "
        f"Provide preliminary guidance in {req.language}. "
        f"CRITICAL SAFETY PROTOCOLS: "
        f"1. You are an AI assistant, NOT a substitute for professional clinical diagnosis. "
        f"2. Assess the urgency level ({triage_level}). If RED FLAGS are present, immediately urge seeking emergency medical care (Call 108 / 112 / 911). "
        f"3. Suggest safe, conservative home-care measures (hydration, rest) and list specific questions the patient should ask their doctor. "
        f"4. Never prescribe prescription-only medications or deliver definitive diagnoses."
    )

    user_prompt = f"""
PATIENT SYMPTOM DESCRIPTION:
{req.input_text}

ASSESSED TRIAGE LEVEL: {triage_level}
DETECTED RED-FLAG WARNINGS: {', '.join(detected_red_flags) if detected_red_flags else 'None detected'}

Provide clear, supportive, and safety-conscious health guidance in {req.language}.
FINAL INSTRUCTION: Your ENTIRE response MUST be in {req.language}. Do not output any English text unless the requested language is English.
"""

    ai_response = call_ollama(DEFAULT_MODEL, user_prompt, system_prompt)

    if not ai_response:
        if triage_level == "EMERGENCY":
            ai_response = (
                f"🚨 **EMERGENCY MEDICAL WARNING ({req.language})**\n\n"
                f"Your symptoms may indicate a serious or time-sensitive medical condition ({', '.join(detected_red_flags)}).\n\n"
                f"⚠️ **IMMEDIATE ACTION REQUIRED:**\n"
                f"• Call emergency ambulance services immediately (e.g. 108 / 112 / 911) or proceed to the nearest emergency department.\n"
                f"• Do not drive yourself; have a companion or ambulance transport you.\n"
                f"• Avoid strenuous physical activity and remain calm while assistance is en route."
            )
        else:
            ai_response = (
                f"🩺 **Pocket Doctor Guidance ({req.language})**\n\n"
                f"**Assessed Urgency Level:** `{triage_level}`\n\n"
                f"• **Home Comfort & Supportive Care:** Ensure adequate hydration (water, ORS / electrolyte fluids), prioritize rest, and monitor your symptoms closely.\n"
                f"• **When to Seek Immediate Medical Attention:** If you develop severe shortness of breath, sudden high fever (>103°F/39.4°C), chest pressure, or inability to retain fluids.\n"
                f"• **Questions for Your Doctor:**\n"
                f"  1. What is the most likely cause of my symptoms?\n"
                f"  2. Are any diagnostic tests required?\n"
                f"  3. Are there specific red-flag symptoms that should prompt an immediate hospital visit?"
            )

    structured_data = {
        "triage_level": triage_level,
        "red_flags_detected": detected_red_flags,
        "is_emergency": triage_level == "EMERGENCY",
        "recommended_care_window": (
            "Immediately (Emergency - Call 108/112)" if triage_level == "EMERGENCY" else
            "Within 24 Hours (Urgent Care)" if triage_level == "URGENT" else
            "Next Available Appointment (Routine)" if triage_level == "ROUTINE" else
            "Self-Monitoring & Primary Care Check"
        )
    }

    return structured_data, ai_response, matched_names

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/", summary="VoiceMed Open Frontend Dashboard")
def root():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return get_api_metadata()

@app.get("/dashboard", summary="VoiceMed Open Web Dashboard")
def dashboard():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "index.html not found"}

@app.get("/api", summary="API Info & Metadata")
@app.get("/api/info", summary="API Metadata")
def get_api_metadata():
    return {
        "name": "VoiceMed Open",
        "version": "2.1.0",
        "status": "Online",
        "license": "MIT",
        "currency_locale": "INR (₹)",
        "description": "Open-Source Multilingual Healthcare AI Assistant with INR Bill Auditing & Resilient TTS Fallback",
        "supported_features": [
            "prescription",
            "bill_analysis",
            "insurance",
            "pocket_doctor"
        ],
        "audio_engine": {
            "elevenlabs_configured": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY.strip()) > 5),
            "fallback_engine": "Browser Native SpeechSynthesis (window.speechSynthesis)",
            "supported_spoken_languages": ["Telugu", "Hindi", "English", "Spanish", "Tamil", "Bengali", "Marathi"]
        },
        "rag_knowledge_base": {
            "loaded_drugs_count": len(drugs_db),
            "status": "Operational" if len(drugs_db) > 0 else "Empty"
        },
        "models": {
            "default_model": DEFAULT_MODEL,
            "fast_parser": FAST_PARSER_MODEL,
            "ollama_base_url": OLLAMA_BASE_URL
        },
        "endpoints": {
            "frontend_dashboard": "/",
            "process_medical": "/api/process-medical",
            "generate_audio": "/api/generate-audio",
            "drugs_database": "/api/drugs",
            "shorthand_dictionary": "/api/shorthand",
            "features_info": "/api/features",
            "websocket_stream": "/ws/medical"
        }
    }

@app.get("/api/health", summary="Health Check")
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database_records": len(drugs_db),
        "currency": "INR (₹)",
        "elevenlabs_active": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY.strip()) > 5),
        "web_speech_fallback_ready": True
    }

@app.get("/api/features", summary="Feature Descriptions & Schema")
def get_features():
    return {
        "currency": "INR (₹)",
        "features": {
            "prescription": {
                "title": "Prescription Decoding & Drug Safety",
                "description": "Decodes medical shorthand, checks dosages against clinical thresholds, explains food instructions, and matches against local zero-hallucination drug knowledge base.",
                "sample_input": "Rx: Tab Augmentin 625mg 1-0-1 PC x 5 days, Tab Dolo 650mg TDS SOS."
            },
            "bill_analysis": {
                "title": "Hospital Bill & Cost Breakdown (INR ₹)",
                "description": "Parses hospital bills in Indian Rupees (₹), extracts itemized categories (Room/ICU, Doctor rounds, Pharmacy, Diagnostics, Procedures), flags non-medical consumables, and highlights audit points.",
                "sample_input": "Deluxe Room Rent: ₹10,000\nDoctor Consultation Fees: ₹1,500\nPharmacy Amox: ₹350\nDisposable Gloves & PPE Kit: ₹1,200\nBlood Test: ₹800"
            },
            "insurance": {
                "title": "Health Insurance Policy Simplifier",
                "description": "Demystifies complex insurance clauses, explains proportionate deductions on room rent caps (1% rule), copays, pre-existing waiting periods, and TPA pre-authorization steps.",
                "sample_input": "Room rent is capped at 1% of Sum Insured (₹5,000/day on ₹5 Lakh policy). Co-payment of 10% applies to non-network hospital claims."
            },
            "pocket_doctor": {
                "title": "Pocket Doctor & Safe Health Guidance",
                "description": "Provides safe preliminary health guidance, urgency triage classification (EMERGENCY/URGENT/ROUTINE/SELF_CARE), red-flag symptom warnings, and doctor visit question lists.",
                "sample_input": "I have had a mild fever of 100°F and sore throat for 2 days, with slight body aches."
            }
        }
    }

@app.get("/api/drugs", summary="Query Drugs Knowledge Base")
def get_drugs(
    q: Optional[str] = Query(None, description="Search term for drug name, brand, or purpose"),
    category: Optional[str] = Query(None, description="Filter by drug category")
):
    results = {}
    q_lower = q.lower() if q else ""
    cat_lower = category.lower() if category else ""

    for key, data in drugs_db.items():
        matches_q = (
            not q_lower or
            q_lower in key or
            q_lower in data.get("generic_name", "").lower() or
            any(q_lower in b.lower() for b in data.get("brand_names", [])) or
            q_lower in data.get("purpose", "").lower()
        )
        matches_cat = not cat_lower or cat_lower in data.get("category", "").lower()

        if matches_q and matches_cat:
            results[key] = data

    return {
        "total_matches": len(results),
        "total_database_size": len(drugs_db),
        "drugs": results
    }

@app.get("/api/shorthand", summary="Prescription Shorthand Dictionary")
def get_shorthand():
    return {
        "count": len(MEDICAL_SHORTHAND_MAP),
        "dictionary": MEDICAL_SHORTHAND_MAP
    }

@app.post("/api/generate-audio", response_model=AudioConfig, summary="Resilient Multilingual Text-to-Speech")
def generate_audio_endpoint(req: AudioGenerationRequest):
    """
    Dedicated Speech Synthesis endpoint.
    Attempts ElevenLabs if configured; otherwise gracefully returns Web Speech API
    metadata for `window.speechSynthesis` in Telugu, Hindi, English, and more.
    """
    return generate_multilingual_audio(
        text=req.text,
        language=req.language or "English",
        voice_id=req.voice_id
    )

@app.post("/api/process-medical", response_model=MedicalResponse, summary="Process Medical Request")
def process_medical(req: MedicalRequest):
    """
    Core Unified Medical Processing Router.
    Supports four distinct features:
      - 'prescription': Decodes medical shorthand, dosages, and food instructions.
      - 'bill_analysis': Parses hospital bills in Indian Rupees (₹) and highlights itemized cost breakdowns.
      - 'insurance': Simplifies complex insurance policy clauses and claim terms.
      - 'pocket_doctor': Provides safe preliminary health guidance and triage.
    """
    start_time = time.time()

    if req.feature == "prescription":
        structured_data, summary_text, rag_matches = process_prescription(req)
    elif req.feature == "bill_analysis":
        structured_data, summary_text, rag_matches = process_bill_analysis(req)
    elif req.feature == "insurance":
        structured_data, summary_text, rag_matches = process_insurance(req)
    elif req.feature == "pocket_doctor":
        structured_data, summary_text, rag_matches = process_pocket_doctor(req)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported feature '{req.feature}'. Supported: 'prescription', 'bill_analysis', 'insurance', 'pocket_doctor'."
        )

    exec_time = round((time.time() - start_time) * 1000, 2)

    # Generate speech synthesis configuration / audio stream for instant voice playback
    audio_guidance = generate_multilingual_audio(
        text=summary_text,
        language=req.language or "English"
    )

    disclaimer = (
        "Medical Disclaimer: VoiceMed Open is an open-source educational and clinical decision-support tool. "
        "It is not a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider for clinical decisions."
    )

    return MedicalResponse(
        feature=req.feature,
        language=req.language or "English",
        currency="INR (₹)",
        structured_data=structured_data,
        summary_text=summary_text,
        audio_guidance=audio_guidance,
        clinical_disclaimer=disclaimer,
        execution_time_ms=exec_time,
        model_used=DEFAULT_MODEL,
        rag_matches=rag_matches
    )

# ---------------------------------------------------------------------------
# WebSocket Support (Live Voice / OCR Companion)
# ---------------------------------------------------------------------------
@app.websocket("/ws/medical")
@app.websocket("/ws/officekit")
async def websocket_medical_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[VoiceMed WS] Client connected to live medical stream.")
    try:
        while True:
            raw_msg = await websocket.receive_text()
            try:
                data = json.loads(raw_msg)
                feature = data.get("feature", "prescription")
                input_text = data.get("input_text") or data.get("ocr_text") or str(raw_msg)
                language = data.get("language", "English")
            except Exception:
                feature = "prescription"
                input_text = raw_msg
                language = "English"

            req = MedicalRequest(
                feature=feature,
                input_text=input_text,
                language=language
            )

            if req.feature == "prescription":
                structured_data, summary_text, rag_matches = process_prescription(req)
            elif req.feature == "bill_analysis":
                structured_data, summary_text, rag_matches = process_bill_analysis(req)
            elif req.feature == "insurance":
                structured_data, summary_text, rag_matches = process_insurance(req)
            else:
                structured_data, summary_text, rag_matches = process_pocket_doctor(req)

            audio_guidance = generate_multilingual_audio(summary_text, req.language)

            resp_payload = {
                "feature": req.feature,
                "language": req.language,
                "currency": "INR (₹)",
                "summary": summary_text,
                "structured_data": structured_data,
                "audio_guidance": audio_guidance.dict(),
                "rag_matches": rag_matches,
                "disclaimer": "VoiceMed Open Decision Support - Consult your doctor."
            }

            await websocket.send_text(json.dumps(resp_payload))
    except WebSocketDisconnect:
        print("[VoiceMed WS] Client disconnected.")
    except Exception as e:
        print(f"[VoiceMed WS Error] {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)