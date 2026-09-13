from typing import TypedDict, List


class AgentState(TypedDict):
    messages: List[dict]
    question: str
    retrieved_context: str
    answer: str
    sources: List[dict]