from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.tools import search_document
from google import genai

from app.config.settings import GOOGLE_API_KEY, MODEL_NAME
client = genai.Client(
    api_key=GOOGLE_API_KEY
)


def retrieve_document(state: AgentState):

    question = state["question"]
    messages = state["messages"]

    conversation_context = ""

    for message in messages[-6:]:
        conversation_context += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    search_query = f"""
Conversation:
{conversation_context}

Current Question:
{question}
"""

    result = search_document(search_query)

    return {
    "retrieved_context": result["context"],
    "sources": result["sources"]
}
def generate_answer(state: AgentState):

    question = state["question"]
    context = state["retrieved_context"]

    if (
        not context
        or context.strip()
        == "No relevant information was found in the uploaded document."
    ):
        return {
            "answer": "I couldn't find that information in the uploaded document."
        }

    prompt = f"""
You are CERTUS AI, an intelligent document assistant.

Answer the user's question ONLY using the retrieved document context.

Do not invent facts.
Do not make assumptions.

If the answer is not present in the context,
say:

"I couldn't find that information in the uploaded document."

Retrieved Document Context:
{context}

User Question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return {
    "answer": response.text.strip(),
    "sources": state["sources"]
}

graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "retrieve_document",
    retrieve_document
)

graph_builder.add_node(
    "generate_answer",
    generate_answer
)

graph_builder.add_edge(
    START,
    "retrieve_document"
)

graph_builder.add_edge(
    "retrieve_document",
    "generate_answer"
)

graph_builder.add_edge(
    "generate_answer",
    END
)


graph = graph_builder.compile()