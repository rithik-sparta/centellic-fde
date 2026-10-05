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
        
    def _get_records(self, entity_name : str, filter_condition: Optional[Callable[[dict],bool]]):
        records = [r for r in self.records[entity_name] if (r.get("borrower_id")==self.borrower_id)]
        if filter_condition is not None:
            records = [r for r in records if filter_condition(r)]
        return records


# class CalculationTool:
    
    