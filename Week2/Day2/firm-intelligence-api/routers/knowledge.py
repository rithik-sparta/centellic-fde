
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# import knowledge
import knowledge_store as knowledge

# our relevance floor
# Below this we treat the retrieved context as not actually relevant
RELEVANCE_FLOOR = 0.35

router = APIRouter(prefix="/knowledge",tags=["knowledge"])

class Question(BaseModel):
    question : str = Field(min_length=3)
    top_k : int = Field(default=3, gt=0, le=8)

# POST does something, GET only retrieves. Here POST builds the index and sends real tokens with a cost.    
# POST because it acts
@router.post("/index")
def rebuild_index():
    """Embed the corpus. Costs tokens... so it is a deliberate POST, rather than automatic"""
    tokens = knowledge.build_index()
    return {"indexed" : knowledge.count(), "embedding_tokens" : tokens}

# POST because it needs to carry data in a response body. GET requests are not meant to take a request body by convention.
@router.post("/search")
def get_docs(question : Question):
    """Retrieval only... no model call or generated text etc... only what was found"""
    try:
        return {
            "question" : question.question, 
            "results" : knowledge.search(question.question, question.top_k)
        }
    except RuntimeError as e:
        raise HTTPException(status_code= 409, detail = str(e))