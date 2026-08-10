from google import genai
from app.config.settings import GOOGLE_API_KEY, MODEL_NAME

# Create Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def ask_gemini(question: str):
    """
    Sends a question to Gemini and returns the response.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=question
        )

        # Clean the response
        answer = response.text.strip()

        # Remove unnecessary trailing spaces from each line
        answer = "\n".join(line.rstrip() for line in answer.splitlines())

        return answer

    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")