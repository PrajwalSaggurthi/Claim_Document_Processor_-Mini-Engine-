from typing import Dict, Any
import google.generativeai as genai
from keys import KEYS

try:
    genai.configure(api_key=KEYS['GOOGLE_API_KEY'])
except Exception as e:
    print(f"Error configuring Google AI. Please set your API key. {e}")

async def validate_extracted_claim(extracted: Dict[str, Any], raw_text: str, file_name: str) -> Dict[str, Any]:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    prompt = f"""
    You are a strict validation agent for healthcare claim documents. You are given:
    - Extracted JSON data for file '{file_name}'
    - The raw OCR/text extracted from the PDF

    Tasks:
    1) Validate presence and plausibility of key fields per record (patient_name, patient_id, admission_date,
       discharge_date, total_charges, diagnosis, summary).
    2) Identify inconsistencies between extracted JSON and raw text (dates out of order, discharge before admission,
       missing IDs, malformed dates, negative or implausibly large charges, conflicting diagnoses, etc.).
    3) Summarize issues per record with severity: INFO, WARNING, or ERROR.
    4) Output JSON ONLY in this schema:
       {{
         "validation_summary": "string",
         "records": [
            {{
              "index": number,
              "issues": [{{"field": "string", "severity": "INFO|WARNING|ERROR", "message": "string"}}]
            }}
         ],
         "has_errors": boolean,
         "has_warnings": boolean
       }}

    Extracted JSON:
    ---
    {extracted}
    ---

    Raw Text:
    ---
    {raw_text}
    ---
    """

    response = await model.generate_content_async(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
    import json
    try:
        return json.loads(cleaned)
    except Exception:
        return {"validation_summary": "LLM returned non-JSON", "records": [], "has_errors": True, "has_warnings": True}


