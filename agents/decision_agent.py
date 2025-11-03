from typing import Dict, Any
import google.generativeai as genai
from keys import KEYS

try:
    genai.configure(api_key=KEYS['GOOGLE_API_KEY'])
except Exception as e:
    print(f"Error configuring Google AI. Please set your API key. {e}")

CLAIM_RULES_PROMPT = """
You are a claim decision agent. Using validation findings and extracted data, decide APPROVE or REJECT.
Consider typical rules, for example:
- Dates valid (admission <= discharge), no missing critical identifiers
- Charges non-negative and within plausible bounds for procedures
- Diagnosis and summary plausible and not contradictory
- No ERROR-level validation issues for approval; WARNINGs may still allow approval with notes

Output JSON ONLY in this schema:
{
  "decision": "APPROVE" | "REJECT",
  "rationale": "string",
  "conditions": ["string"],
  "risk_level": "LOW" | "MEDIUM" | "HIGH"
}
"""

async def decide_claim(extracted: Dict[str, Any], validation: Dict[str, Any], file_name: str) -> Dict[str, Any]:
    # model = genai.GenerativeModel('gemini-2.5-flash-lite')
    model = genai.GenerativeModel('gemini-pro-latest')
    prompt = f"""
    File: {file_name}

    Rules:
    ---
    {CLAIM_RULES_PROMPT}
    ---

    Extracted JSON:
    ---
    {extracted}
    ---

    Validation:
    ---
    {validation}
    ---
    """

    response = await model.generate_content_async(prompt)
    cleaned = response.text.strip().replace("```json", "").replace("```", "").strip()
    import json
    try:
        return json.loads(cleaned)
    except Exception:
        return {"decision": "UNKNOWN", "rationale": "Non-JSON decision output.", "conditions": [], "risk_level": "HIGH"}


