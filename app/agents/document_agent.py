from google import genai

from app.config.settings import GOOGLE_API_KEY, MODEL_NAME
from app.agents.tools import search_document


client = genai.Client(api_key=GOOGLE_API_KEY)


SYSTEM_PROMPT = """
You are CERTUS AI, an intelligent document assistant.

Your job is to answer questions about documents uploaded by the user.

Use the search_document tool whenever the question requires
information from the uploaded document.

Answer ONLY using information retrieved from the document.

If the required information cannot be found in the document,
say:

"I couldn't find that information in the uploaded document."

Do not invent information.
Do not make assumptions.
"""


def ask_document_agent(question: str):
    """
    Sends a user question to the CERTUS AI document agent.
    """

    try:
        document_context = search_document(question)

        # If no relevant information was retrieved,
        # don't send the question to Gemini.
        if (
            not document_context
            or document_context.strip()
            == "No relevant information was found in the uploaded document."
        ):
            return "I couldn't find that information in the uploaded document."

        prompt = f"""
{SYSTEM_PROMPT}

RETRIEVED DOCUMENT CONTEXT:
{document_context}

USER QUESTION:
{question}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        raise Exception(
            f"Document Agent Error: {str(e)}"
        )