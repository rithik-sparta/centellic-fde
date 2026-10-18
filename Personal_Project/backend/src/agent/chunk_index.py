""" 
One Chroma collection per chunking strategy so that strategies can be compared side by side

Each collection remembers a "fingerprint" of the chunks and the embedding model that built it.
If wither changes, the collecttion is rebuilt from scratch.

Builds write and read
"""

# things to note from our switch to Chroma
# embed_texts is imported not rewritten... embedding provider hasn't changed only the storage has
#  configuration=.... -> not optional, we are choosing something different from Chromas default
# Chroma returns distane, we return similarity -> flip the meaning Chroma -> distance lower is better, 1-distance -> similarity cosine
# upsert instead of add -> add fails on an id that already exists, upsert overwrites


import hashlib

import chromadb

from agent import chunking
from agent import document_store
from data.documents import documents as DOCUMENTS

ALL_DOCUMENTS : list[dict] = DOCUMENTS
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
        batch_vectors, batch_tokens = document_store.embed_texts(texts[start:start+BATCH_SIZE], input_type=input_type)
        vectors.extend(batch_vectors)
        tokens += batch_tokens
    return vectors, tokens

# the fingerprint changes if the text, the embedding model or the order changes... and stays put if nothing does
def fingerprint(chunks: list[dict]) -> str:
    # SHA-256 - a hashing algorithm that returns a fixed length code (64 characters long)
    digest = hashlib.sha256(document_store.EMBED_MODEL.encode())
    # Feed in pieces same output as feeding all at once
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[:16]


def build(strategy: str, force: bool = False) -> dict:
    """Make sure the strategy's collection matches the current corpus, chunker and model."""
    """Answer's one q.... is the index I already have still correct? Yes then do nothing, no then throw index away and build a new one"""
    """Write side is run once, free if nothing changed."""
    """Flow: chunking.py<chunk_corpus> -> """
    """Read side: Run for every question. Question vector -> search_with_vectors -> chromadb -> chunks_strategy"""
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
    #. voyage call
    vectors, tokens = embed_batched([c["text"] for c in chunks], input_type="document")
    # Upsert never removes. If corpus shrinks old chunks will stay behind, we do not want this to happen.
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings = vectors, # type: ignore
        documents=[c["text"] for c in chunks],
        metadatas = [{"doc-id": c["doc_id"], "title" : c["title"], "fingerprint" : fp} for c in chunks],
        
    )
    
    return {"strategy" : strategy, "chunks" : len(chunks), "embedding_tokens" : tokens, "rebuilt" : True}


# CURRENT - 

# NEW FUNCTIONS ADDS - search_with_vectors
# the read side
# it takes question vectors that are already embedded, so questions are embedded once and reused across all 6 categories
# k - how many chunks to return per question

def search_with_vectors(strategy: str, query_vectors: list[list[float]], k: int) -> list[list[dict]]:
    """
    We embed the question once, then searches many strategies with the same vectors.
    """
    col = collection_for(strategy)
    if col.count()==0:
        raise RuntimeError(f"Index for '{strategy}' is empty, build it first")
    
    # the search
    result = col.query(query_embeddings=query_vectors, n_results=min(k, col.count())) # type: ignore
    """ 
    what result looks like
      - result["ids"] - a list of 2 lists, each holding 3 ids.
      - result["documents"] - a list of 2 lists, each holding 3 texts.
      - result["metadatas"] - a list of 2 lists, each holding 3 metadata dictionaries.
      - result["distances"] - a list of 2 lists, each holding 3 distances.
      e.g. ids ['doc001#00', 'doc101#00'. 'doc007#00']
      e.g. distances [0.375, 0.389, 0.30]
    Takes vectors not questions
    """
    return [
        # Chroma returns 4 parallel nested lists
       [{"id": meta["doc-id"], "chunk_id": chunk_id, "title": meta["title"], "text": text, "score" : 1 - distance} for chunk_id, text, meta, distance in zip(ids, docs, metas, dists) ]
       for ids, docs, metas, dists in zip(result["ids"], result["documents"], result["metadatas"], result["distances"]) # type: ignore
    ]


"""
a chunk that only keyword search found has no cosine score... our relevance gate needs one
"""

def cosine_for(strategy: str, query_vector: list[float], chunk_ids: list[str]) -> dict[str, float]:
    if not chunk_ids:
        return {}
    
    stored = collection_for(strategy).get(ids=chunk_ids, include=["embeddings"])
    return {
        chunk_id: float(document_store.cosine_similarity(query_vector, list(vector)))
        for chunk_id, vector in zip(stored["ids"], stored["embeddings"])
    }
    