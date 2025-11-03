from typing import Dict, Any, List
from agents.extract_agent import format_data_with_gemini_agent
from agents.validation_agent import validate_extracted_claim
from agents.decision_agent import decide_claim

async def process_claim_with_agents(raw_text: str, file_name: str) -> Dict[str, Any]:
    """
    Orchestrates subagents:
    1) Extraction/formatting
    2) Validation of extracted data against raw text
    3) Decision (approve/reject) based on rules and validations
    """
    extraction_result = await format_data_with_gemini_agent(raw_text, file_name)

    if 'error' in extraction_result:
        return {
            "file_name": file_name,
            "extraction": extraction_result,
            "validation": {"has_errors": True, "validation_summary": "Extraction failed."},
            "decision": {"decision": "REJECT", "rationale": "Extraction failed", "conditions": [], "risk_level": "HIGH"}
        }

    extracted_json = extraction_result.get('data', {})

    validation_result = await validate_extracted_claim(extracted_json, raw_text, file_name)

    decision_result = await decide_claim(extracted_json, validation_result, file_name)

    records: List[Dict[str, Any]] = extracted_json.get("records", []) if isinstance(extracted_json, dict) else []

    documents: List[Dict[str, Any]] = []
    has_any_bill = False
    has_any_discharge = False

    for record in records:
        if any(record.get(k) is not None for k in ["total_charges", "admission_date", "discharge_date"]):
            has_any_bill = True
            documents.append({
                "type": "bill",
                "hospital_name": record.get("hospital_name"),
                "total_amount": record.get("total_charges"),
                "date_of_service": record.get("discharge_date") or record.get("admission_date")
            })

        if any(record.get(k) is not None for k in ["patient_name", "diagnosis", "admission_date", "discharge_date"]):
            has_any_discharge = True
            documents.append({
                "type": "discharge_summary",
                "patient_name": record.get("patient_name"),
                "diagnosis": record.get("diagnosis"),
                "admission_date": record.get("admission_date"),
                "discharge_date": record.get("discharge_date")
            })

    missing_documents: List[str] = []
    if not has_any_bill:
        missing_documents.append("bill")
    if not has_any_discharge:
        missing_documents.append("discharge_summary")

    discrepancies: List[str] = []
    if isinstance(validation_result, dict):
        for rec_issue in validation_result.get("records", []):
            for issue in rec_issue.get("issues", []):
                msg = issue.get("message")
                if msg:
                    discrepancies.append(msg)

    validation_out = {
        "missing_documents": missing_documents,
        "discrepancies": discrepancies
    }

    status = (decision_result or {}).get("decision", "REJECT").lower()
    reason = (decision_result or {}).get("rationale", "")
    risk_level = (decision_result or {}).get("risk_level", "HIGH")
    claim_decision = {"status": status, "reason": reason, "risk_level": risk_level}

    return {
        "documents": documents,
        "validation": validation_out,
        "claim_decision": claim_decision
    }


