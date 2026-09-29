from anthropic import APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from langsmith import APIStatusError

import agent
import knowledge_store as knowledge
import llm
from routers.knowledge import RELEVANCE_FLOOR, Question

router = APIRouter(prefix="/agent",tags=["agent"])

# Function behaviour
    # Refusal - Happens before the model is called not after
    # Why 200 and not a 404 for refusal???
    # the request was valid... service handles it correctly and "we have no relevant document is a real answer"
# sources...
    # this makes our answer checkable... without it a client has an answer/para that they have HAVE to trust... with it they can open doc-004 and verify the claim themselves
# same error mapping as before
    # 504, 429, 502 ... never a bare 500
@router.post("/context")
def ask(q : Question):
    """Retrieve, then answer using only what was retrieved... or refuse"""
    # 1. Retrieve
    # same call as /knowledge/search
    try:
        hits = knowledge.search(q.question, q.top_k)
        
    except RuntimeError as e:
        raise HTTPException(status_code= 409, detail = str(e))
    
    
    # 2. Filter, and decide whether to make a call to the model at all.
    # compare against our RELEVANCE_FLOOR
    usable = [hit for hit in hits if hit["score"] >= RELEVANCE_FLOOR]
    
    if not usable:
        return {
            "question" : q.question,
            "answer" : None,
            "refused" : True,
            "reason" : "No document in the corpus is relevant to that question.",
            "sources" : []
        }
    
    # 3. Generation, Build context and generate the answer
    context = "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}" for h in usable)
    print(len(context), repr(context[:100]))
    
    try:
        result = llm.answer_from_context(q.question,context=context)
    except APITimeoutError as e:
        print(e.message)
        raise HTTPException(status_code = 504, detail = "Answer provider timed out")
    except RateLimitError as e:
        print(e.message)
        raise HTTPException(status_code = 429, detail = "Answer provider rate limited")
    except APIStatusError as e:
        print(e.message)
        raise HTTPException(status_code = 502, detail = "Answer provider unavailable")
        
    # Structure format if the output will be given to another application
    # 4. Return the succesful answer
    # Natural language when the output will be given to a person.
    return {
            "question" : q.question,
            "answer" : result["answer"],
            "refused" : False,
            "reason" : None,
            "sources" : [{"id" : h["id"], 
                          "title" : h["title"], 
                          "score" : round(h["score"],3)} for h in usable],
            "input_tokens" : result["input_tokens"], 
            "output_tokens" : result["output_tokens"], 
            "stop_reason" : result["stop_reason"]
    }


@router.post("/ask")
def ask_with_tools(q: Question):
    try:
        result = agent.ask_with_tools(q.question)
    except RuntimeError as e:
        print(e)
        raise HTTPException(status_code = 401, detail = "Something went wrong.")
    except APITimeoutError as e:
        print(e.message)
        raise HTTPException(status_code = 504, detail = "Answer provider timed out")
    except RateLimitError as e:
        print(e.message)
        raise HTTPException(status_code = 429, detail = "Answer provider rate limited")
    except APIStatusError as e:
        print(e.message)
        raise HTTPException(status_code = 502, detail = "Answer provider unavailable")
    
    return result