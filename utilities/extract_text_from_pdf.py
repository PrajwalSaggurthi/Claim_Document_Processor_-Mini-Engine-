import PyPDF2
from fastapi import HTTPException
import io 
def extract_text_from_pdf(file_stream) -> str:
    """
    Reads a PDF file stream and extracts all text content.
    """
    try:
        # Ensure we pass a file-like object to PdfReader
        if isinstance(file_stream, (bytes, bytearray)):
            file_obj = io.BytesIO(file_stream)
        else:
            file_obj = file_stream

        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        # Raise an exception that the API endpoint can catch
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")
