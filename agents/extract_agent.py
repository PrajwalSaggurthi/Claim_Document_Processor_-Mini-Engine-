from typing import Dict, Any
import google.generativeai as genai
import json
from keys import KEYS
JSON_SCHEMA = open('agents/example_schema.json', 'r').read()
try:
    genai.configure(api_key=KEYS['GOOGLE_API_KEY'])
except Exception as e:
    print(f"Error configuring Google AI. Please set your API key. {e}")

async def format_data_with_gemini_agent(text_content: str, file_name: str) -> Dict[str, Any]:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    prompt = f"""
    You are an intelligent data extraction agent. Your task is to analyze the following text extracted from a healthcare document named '{file_name}'.
    The document may contain multiple patient records, including billing information, discharge summaries, and other documents.

    Please perform the following actions:
    1.  Carefully read and understand the entire text provided.
    2.  Identify each distinct patient record within the text.
    3.  For each record, extract the following information:
        - patient_name: The full name of the patient.
        - patient_id: The unique identifier for the patient.
        - admission_date: The date of admission.
        - discharge_date: The date of discharge.
        - total_charges: The total billing amount.
        - diagnosis: A brief summary of the primary diagnosis.
        - summary: The key points from the discharge summary.
    4.  Format the extracted information into a clean, valid JSON object. The root of the object should be a key named "records" which contains a list of all extracted patient records.

    If any piece of information is not found for a record, use a value of `null`.
    Do not include any explanations or text outside of the final JSON object.
    NOTE: ALWAYS GIVE ONLY THE JSON OBJECT, NO OTHER TEXT OR COMMENTS, DONOT CHANGE JSON FORMAT OR ANY OTHER TEXT CAUSING TO BREAK THE JSON FORMAT.
    
    Example JSON SCHEMA:
    {JSON_SCHEMA}

    Here is the text to process:
    ---
    {text_content}
    ---
    """

    try:
        response = await model.generate_content_async(prompt)
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "").strip()
        return {"file_name": file_name, "data": json.loads(cleaned_json_string)}
    except Exception as e:
        print(f"Error processing '{file_name}' with Gemini API: {str(e)}")
        return {"file_name": file_name, "error": f"Failed to process with AI agent: {str(e)}"}
