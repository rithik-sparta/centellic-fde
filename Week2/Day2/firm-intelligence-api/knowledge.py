"""Embedding and retrieval mechanics... nothing in here will know about FastAPI"""
import math
import os
from typing import cast

# import numpy as np
import voyageai

from documents import DOCUMENTS

EMBED_MODEL = "voyage-3-lite"

voyage = voyageai.Client(  # type: ignore
    api_key = os.environ["VOYAGE_API_KEY"],
    max_retries = 3,
    timeout = 30,
)

def count() -> int:
    return len(INDEX)

# Vectors representing documents
INDEX: list[dict] = []


def embed_texts(texts: list[str], input_type: str) -> tuple[ list[list[float]], int]:
    # embed a batch
        # input_type: tells Voyage whether these are docs or a query
    # No matter the length of text being embedded, we will have one vector of the same length
    
    # Two types of input_type : document or query. Voyage shapes the two differently internally. 
    # Helps optimise the meaning of the generated embedding depending on how it is used
    result = voyage.embed(texts=texts, model= EMBED_MODEL, input_type=input_type)
    return cast(list[list[float]], result.embeddings), cast(int, result.total_tokens)
    # returns the vectors and token count (can see cost)

def cosine_similarity(a: list[float], b: list[float]):
    """How close together two vectors in space are, ignoring magnitude
        1.0 exact match
        0.0 unrelated
        -1.0 means opposite
    """
    # nA = np.array(a)
    # nB = np.array(b)
    # nA.dot(nB)/np.abs(nA)*np.abs(nB)
    
    dot = sum(x*y for x,y in zip(a,b))
    abs_a = math.sqrt(sum(x*x for x in a))
    abs_b = math.sqrt(sum(y*y for y in b))
    
    cosine_sim = dot / (abs_a*abs_b)
    return cosine_sim
    
def build_index() -> int:
    """Embed every document once and hold the vectors in memory"""
    INDEX.clear()
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors, tokens = embed_texts(texts, input_type = "document")
    for doc, vector in zip(DOCUMENTS, vectors):
        INDEX.append({
            "id" : doc["id"],
            "title" : doc["title"],
            "text" : doc["body"],
            "vector" : vector
        })
        
    return tokens
    
def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question... then score it against everything in the index"""
    if not INDEX:
        raise RuntimeError("Index is empty - call index first.")
    
    query_vectors, _ = embed_texts([question], input_type = "query")
    
    query_vector : list[float] = query_vectors[0]
    scored : list[dict] = [
        {
            "id" : entry["id"],
            "title" : entry["title"],
            "text" : entry["text"],
            "score" : cosine_similarity(query_vector, entry["vector"])
        } for entry in INDEX
    ]
    
    scored.sort(key = lambda item : item["score"], reverse=True)
    return scored[:top_k]



def print_scores(search_result : list[dict]):
    for p in search_result:
        print(p["id"])
        print(p["title"])
        print(p["text"])
        print(p["score"])
        print("\n")
        



