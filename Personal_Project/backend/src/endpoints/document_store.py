
from fastapi import APIRouter
from agent import document_store as ds


router = APIRouter(prefix = "/borrowers", tags=["borrowers"])

@router.post("/index")
def rebuild_index():
    """Embed the corpus. Costs tokens... so it is a deliberate POST, rather than automatic"""
    tokens = ds.build_index()
    return {"indexed" : ds.count(), "embedding_tokens" : tokens}