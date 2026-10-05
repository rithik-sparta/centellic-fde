from typing import Annotated

from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from utils import _create_new_id
from agent import summarise_borrower as sb
from agent import analyse_borrower as ab

from data.records import borrowers

router = APIRouter(prefix = "/borrowers", tags=["borrowers"])
_seen_keys : dict[str,dict] = {}

class NewBorrower(BaseModel):
    name : str = Field(min_length=1)
    sector : str = Field(min_length=1)
    rating_agency : str | None = Field(None, min_length=1)
    credit_rating : str | None = Field(None, min_length=1)
    as_of_date : str | None = Field(min_length=1)
    internal_rating_rank : int | None = Field(None,ge=1,lt=23)
    latest_period_id : str | None = Field(None, min_length=4)
    archived : bool = Field(default=False)

class UpdateBorrower(BaseModel):
    name : str | None = Field(None, min_length=1)
    sector : str | None = Field(None, min_length=1)
    rating_agency : str | None = Field(None, min_length=1)
    credit_rating : str | None = Field(None, min_length=1)
    as_of_date : str | None = Field(min_length=1)
    internal_rating_rank : int | None = Field(None, ge=1, lt=23)
    latest_period_id : str | None = Field(None, min_length=4)
    archived : bool | None = Field(None)
    
def get_borrower_or_404(borrower_id: str) -> dict:
    for borrower in borrowers:
        if (borrower["borrower_id"] == borrower_id) and (not borrower["archived"]):
            return borrower
    raise HTTPException(404, f"No borrower with id {borrower_id}.")


@router.get("")
def get_borrowers(sector : str | None = None, internal_rating_rank_lte : int | None = None, get_unranked : bool | None = None):
    answer = borrowers
    # Filter by sector case insensitive search
    if sector is not None:
        answer = [b for b in answer if b["sector"] == sector.lower()]
        
    # Filter by unranked borrowers
    if get_unranked is not None:
        def is_unranked(b):
            return b["rating_agency"] is None and b["credit_rating"] is None and b["internal_rating_rank"] is None and b["as_of_date"] is None
        answer = [b for b in answer if is_unranked(b)]

    # Filter borrowers that are below or equal to a given threshold. Lower is better
    if internal_rating_rank_lte is not None:
        if internal_rating_rank_lte >= 1 and internal_rating_rank_lte <= 22:
            answer = [b for b in answer if b["internal_rating_rank"] is not None and b["internal_rating_rank"] >= internal_rating_rank_lte]
        else:
            raise HTTPException(404, f"Internal rating rank must be between 1 and 22 inclusive. Your value is {internal_rating_rank_lte}")
    return answer

@router.get("/{borrower_id}")
def get_borrower(borrower : dict = Depends(get_borrower_or_404)):  # noqa: B008
    return borrower

@router.post("", status_code = 201)
def add_borrower(new : NewBorrower, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]
    
    new_id : str = _create_new_id(borrowers,"borrower_id","b")
    borrower = {
        "borrower_id": new_id,
        "name": new.name,
        "sector": new.sector,
        "rating_agency": new.rating_agency,
        "credit_rating": new.credit_rating,
        "as_of_date": new.as_of_date,
        "internal_rating_rank": new.internal_rating_rank,
        "latest_period_id": new.latest_period_id,
        "deleted": new.archived,
    }
    
    borrowers.append(borrower)
    
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = borrower
    
    return borrower

@router.put("/{borrower_id}")
def update_borrower(borrower : dict = Depends(get_borrower_or_404), to_update: UpdateBorrower | None = None):
    if to_update is None:
        return borrower
        #raise HTTPException(400, "No request body found.")
    updates = to_update.model_dump(exclude_none=True)
    borrower.update(updates)
    return borrower

# We want to track borrowers we previously had, to ensure record history is consistent. We just no longer report on it.
@router.delete("/{borrower_id}", status_code = 204)
def delete_borrower(borrower : dict = Depends(get_borrower_or_404)):
    borrower["archived"] = True


@router.post("/{borrower_id}/summary")
def summarise(borrower: dict = Depends(get_borrower_or_404)):
    try:
        return sb.summarise_borrower(borrower)
    except APITimeoutError as e:
        print(e.message)
        raise HTTPException(status_code = 504, detail = "Summary provider timed out")
    except RateLimitError as e:
        print(e.message)
        raise HTTPException(status_code = 429, detail = "Summary provider rate limited")
    except APIStatusError as e:
        print(e.message)
        raise HTTPException(status_code = 502, detail = "Summary provider unavailable")
    
@router.post("/{borrower_id}/stream_summary")
def stream_summarise(borrower: Annotated[dict, Depends(get_borrower_or_404)]):
    return StreamingResponse(
        sb.stream_borrower_summary(borrower),
        media_type="text/plain",
    )

@router.post("/{borrower_id}/estimate_summary_prompt")
def estimate_summary_prompt(borrower : dict = Depends(get_borrower_or_404)):
    return sb.estimate_input_tokens(borrower, sb.build_prompt)

@router.post("/{borrower_id}/estimate_credit_memo_prompt")
def estimate_credit_memo_prompt(borrower : dict = Depends(get_borrower_or_404)):
    return sb.estimate_input_tokens(borrower, sb.build_credit_memo_prompt)

@router.post("/{borrower_id}/credit_assessment")
def credit_assessment(borrower : dict = Depends(get_borrower_or_404)):
    try:
        return ab.credit_assessment(borrower)
    except APITimeoutError as e:
        print(e.message)
        raise HTTPException(status_code = 504, detail = "Analysis provider timed out")
    except RateLimitError as e:
        print(e.message)
        raise HTTPException(status_code = 429, detail = "Analysis provider rate limited")
    except APIStatusError as e:
        print(e.message)
        raise HTTPException(status_code = 502, detail = "Analysis provider unavailable")
    