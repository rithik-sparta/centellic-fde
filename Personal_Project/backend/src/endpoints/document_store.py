
from fastapi import APIRouter, HTTPException
from agent import document_store as ds
from pydantic import BaseModel, Field

router = APIRouter(prefix = "/doc_store", tags=["doc_store"])

class Question(BaseModel):
    question : str = Field(min_length=3)
    top_k : int = Field(default=3,gt=0,le=8)

@router.post("/index")
def rebuild_index():
    """Embed the corpus. Costs tokens... so it is a deliberate POST, rather than automatic"""
    tokens = ds.build_index()
    return {"indexed" : ds.count(), "embedding_tokens" : tokens}

@router.post("/search")
def search(question : Question):
    
    try:
        print(question.top_k)
        return {
            "question" : question.question,
            "results" : ds.search(question.question, question.top_k)
        }
    except RuntimeError as e:
        raise HTTPException(status_code= 409, detail = str(e))