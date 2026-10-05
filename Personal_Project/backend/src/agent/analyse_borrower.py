
from pydantic import BaseModel, Field
from agent.model import MODEL, SYSTEM_PROMPT, client
from agent.summarise_borrower import build_prompt
from utils import list_fields

class BorrowerAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model.... it is a contract"""
    tier : str = Field(description="One of: magic circle, national, boutique")
    strengths : list[str] = Field(max_length = 3, description = "Strengths associates with the firm")
    risks : list[str] = Field(max_length = 3, description = "Risks associated with the firm")
    headcount_efficiency : str = Field(description = "high, medium or low")
    
    
    rating : str = Field(description="The credit rating of the borrower.")
    sector : str = Field(description="The sector the borrower works in.")
    leverage : str = Field(description="The leverage of the borrower.")
    interest_cover : str = Field(description="The interest cover of the borrower")
    risk_of_default : str = Field(description="High, medium or low")
    points_to_note : list[str] = Field(max_length=4, description="Points of importance about the borrower that should be taken into account when making a credit rating.")
    
def analyse_borrower(borrower: dict) -> dict:
    """Structured output. The response is validated against BorrowerAnalysis or it fails."""
    response = client.messages.parse(
        model = MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user", "content": build_prompt(borrower)}],
        output_format = BorrowerAnalysis
    )

    analysis : dict = response.content[0].parsed_output  # type: ignore
    
    return {
        "id" : borrower["borrower_id"],
        "name" : borrower["name"],
        "analysis" : analysis,
        "input tokens" : response.usage.input_tokens,
        "output tokens" : response.usage.output_tokens,
        "stop reason" : response.stop_reason,
    }
    
    
class CreditAssessment(BaseModel):
    strengths : list[str] =  Field(max_length=3, description="List of strengths from the borrowers credit assessment. Each point is at most 2 sentences.")
    risks : list[str] = Field(max_length=3, description="List of risks from the borrowers credit assessment, that are holding their credit rating back. Each point is at most 2 sentences.")
    proposed_internal_rating : int = Field(gt=0 ,lt=23, description="The proposed internal rating of the borrower from 1 to 22.")
    rationale : str =  Field(description="A small 4 sentence maximum paragraph reasoning behind the proposed rating given.")
    
def build_credit_assessment_prompt(borrower : dict):
    prompt = "Give a credit assessment for the following borrower. Include details about their strengths, risks, a proposed internal rating from 1 (best) to 22 (worst) and a rationale behind the chosen rating."
    prompt += list_fields(borrower,["borrower_id","name","sector","latest_period_id"])
    return prompt
    
    
def credit_assessment(borrower : dict):
    """Structured output. The response is validated against BorrowerAnalysis or it fails."""
    response = client.messages.parse(
        model = MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user", "content": build_credit_assessment_prompt(borrower)}],
        output_format = CreditAssessment
    )

    analysis : dict = response.content[0].parsed_output  # type: ignore
    
    return {
        "id" : borrower["borrower_id"],
        "name" : borrower["name"],
        "analysis" : analysis,
        "input tokens" : response.usage.input_tokens,
        "output tokens" : response.usage.output_tokens,
        "stop reason" : response.stop_reason,
    }