from typing import cast
import os
import chromadb
import voyageai

from data.documents import documents


EMBED_MODEL = "voyage-3-lite"
voyage = voyageai.Client(  # type: ignore
    api_key = os.environ["VOYAGE_API_KEY"],
    max_retries = 3,
    timeout = 30,
)

# writes to disk at the path we give it
chroma = chromadb.PersistentClient(
    path="./chroma_store",
)

collection = chroma.get_or_create_collection(
    name="documents",
    configuration={
        # HNSW (Hierarchical Navigable Small World) is a graph based index used in vector databases to perform fast an appropriate kNN search.
        "hnsw": {
            "space" : "cosine"
        }
    }
)

def embed_texts(texts: list[str], input_type: str) -> tuple[ list[list[float]], int]:
    # embed a batch
        # input_type: tells Voyage whether these are docs or a query
    # No matter the length of text being embedded, we will have one vector of the same length

    # Two types of input_type : document or query. Voyage shapes the two differently internally.
    # Helps optimise the meaning of the generated embedding depending on how it is used
    result = voyage.embed(texts=texts, model= EMBED_MODEL, input_type=input_type)
    return cast(list[list[float]], result.embeddings), cast(int, result.total_tokens)
    # returns the vectors and token count (can see cost)

def count() -> int:
    return collection.count()

def build_index() -> int:
    """Embed every document and hand the vectors to chroma"""
    texts = [doc["body"] for doc in documents]
    vectors, tokens = embed_texts(texts, input_type = "document")
    collection.upsert(
        ids = [doc["id"] for doc in documents],
        embeddings = vectors,  # type: ignore
        documents = texts,
        metadatas = [{"title" : doc["title"], "type" : doc["type"] , "date" : doc["date"]} for doc in documents],
    )

    return tokens


# Chroma will give us back distance... lower is closer
def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and let Chroma do the storing"""
    query_vectors, _ = embed_texts([question], input_type="query")
    result = collection.query(query_embeddings = query_vectors, n_results = top_k) # type: ignore
    return [
        {
            "id" : doc_id,
            "title" : metadata["title"],
            "text" : text,
            # Chroma will give us back distance... lower is closer...
            # Do (1-disance) in order to flip from return distance to similarity
            "score" : 1 - distance
        }
        for doc_id, text, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],  # type: ignore
            result["metadatas"][0],  # type: ignore
            result["distances"][0],  # type: ignore
        )
    ]