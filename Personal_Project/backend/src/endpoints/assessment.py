from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from utils import _create_new_id

from data.records import assessments

_seen_keys : dict[str,dict] = {}
router = APIRouter(prefix = "/assessments", tags=["assessments"])
class NewAssessment(BaseModel):
    borrower_id : str = Field(min_length=4)
    policy_id : str = Field(min_length=4)
    primary_period_id : str = Field(min_length=5)
    financial_period_ids : list[Annotated[str,Field(min_length=5)]]
    facility_id : str | None = Field(min_length=5)
    assessed_at : str = Field(min_length=25)
    assessed_by : str = Field(min_length=1)
    policy_breaches : list[Annotated[str,Field(min_length=5)]] = Field(default_factory=list)
    key_strengths : list[Annotated[str,Field(min_length=5)]] = Field(default_factory=list)
    key_risks : list[Annotated[str,Field(min_length=5)]] = Field(default_factory=list)
    mitignants : list[Annotated[str,Field(min_length=5)]] = Field(default_factory=list)
    proposed_internal_rating_rank : int = Field(ge=1, lt=23)
    recommendation : str = Field(min_length=1)
    rationale : str = Field(min_length=1)
    review_status : str = Field(min_length=5)
    

class UpdateAssessment(BaseModel):
    policy_id : str | None= Field(None, min_length=4)
    primary_period_id : str | None = Field(None, min_length=5)
    financial_period_ids : list[Annotated[str,Field(min_length=5)]] | None = Field(None)
    facility_id : str | None = Field(None, min_length=5)
    assessed_at : str | None = Field(None, min_length=25)
    assessed_by : str | None = Field(None, min_length=1)
    policy_breaches : list[Annotated[str,Field(min_length=5)]] | None = Field(None)
    key_strengths : list[Annotated[str,Field(min_length=5)]] | None = Field(None)
    key_risks : list[Annotated[str,Field(min_length=5)]] | None = Field(None)
    mitignants : list[Annotated[str,Field(min_length=5)]] | None = Field(None)
    proposed_internal_rating_rank : int | None = Field(None, ge=1, lt=23)
    recommendation : str | None = Field(None, min_length=1)
    rationale : str | None = Field(None, min_length=1)
    review_status : str | None = Field(None, min_length=5)
    
def get_assessment_or_404(assessment_id: str) -> dict:
    for assessment in assessments:
        if (assessment["assessment_id"] == assessment_id):
            return assessment
    raise HTTPException(404, f"No assessment with id {assessment_id}.")
    

@router.get("")
def get_assessments(borrower_id : str | None, assessed_after : str | None, assessed_before : str | None):
    answer = assessments
    # Filter assessments by borrower
    if borrower_id is not None:
        answer = [asmnt for asmnt in answer if asmnt["borrower_id"] == borrower_id]
        
    # Filter assessments assessed after a given date
    if assessed_after is not None:
        after = datetime.strptime(assessed_after, "%d-%m-%Y")
        answer = [asmnt for asmnt in answer if datetime.strptime(asmnt["assessed_at"], "%d-%m-%Y") > after]
    
    # Filter assessments assessed before a given date
    if assessed_before is not None:
        before = datetime.strptime(assessed_before, "%d-%m-%Y")
        answer = [asmnt for asmnt in answer if datetime.strptime(asmnt["assessed_at"], "%d-%m-%Y") < before]
    
    # Sort assessments from latest to earliest
    sorted_answers = sorted(answer, key = lambda x: x["assessed_at"], reverse=True)
    return sorted_answers
    
@router.get("/{assessment_id}")
def get_assessment(assessment : dict = Depends(get_assessment_or_404)):
    return assessment
    
@router.post("", status_code = 201)
def add_assessment(new : NewAssessment, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]
    
    new_id = _create_new_id(assessments,"assessment_id","a")

    assessment = {
        "assessment_id": new_id,
        "borrower_id" : new.borrower_id,
        "policy_id" : new.policy_id,
        "primary_period_id" : new.primary_period_id,
        "financial_period_ids" : new.financial_period_ids,
        "facility_id" : new.facility_id,
        "assessed_at" : new.assessed_at,
        "assessed_by" : new.assessed_by,
        "policy_breaches" : new.policy_breaches,
        "key_strengths" : new.key_strengths,
        "key_risks" : new.key_risks,
        "mitignants" : new.mitignants,
        "proposed_internal_rating_rank" : new.proposed_internal_rating_rank,
        "recommendation" : new.recommendation,
        "rationale" : new.rationale,
        "review_status" : new.review_status,
    }

    assessments.append(assessment)

    if idempotency_key is not None:
        _seen_keys[idempotency_key] = assessment

    return assessment

@router.put("/{assessment_id}")
def update_borrower(assessment : dict = Depends(get_assessment_or_404), to_update: UpdateAssessment | None = None):
    if to_update is None:
        return assessment
        #raise HTTPException(400, "No request body found.")
    updates = to_update.model_dump(exclude_none=True)
    assessment.update(updates)
    return assessment

@router.delete("/{assessment_id}",status_code=204)
def delete_assessment(assessment : dict = Depends(get_assessment_or_404)):
    assessments.remove(assessment)