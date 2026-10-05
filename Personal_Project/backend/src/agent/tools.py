from decimal import Decimal
from typing import Any, Callable, Optional

from agent.document_store import count, build_index, search
from data.records import borrowers, assessments, debt_repayments, covenant_tests, facilities, lending_policies, covenants, financial_periods

class DocumentSearchTool:
    
    def __init__(self, relevance_floor, top_k=3):
        self.relevance_floor = relevance_floor
        self.top_k = top_k
        
        
    def get_context(self, question: str) -> tuple[str,bool]:
        try:
            results = search(question, self.top_k)
            
        except RuntimeError as e:
            return f"Error: {e}", True
        
        if not results:
            return "No relevant documents found", False
        
        formatted = "\n\n".join(
            f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
            for r in results
        )
        # real success path - genuine results, formatted for the model to read.
        return formatted, False
        
    
    
class RecordSearchTool:
    
    def __init__(self, borrower_id : str):
        self.borrower_id = borrower_id
        self.records = {
            "borrowers" : borrowers,
            "facilities" : facilities,
            "covenants" : covenants,
            "lending_policies" : lending_policies,
            "debt_repayments" : debt_repayments,
            "financial_periods" : financial_periods,
            "covenant_tests" : covenant_tests,
            "assessments" : assessments,
        }
        
    def _get_records(self, entity_name : str, filter_condition: Optional[Callable[[dict],bool]]) -> list[dict]:
        records = [r for r in self.records[entity_name] if (r.get("borrower_id")==self.borrower_id)]
        if filter_condition is not None:
            records = [r for r in records if filter_condition(r)]
        return records

class CalculationError(ValueError):
    """Invalid input. Converted into {"ok": False, "error": ...} for the LLM."""
class CalculationTool:
    
    def net_debt(self, total_debt : float, cash : float):
        return Decimal(total_debt) - Decimal(cash)
    
    def maximum_covenant_headroom_percentage(self, threshold : float, actual : float) -> Decimal:
        if actual <= threshold:
            return Decimal(threshold) - Decimal(actual) / Decimal(threshold)
        raise CalculationError("Maximum Covenant Headroom: actual must be less than or equal to threshold")
    
    def minimum_covenant_headroom_percentage(self, threshold : float, actual : float) -> Decimal:
        if actual >= threshold:
            return Decimal(actual) - Decimal(threshold) / Decimal(threshold)
        raise CalculationError("Minimum Covenant Headroom: actual must be greater than or equal to threshold")
    
    def leverage_covenant_cushion(self, actual_leverage : float, threshold : float) -> Decimal:
        return 1 - (Decimal(actual_leverage)/Decimal(threshold))
    
    def interest_cover_covenant_cushion(self, actual_cover : float, threshold : float) -> Decimal:
        return 1 - (Decimal(threshold)/Decimal(actual_cover))
    
    def utilisation(self, drawn_amount : float, commited_amount : float):
        return Decimal(drawn_amount) / Decimal(commited_amount)
    
    def undrawn(self, drawn_amount : float, commited_amount : float):
        return Decimal(commited_amount) - Decimal(drawn_amount)
    
    def liquidity(self, cash : float, available_amounts : list[float]):
        return Decimal(cash) + sum([Decimal(amount) for amount in available_amounts])
    
    def arrears(self, principal_amount : float, amount_paid : float):
        return Decimal(principal_amount) - Decimal(amount_paid)
    
    def free_cash_flow(self, operating_cash_flow : float, capex : float):
        return Decimal(operating_cash_flow) - Decimal(capex)
    
    def cash_conversion(self, operating_cash_flow : float, ebitda : float):
        return Decimal(operating_cash_flow) / Decimal(ebitda)
    
    
    