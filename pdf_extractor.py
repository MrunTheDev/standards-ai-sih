import io
from typing import Tuple

def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[bool, str]:
    """
    Extracts text content from uploaded PDF tender or specification document bytes.
    Returns (success: bool, extracted_text_or_error: str)
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                extracted_pages.append(text.strip())
        
        if not extracted_pages:
            return False, "Could not extract plain text from PDF. The document may be scanned (image-only) or password protected."
        
        full_text = "\n\n".join(extracted_pages)
        return True, full_text
    except Exception as e:
        # Fallback check for PyPDF2 if pypdf is missing
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            if extracted_pages:
                return True, "\n\n".join(extracted_pages)
        except Exception:
            pass
        return False, f"Failed to parse PDF document: {str(e)}"
