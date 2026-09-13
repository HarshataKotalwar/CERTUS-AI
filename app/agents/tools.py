from app.services.embedding_service import create_embedding
from app.services.vector_service import search_chunks


def search_document(
    question: str,
    document_id: str
):
    """
    Searches only the selected uploaded document.
    """

    # Create embedding for question
    query_embedding = create_embedding(question)

    # Search ONLY the selected document
    results = search_chunks(
        query_embedding,
        document_id=document_id
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    # Nothing found
    if not documents:
        return {
            "context": "",
            "sources": []
        }

    # Combine retrieved chunks
    context = "\n\n".join(documents)

    # Build sources
    sources = []

    for metadata in metadatas:

        sources.append({
            "document": metadata.get("document"),
            "chunk": metadata.get("chunk")
        })

    return {
        "context": context,
        "sources": sources
    }