"""
VoiceMed Open — Comprehensive Test Client
=========================================
Tests all four core clinical AI features via `/api/process-medical`:
  1. "prescription"   - Shorthand decoding, dosage threshold checks & food safety notes.
  2. "bill_analysis"  - Itemized cost breakdown (INR ₹), consumable markup flags & audit guidance.
  3. "insurance"      - Policy clause simplification, room rent caps (1% rule) & TPA checklist.
  4. "pocket_doctor"  - Safe preliminary health guidance, urgency triage & red flags.

Also tests:
  - System Healthcheck (`/api/health`)
  - Dedicated Resilient Audio Generation (`/api/generate-audio`) in Telugu, Hindi, and English
  - Error Handling for invalid payloads
"""

import io
import json
import sys
import time
from typing import Any, Dict, Optional
import requests

# Set stdout/stderr encoding to UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
elif sys.stdout:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 15


def print_banner(title: str, character: str = "="):
    line = character * 76
    print(f"\n{line}")
    print(f"  {title}")
    print(f"{line}")


def print_json(data: Any, indent: int = 2):
    try:
        print(json.dumps(data, indent=indent, ensure_ascii=False))
    except Exception as e:
        print(f"[Formatting Error: {e}] {data}")


def check_server_health() -> bool:
    """Check whether the VoiceMed Open backend server is reachable and healthy."""
    print_banner("STEP 1: Checking VoiceMed Open Backend Liveness (127.0.0.1:8000)", "-")
    url = f"{API_BASE_URL}/api/health"
    try:
        start_t = time.time()
        res = requests.get(url, timeout=5)
        elapsed = round((time.time() - start_t) * 1000, 2)

        if res.status_code == 200:
            data = res.json()
            print(f"[SUCCESS] Server is ONLINE at {API_BASE_URL} (Response time: {elapsed} ms)")
            print(f"          Database Records: {data.get('database_records', 'N/A')}")
            print(f"          Currency Locale:  {data.get('currency', 'N/A')}")
            print(f"          ElevenLabs Active: {data.get('elevenlabs_active', False)}")
            print(f"          Web Speech Fallback Ready: {data.get('web_speech_fallback_ready', True)}")
            return True
        else:
            print(f"[WARNING] Server returned status code {res.status_code}: {res.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection Failed: Could not connect to {API_BASE_URL}")
        print("        Please ensure the server is running (e.g. `uvicorn server:app --host 127.0.0.1 --port 8000`).")
        return False
    except Exception as e:
        print(f"[ERROR] Error while checking server health: {e}")
        return False


def test_process_medical_endpoint(
    test_id: int,
    title: str,
    feature: str,
    input_text: str,
    language: str = "English",
    user_context: Optional[Dict[str, Any]] = None,
    expect_error: bool = False
) -> Optional[Dict[str, Any]]:
    """Execute a test case against the /api/process-medical endpoint."""
    print_banner(f"Test Case {test_id}: {title.upper()} [Feature: {feature}]", "=")
    
    payload = {
        "feature": feature,
        "input_text": input_text,
        "language": language,
    }
    if user_context is not None:
        payload["user_context"] = user_context

    print(f"Target Endpoint: POST {API_BASE_URL}/api/process-medical")
    print(f"Target Language: {language}")
    print("\n[Request Payload]")
    print_json(payload)

    start_time = time.time()
    try:
        res = requests.post(
            f"{API_BASE_URL}/api/process-medical",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT_SECONDS
        )
        total_roundtrip = round((time.time() - start_time) * 1000, 2)

        if res.status_code == 200:
            if expect_error:
                print(f"[NOTICE] Expected error but received HTTP 200 OK ({total_roundtrip} ms)")
            else:
                print(f"\n[SUCCESS] HTTP 200 OK | Roundtrip Time: {total_roundtrip} ms")

            data = res.json()

            print(f"Model/Engine Used: {data.get('model_used', 'N/A')} (Backend exec: {data.get('execution_time_ms', 'N/A')} ms)")
            print(f"Currency Format:   {data.get('currency', 'INR (₹)')}")
            print(f"RAG Matched Drugs: {data.get('rag_matches', [])}")

            print("\n" + "="*30 + " Patient Summary " + "="*30)
            print(data.get("summary_text", ""))
            print("="*77)

            print("\n[Audio / TTS Guidance Status]")
            audio_info = data.get("audio_guidance", {})
            print(f"  • Engine: {audio_info.get('engine')}")
            print(f"  • Fallback to Web Speech API: {audio_info.get('fallback_to_web_speech')}")
            print(f"  • Speech Lang Code: {audio_info.get('speech_synthesis_config', {}).get('lang_code')}")
            print(f"  • Message: {audio_info.get('message')}")

            print("\n[Structured Clinical JSON Output]")
            print_json(data.get("structured_data", {}))

            print(f"\nDisclaimer: {data.get('clinical_disclaimer', '')}")
            return data

        else:
            if expect_error:
                print(f"\n[SUCCESS] Handled expected error: HTTP {res.status_code}")
            else:
                print(f"\n[ERROR] HTTP {res.status_code}")
            try:
                err_data = res.json()
                print_json(err_data)
            except Exception:
                print(res.text)
            return None

    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request Timed Out after {TIMEOUT_SECONDS} seconds.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n[ERROR] Connection Error: Unable to reach {API_BASE_URL}/api/process-medical ({e})")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected Exception: {type(e).__name__}: {e}")
        return None


def test_audio_generation(language: str, text: str):
    """Test the dedicated /api/generate-audio endpoint with multilingual fallback."""
    print_banner(f"🎙️ Testing Audio Generation Endpoint ({language})", "-")
    url = f"{API_BASE_URL}/api/generate-audio"
    payload = {"text": text, "language": language}
    try:
        res = requests.post(url, json=payload, timeout=8)
        if res.status_code == 200:
            data = res.json()
            print(f"[SUCCESS] /api/generate-audio response for {language}:")
            print(f"  • Audio Engine: {data.get('engine')}")
            print(f"  • Fallback To Web Speech: {data.get('fallback_to_web_speech')}")
            print(f"  • Browser Lang Code: {data.get('speech_synthesis_config', {}).get('lang_code')}")
            print(f"  • Voice Name Hints: {data.get('speech_synthesis_config', {}).get('voice_hints')}")
            print(f"  • Status Message: {data.get('message')}")
        else:
            print(f"[ERROR] Audio endpoint returned status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[ERROR] Audio generation request failed: {e}")


def run_comprehensive_test_suite():
    """Runs tests for all 4 core features, INR localization, multilingual audio, and error cases."""
    print_banner("VOICEMED OPEN — AUTOMATED COMPREHENSIVE TEST SUITE", "#")
    print(f"Server Base URL: {API_BASE_URL}\n")

    # 1. Healthcheck
    check_server_health()

    # -------------------------------------------------------------------------
    # TEST CASE 1: Prescription Decoding & Dosage Safeguards
    # -------------------------------------------------------------------------
    test_process_medical_endpoint(
        test_id=1,
        title="Prescription Shorthand & Dosage Safeguard",
        feature="prescription",
        input_text="Rx:\n1. Tab Augmentin 625mg 1-0-1 PC x 5 days\n2. Tab Dolo 650mg TDS SOS\n3. Cap Pan 40 1-0-0 AC x 14 days\n4. Tab Cetirizine 10mg 0-0-1 HS",
        language="English",
        user_context={"patient_age": 34, "allergies": ["Sulfa drugs"]}
    )

    # -------------------------------------------------------------------------
    # TEST CASE 2: Hospital Bill & Cost Breakdown (INR ₹)
    # -------------------------------------------------------------------------
    test_process_medical_endpoint(
        test_id=2,
        title="Hospital Bill Cost Audit in Indian Rupees (₹ / INR)",
        feature="bill_analysis",
        input_text=(
            "APOLLO MULTISPECIALTY HOSPITAL - INPATIENT BILLING\n"
            "--------------------------------------------------\n"
            "1. Deluxe Private Room (3 Days): ₹10,000.00 per day = ₹30,000.00\n"
            "2. Critical Care Nursing Fee: ₹4,500.00\n"
            "3. Treating Physician Visit (Dr. Rao 3 visits): ₹4,500.00\n"
            "4. Pharmacy - IV Amoxicillin & Paracetamol: ₹1,480.00\n"
            "5. Disposable PPE Kits & Sterile Gloves (10 sets): ₹3,250.00\n"
            "6. Complete Blood Count (CBC) & Liver Function Test: ₹1,650.00\n"
            "7. OT Sterilization & Equipment Surcharge: ₹8,400.00\n"
            "TOTAL ESTIMATE: ₹53,780.00"
        ),
        language="English"
    )

    # -------------------------------------------------------------------------
    # TEST CASE 3: Health Insurance Clause Simplifier (Multilingual: Hindi)
    # -------------------------------------------------------------------------
    test_process_medical_endpoint(
        test_id=3,
        title="Insurance Policy Clause & Proportionate Room Rent Penalty (Hindi)",
        feature="insurance",
        input_text=(
            "Clause 7.3 (Room Category Limitation): The Room Rent eligibility is capped at 1% of the Sum Insured per day "
            "(e.g. ₹5,000 per day on a ₹5,00,000 Sum Insured policy). If the Insured occupies a room category costing ₹10,000 per day, "
            "the Insurer's liability for all associated medical expenses (including ICU, surgeon fees, and OT charges) shall be reduced "
            "proportionately by 50%. A co-payment of 10% applies to claims from non-network hospitals."
        ),
        language="Hindi"
    )

    # -------------------------------------------------------------------------
    # TEST CASE 4: Pocket Doctor Preliminary Triage (Multilingual: Telugu)
    # -------------------------------------------------------------------------
    test_process_medical_endpoint(
        test_id=4,
        title="Pocket Doctor Symptom Assessment & Emergency Red-Flag Triage (Telugu)",
        feature="pocket_doctor",
        input_text=(
            "Patient report: I have a sudden severe pressure and squeezing chest pain radiating to my left arm "
            "and jaw, accompanied by shortness of breath and cold sweat for the past 20 minutes."
        ),
        language="Telugu"
    )

    # -------------------------------------------------------------------------
    # TEST CASE 5: Dedicated Multilingual Audio Fallback Tests
    # -------------------------------------------------------------------------
    test_audio_generation("Telugu", "మీరు అత్యవసర వైద్య సేవలను సంప్రదించాలి (108).")
    test_audio_generation("Hindi", "कृपया अपने डॉक्टर से परामर्श करें और दवा समय पर लें।")
    test_audio_generation("English", "Take Pan 40 thirty minutes before breakfast on an empty stomach.")

    # -------------------------------------------------------------------------
    # TEST CASE 6: Error Handling - Unsupported Feature
    # -------------------------------------------------------------------------
    test_process_medical_endpoint(
        test_id=6,
        title="Error Handling (Unsupported Feature)",
        feature="invalid_feature_name",
        input_text="Sample test text",
        language="English",
        expect_error=True
    )

    print_banner("ALL VOICEMED OPEN TESTS COMPLETED", "#")


if __name__ == "__main__":
    run_comprehensive_test_suite()