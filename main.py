
import asyncio
from typing import List, Dict, Any
from agents.main_workflow_agents import process_claim_with_agents
import uvicorn
from utilities.extract_text_from_pdf import extract_text_from_pdf
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Claim Processing API",
    description="An API to process uploaded PDF claim documents and return APPROVED or REJECTED decision",
    version="1.0.0"
)

@app.post("/process-claim/", summary="Upload and Process Multiple PDF Claims")
async def process_claim_files(files: List[UploadFile] = File(...)):
    """
    This endpoint accepts one or more PDF files, extracts their text,
    processes the content using a generative AI agent to create a structured JSON,
    and returns the combined results.

    - **files**: A list of PDF files to be processed.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    # Create a list of tasks to run concurrently
    tasks = []
    for file in files:
        if file.content_type != 'application/pdf':
            # Immediately inform the user about invalid file types
            raise HTTPException(
                status_code=415,
                detail=f"Invalid file type for '{file.filename}'. Only PDFs are accepted."
            )

        print(f"Processing file: {file.filename}")
        # Read the file content into memory
        pdf_content = await file.read()
        
        # The extraction is CPU-bound, so it's not truly async, but this is how we call it
        extracted_text = extract_text_from_pdf(pdf_content)

        if not extracted_text.strip():
             # Handle cases of empty or unreadable PDFs
            tasks.append(
                asyncio.create_task(
                    asyncio.sleep(0, result={"file_name": file.filename, "error": "No text could be extracted from the PDF."})
                )
            )
            continue
            
        # Add the orchestrated main agent call to our list of tasks
        tasks.append(
            asyncio.create_task(process_claim_with_agents(extracted_text, file.filename))
        )

    # Wait for all the API calls to complete
    results = await asyncio.gather(*tasks)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Files processed successfully.",
            "results": results
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)