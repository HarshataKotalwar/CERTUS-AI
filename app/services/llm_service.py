from google import genai
from app.config.settings import GOOGLE_API_KEY, MODEL_NAME

# Create Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def ask_gemini(question: str, context: str = ""):
    """
    Sends a question and document context to Gemini
    and returns the response.
    """

    try:
        prompt = f"""
You are CERTUS AI, a document intelligence assistant.

Answer the user's question using ONLY the provided document context.

If the answer cannot be found in the document context,
say:

"I couldn't find that information in the uploaded document."

Do not use your general knowledge.
Do not invent information.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        # Clean the response
        answer = response.text.strip()

        # Remove unnecessary trailing spaces
        answer = "\n".join(
            line.rstrip() for line in answer.splitlines()
        )

        return answer

    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")