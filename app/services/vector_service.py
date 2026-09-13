import chromadb
from chromadb.errors import NotFoundError

from app.config.settings import (
    CHROMA_PATH,
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_SPACE,
    N_RESULTS,
)


COLLECTION_NAME = CHROMA_COLLECTION_NAME
DISTANCE_SPACE = CHROMA_DISTANCE_SPACE


# --------------------------------------------------
# CHROMADB SETUP
# --------------------------------------------------

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def _collection_space(collection) -> str:
    configuration = getattr(collection, "configuration", None) or {}
    hnsw = configuration.get("hnsw") or {}
    space = hnsw.get("space")

    if space:
        return space

    metadata = collection.metadata or {}
    return metadata.get("hnsw:space", "l2")


def _get_collection():
    try:
        existing = client.get_collection(
            name=COLLECTION_NAME
        )
    except NotFoundError:
        existing = None

    if existing is None:
        return client.create_collection(
            name=COLLECTION_NAME,
            configuration={
                "hnsw": {
                    "space": DISTANCE_SPACE
                }
            },
            metadata={
                "hnsw:space": DISTANCE_SPACE
            }
        )

    actual_space = _collection_space(existing)

    if actual_space != DISTANCE_SPACE:
        raise RuntimeError(
            f"Existing Chroma collection '{COLLECTION_NAME}' uses "
            f"'{actual_space}' distance, but CERTUS AI now requires "
            f"'{DISTANCE_SPACE}'. Existing chroma_db data was not "
            f"deleted or converted. Rebuild the index manually by "
            f"removing the chroma_db directory and re-uploading "
            f"documents."
        )

    return existing


collection = _get_collection()


# --------------------------------------------------
# ADD CHUNKS
# --------------------------------------------------

def add_chunks(
    chunks: list,
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    """
    Stores document chunks, embeddings and metadata
    in ChromaDB.
    """

    documents = []

    for chunk in chunks:

        # If chunk is a dictionary, extract text
        if isinstance(chunk, dict):
            chunk = chunk.get("text", "")

        # Make sure Chroma receives a string
        chunk = str(chunk)

        documents.append(chunk)


    # Create unique IDs
    ids = []

    for index, metadata in enumerate(metadatas):

        document_id = metadata.get(
            "document_id"
        )

        if not document_id:
            raise ValueError(
                "Each chunk metadata must include document_id."
            )

        chunk_number = metadata.get(
            "chunk",
            index + 1
        )

        ids.append(
            f"{document_id}_chunk_{chunk_number}"
        )


    # Store / update records
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


# --------------------------------------------------
# SEARCH CHUNKS
# --------------------------------------------------

def search_chunks(
    query_embedding: list[float],
    document_id: str,
    n_results: int = N_RESULTS,
) -> dict:
    """
    Searches only the currently selected document.
    """

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],

        n_results=n_results,

        where={
            "document_id": document_id
        }
    )

    return results
