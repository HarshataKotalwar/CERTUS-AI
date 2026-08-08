import fitz  # PyMuPDF


def extract_pdf_text(file_path: str):
    """
    Extracts text and metadata from a PDF.

    Args:
        file_path (str): Path of the uploaded PDF.

    Returns:
        dict: Contains filename, page count,
              character count and extracted text.
    """

    try:
        # Open PDF
        pdf_document = fitz.open(file_path)

        extracted_text = ""

        # Read every page
        for page in pdf_document:
            extracted_text += page.get_text()

        # Metadata
        total_pages = len(pdf_document)
        total_characters = len(extracted_text)

        pdf_document.close()

        return {
            "pages": total_pages,
            "characters": total_characters,
            "text": extracted_text
        }

    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")