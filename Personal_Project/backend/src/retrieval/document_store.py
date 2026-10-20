from typing import cast
import math

import voyageai
from retrieval import document_store, hybrid
from config import VOYAGE_API_KEY, VOYAGE_EMBED_MODEL
from chunking import chunk_index

CHUNK_STRATEGY = "whole_document"

SEARCH_MODE = "hybrid"

voyage = voyageai.Client(  # type: ignore
    api_key = VOYAGE_API_KEY,
    max_retries = 3,
    timeout = 30,
)


def embed_texts(texts: list[str], input_type: str) -> tuple[ list[list[float]], int]:
    # embed a batch
        # input_type: tells Voyage whether these are docs or a query
    # No matter the length of text being embedded, we will have one vector of the same length

    # Two types of input_type : document or query. Voyage shapes the two differently internally.
    # Helps optimise the meaning of the generated embedding depending on how it is used
    result = voyage.embed(texts=texts, model= VOYAGE_EMBED_MODEL, input_type=input_type)
    return cast(list[list[float]], result.embeddings), cast(int, result.total_tokens)
    # returns the vectors and token count (can see cost)

def count() -> int:
    # return collection.count()
    return chunk_index.collection_for(CHUNK_STRATEGY).count()

def build_index() -> int:
    """Embed every document and hand the vectors to chroma"""
    
    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]


# Chroma will give us back distance... lower is closer
def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and let Chroma do the storing"""
    if count() == 0:
        raise RuntimeError("Index is empty, call POST doc_store/index first")
    query_vectors, _ = document_store.embed_texts([question], input_type="query")
    
    if SEARCH_MODE=="hybrid":
        return hybrid.search_with_vectors(CHUNK_STRATEGY, question, query_vectors[0], top_k)
    
    return chunk_index.search_with_vectors(CHUNK_STRATEGY, query_vectors, k=top_k)[0]
    
def cosine_similarity(a: list[float], b: list[float]):
    """How close together two vectors in space are, ignoring magnitude
        1.0 exact match
        0.0 unrelated
        -1.0 means opposite
    """
    
    dot = sum(x*y for x,y in zip(a,b))
    abs_a = math.sqrt(sum(x*x for x in a))
    abs_b = math.sqrt(sum(y*y for y in b))
    
    cosine_sim = dot / (abs_a*abs_b)
    return cosine_sim