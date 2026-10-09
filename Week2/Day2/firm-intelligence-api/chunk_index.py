""" 
One Chroma collection per chunking strategy so that strategies can be compared side by side

Each collection remembers a "fingerprint" of the chunks and the embedding model that built it.
If wither changes, the collecttion is rebuilt from scratch.
"""


import hashlib

import chromadb

import chunking
import knowledge
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

ALL_DOCUMENTS : list[dict] = DOCUMENTS + CORPUS_DOCUMENTS
BATCH_SIZE = 128 # Voyages's own guidance: batch documetns to stay well inside rate limits.

chroma = chromadb.PersistentClient(path="./chroma_store")

def collection_name(strategy: str) -> str:
    return f"chunks_{strategy}"

def collection_for(strategy: str):
    return chroma.get_or_create_collection(
        name = collection_name(strategy),
        configuration = {"hnsw" : {"space" : "cosine"}}
    )

def embed_batched(texts: list, input_type: str) -> tuple[list[list[float]],int]:
    "Embed any number of texts in batched. Return all vectors and the total token count."
    vectors : list[list[float]] = []
    tokens = 0
    
    for start in range(0, len(texts), BATCH_SIZE):
        # We send in batches to balance between reaching a single requests limit, vs being conservative sending one text at a time.
        # Vectors come back at same order as the text
        batch_vectors, batch_tokens = knowledge.embed_texts(texts[start:start+BATCH_SIZE], input_type=input_type)
        vectors.extend(batch_vectors)
        tokens += batch_tokens
    return vectors, tokens

# the fingerprint changes if the text, the model or the order changes... and stays put if nothing does
def fingerprint(chunks: list[dict]) -> str:
    # SHA-256 - a hashing algorithm that returns a fixed length code (64 characters long)
    digest = hashlib.sha256(knowledge.EMBED_MODEL.encode())
    # Feed in pieces same output as feeding all at once
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[:16]


def build(strategy: str, force: bool = False) -> dict:
    """Make sure the strategy's collection matches the current corpus, chunker and model."""
    """Answer's one q.... is the index I already have still correct? Yes then do nothing, no then throw index away and build a new one"""
    # Part 1
    chunks = chunking.chunk_corpus(ALL_DOCUMENTS, strategy)
    fp = fingerprint(chunks)
    col = collection_for(strategy)
    stored = col.get(limit=1, include=["metadatas"])["metadatas"]
    # Did not force a rebuild, Does stored chunk count match size, does fingerprint match
    if not force and col.count() == len(chunks) and stored and stored[0].get("fingerprint") == fp:
        return {"strategy" : strategy, "chunks": len(chunks), "embedding_tokens": 0, "rebuilt": False}
    
    # Part 2 - The rebuild
    try:
        chroma.delete_collection(collection_name(strategy))
    except Exception:
        # First time we run this call, there will be nothing to delete
        pass
    
    col = collection_for(strategy)
    vectors, tokens = embed_batched([c["text"] for c in chunks], input_type="document")
    # Upsert never removes. If corpus shrinks old chunks will stay behind, we do not want this to happen.
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings = vectors, # type: ignore
        documents=[c["text"] for c in chunks],
        metadatas = [{"doc-id": c["doc-id"], "title" : c["title"], "fingerprint" : fp} for c in chunks],
        
    )
    
    return {"strategy" : strategy, "chunks" : len(chunks), "embedding_tokens" : tokens, "rebuilt" : True}




    