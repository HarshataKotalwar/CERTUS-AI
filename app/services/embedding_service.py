from google import genai

from app.config.settings import GOOGLE_API_KEY, EMBEDDING_MODEL


client = genai.Client(
    api_key=GOOGLE_API_KEY
)


def create_embedding(text: str | dict) -> list[float]:

    """
    Creates an embedding for a text chunk.
    """

    # Handle dictionary chunks safely

    if isinstance(text, dict):

        text = text.get(
            "text",
            ""
        )


    text = str(text)


    response = client.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=text

    )


    return response.embeddings[0].values
