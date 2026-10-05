from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Iterable, Set, cast
from utils import list_fields, list_all_data
from pydantic import BaseModel, Field
import os
from anthropic.types import TextBlock
import anthropic
from data.records import financial_periods, covenant_tests, covenants, assessments, lending_policies, facilities, debt_repayments
from agent.model import MODEL, SYSTEM_PROMPT, client



class BorrowerAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model.... it is a contract"""
    proposed_internal_credit_rating : str = Field(gt = 0, lt=23, description = "A rating from 1 (best) to 22 (worst)")
    strengths : list[str] = Field(max_length = 3, description = "Strengths of the borrower")
    risks : list[str] = Field(max_length = 3, description = "Risks the borrower is facing.")
    mitignants : list[str] = Field(max_length = 3, description = "Factors that mitigate the risks")
    
def _get_financial_period(financial_period_id : str | None) -> dict | None:
    if financial_period_id is None:
        return None
    for fp in financial_periods:
        if fp["period_id"] == financial_period_id:
            return fp
    return None

def _get_financial_periods(financial_period_ids : Iterable[str]) -> list[dict]:
    return sorted([f for f in financial_periods if f["period_id"] in financial_period_ids], key = lambda x : datetime.strptime(x["period_end_date"], "%d-%m-%Y"), reverse=True)

# Get the covenant tests associated with a borrowers financial period. Return with the covenant id used for the test.
def _get_covenant_tests(financial_period_id : str | None) -> dict[str,list[dict[str, list[dict]]]]:
    if financial_period_id is None:
        return {}
    tests = defaultdict(list)
    for test in covenant_tests:
        if test["period_id"] == financial_period_id:
            tests[test["covenant_id"]].append(test)
    return tests

def _get_covenants(covenant_ids : Iterable[str]) -> dict[str,dict]:
    return {cov["covenant_id"] : cov for cov in covenants if cov["covenant_id"] in covenant_ids}
            
def _get_assessments(borrower_id : str) -> list[dict]:
    return sorted([asmnt for asmnt in assessments if asmnt["borrower_id"] == borrower_id], key = lambda x : datetime.strptime(x["assessed_at"], "%d-%m-%Y"), reverse=True)
    
def _get_lending_policies(policy_ids : Iterable[str]) -> list[dict]:
    return [pol for pol in lending_policies if pol["policy_id"] in policy_ids]
    
def _get_facilities(borrower_id : str) -> list[dict]:
    return [f for f in facilities if f["borrower_id"]==borrower_id]
    
def _get_debt_repayments(borrower_id : str) -> list[dict]:
    return sorted([dr for dr in debt_repayments if dr["borrower_id"] == borrower_id], key = lambda x : datetime.strptime(x["due_date"], "%d-%m-%Y"), reverse=True)
    
def build_prompt(borrower: dict) -> str:
    prompt = (
        f"Summarize this borrower in two short paragraphs. Do not use the ids in your answer, only the numbers to summarise the borrower.\n\n"
        f"Name : {borrower["name"]}"
        f"Sector : {borrower["sector"]}"
    )
    if borrower["latest_period_id"] is not None:
        prompt += f"Latest Financial Period id : {borrower["latest_period_id"]}"
        
    financial_period_fields = ["period_end_date", "period_type", "currency", "revenue", "cash", "total_debt", "net_interest_expense", "ebitda", "ebitda_basis", "net_income", "depreciation_amortisation", "total_assets", "ebitda_adjustments", "net_worth", "operating_cash_flow", "capex", "leverage, interest_cover", "dscr", "debt_basis", "includes_leases", "earning_period_basis", "ratio_source"]
    
    facility_results = _get_facilities(borrower["borrower_id"])
    
    list_all_data("Facility", "facility_id", facility_results, ["facility_type", "currency", "commited_amount", "drawn_amount", "available_amount", "balance_as_of_data", "start_date", "maturity_date", "margin_bps", "ranking", "security_description", "status"])
        
    assessment_results = _get_assessments(borrower["borrower_id"])
    financial_period_ids : Set[str] = set()
    for ar in assessment_results:
        financial_period_ids.update(ar["financial_period_ids"])
        
    financial_period_results = _get_financial_periods(financial_period_ids)
    prompt += list_all_data("Financial Period", "period_id", financial_period_results, financial_period_fields)
        
    policy_ids = {a["policy_id"] for a in assessment_results}
    
    lending_policy_results = _get_lending_policies(policy_ids)
    prompt += list_all_data("Lending Policy", "policy_id", lending_policy_results,["sector", "max_internal_rating_rank", "max_leverage", "min_interest_cover", "currency", "max_exposure_per_borrower", "max_sector_exposure", "require_security", "effective_date","end_date","status","notes"])
    
    
    debt_repayments = _get_debt_repayments(borrower["borrower_id"])
    prompt += list_all_data("Debt Repayments", "repayment_id", debt_repayments,["facility_id", "due_date", "principal_amount", "currency", "repayment_type", "status", "paid_date", "amount_paid", "interest_amount"])
    
    latest_finanical_results = _get_financial_period(borrower["latest_period_id"])
    
    if latest_finanical_results is not None :
        
    
        prompt += (
            f"Latest Financial Period Results: [{latest_finanical_results["period_id"]}]\n"
        )
        
        prompt += list_fields(latest_finanical_results, financial_period_fields)
                
        covenant_test_results = _get_covenant_tests(borrower["latest_period_id"])
        
        covenant_results : dict[str,dict] = _get_covenants(set(covenant_test_results.keys()))
        
        prompt += (
            "Covenants and Results:"
        )
        for k,v in covenant_test_results.items():
            covenant = covenant_results[k]
            prompt += list_all_data("Covenant","covenant_id",[covenant],["facility_id", "covenant_type", "description", "metric", "operator", "threshold", "test_frequency", "calculation_basis", "effective_from", "effective_to"])
            prompt += "\n"
            for test_result in v:
                prompt += list_all_data("Covenant Tests","test_id",v,["test_date","actual_value","result", "headroom", "notes"])
            prompt += "\n"
        
    return prompt

def build_credit_memo_prompt(borrower : dict):
    financial_period_fields = ["period_end_date", "period_type", "currency", "revenue", "cash", "total_debt", "net_interest_expense", "ebitda", "ebitda_basis", "net_income", "depreciation_amortisation", "total_assets", "ebitda_adjustments", "net_worth", "operating_cash_flow", "capex", "leverage, interest_cover", "dscr", "debt_basis", "includes_leases", "earning_period_basis", "ratio_source"]
    
    prompt = "Create a draft credit memo for this borrower. Go over the borrower name, sector, and latest financial period statistics.\n"
    prompt += list_fields(borrower,["borrower_id", "name", "sector", "rating_agency", "credit_rating", "as_of_date", "internal_rating_rank", "archived"])
    if borrower["latest_period_id"] is not None:
        fp : dict | None = _get_financial_period(borrower["latest_period_id"])
        if fp is not None:
            prompt += list_fields(fp, financial_period_fields)    
    
    return prompt
    


def summarise_borrower(borrower: dict) -> dict:
    # one LLM call that returns the text plus what it costs to get it.
    response = client.messages.create(
        model = MODEL,
        max_tokens = 400,
        system = SYSTEM_PROMPT,
        messages = [{"role":"user","content": build_prompt(borrower)}]
    )
    text_content = next(
        (block.text for block in response.content if isinstance(block, TextBlock)),
        ""
    )

    return {
        "borrower": borrower["borrower_id"],
        "name": borrower["name"],
        "sector" : borrower["sector"],
        "summary": text_content,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason
    }
    
    
def estimate_input_tokens(borrower: dict, prompt_builder : Callable[[dict],str]) -> int:
    """Count tokens BEFORE sending, Costs nothing, tells you what a call will cost"""

    counted = client.messages.count_tokens(
        model = MODEL,
        system = SYSTEM_PROMPT,
        messages=[{"role":"user","content": prompt_builder(borrower)}],

    )
    return counted.input_tokens


def stream_borrower_summary(borrower: dict):
    """Yields tect chunks as they arrive, rather than waiting for the whole response"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content": build_credit_memo_prompt(borrower)}]
    ) as stream:
        yield from stream.text_stream