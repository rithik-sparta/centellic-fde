# embed texts... is imported rather than rewritten
# the embedding provider has not changes ... only where the vectors get stored

import chromadb

from documents import DOCUMENTS
from knowledge import embed_texts

# writes to disk at the path we give it
chroma = chromadb.PersistentClient(
    path="./chroma_store",
)

collection = chroma.get_or_create_collection(
    name="firm-documents",
    configuration={
        # HNSW (Hierarchical Navigable Small World) is a graph based index used in vector databases to perform fast an appropriate kNN search.
        "hnsw": {
            "space" : "cosine"
        }
    }
)

def count() -> int:
    return collection.count()

def build_index() -> int:
    """Embed every document and hand the vectors to chroma"""
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors, tokens = embed_texts(texts, input_type = "document")
    collection.upsert(
        ids = [doc["id"] for doc in DOCUMENTS],
        embeddings = vectors,  # type: ignore
        documents = texts,
        metadatas = [{"title" : doc["title"], "type" : doc["type"] } for doc in DOCUMENTS],
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
    
# things to note from our switch to Chroma
# embed_texts is imported not rewritten... embedding provider hasn't changed only the storage has
#  configuration=.... -> not optional, we are choosing something different from Chromas default
# Chroma returns distane, we return similarity -> flip the meaning Chroma -> distance lower is better, 1-distance -> similarity cosine
# upsert instead of add -> add fails on an id that already exists, upsert overwrites




