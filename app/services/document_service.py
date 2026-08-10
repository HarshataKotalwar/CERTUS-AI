document_text = ""


def save_document(text: str):
    global document_text
    document_text = text


def get_document():
    return document_text