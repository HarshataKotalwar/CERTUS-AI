import logging
import pymupdf

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when PDF text cannot be extracted."""


def extract_pdf_text(file_path: str) -> dict[str, int | str]:
    """
    Extracts text and metadata from a PDF.

    Args:
        file_path (str): Path of the uploaded PDF.

    Returns:
        dict: Contains filename, page count,
              character count and extracted text.
    """

    try:
        with pymupdf.open(file_path) as pdf_document:

            extracted_text = ""

            for page in pdf_document:
                extracted_text += page.get_text()

            total_pages = len(pdf_document)
            total_characters = len(extracted_text)

            return {
                "pages": total_pages,
                "characters": total_characters,
                "text": extracted_text
            }

    except PDFExtractionError:
        raise

    except Exception:
        logger.exception("Failed to extract text from the PDF.")
        raise PDFExtractionError(
            "Failed to extract text from the PDF."
        )
