import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def extract_text_from_upload(content: bytes, filename: str = "") -> Tuple[str, str]:
    """Extract plain text from uploaded file bytes (PDF or Text).

    Returns:
        (extracted_text, detected_type)
    """
    fname = (filename or "").lower()

    # Case 1: PDF Document
    if fname.endswith(".pdf") or content.startswith(b"%PDF"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    txt = page.extract_text()
                    if txt:
                        pages_text.append(f"--- Page {i+1} ---\n{txt}")
                extracted = "\n\n".join(pages_text).strip()
                if extracted:
                    return extracted, "pdf"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}. Trying fallback...")

        # Fallback using pypdf if available
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            extracted = "\n\n".join(pages_text).strip()
            if extracted:
                return extracted, "pdf"
        except Exception as e:
            logger.warning(f"pypdf extraction failed: {e}")

    # Case 2: Plain Text / Markdown / Other UTF-8
    try:
        text = content.decode("utf-8")
        return text, "text"
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
            return text, "text"
        except Exception as e:
            logger.error(f"Failed to decode uploaded text: {e}")
            return "", "unknown"
