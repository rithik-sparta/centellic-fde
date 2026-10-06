from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Optional
import functools
import inspect

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

def _d(value: Any, name: str = "value") -> Decimal:
    """Convert a number to Decimal via str, so 0.1 stays 0.1. Rejects bool, text and NaN."""
    if isinstance(value, bool) or value is None:
        raise CalculationError(f"'{name}' must be a number, got {value!r}")
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise CalculationError(f"'{name}' must be a number, got {value!r}")
    if not result.is_finite():
        raise CalculationError(f"'{name}' must be a finite number, got {value!r}")
    return result
 
 
def _divide(numerator: Any, denominator: Any, name: str) -> Decimal:
    """Divide, raising a CalculationError instead of ZeroDivisionError."""
    denom = _d(denominator, name)
    if denom == 0:
        raise CalculationError(f"{name} must not be zero")
    return _d(numerator, "numerator") / denom
 
 
def _jsonable(value: Any) -> Any:
    """Decimal is not JSON serialisable, so return floats rounded to 4 decimal places."""
    if isinstance(value, Decimal):
        return round(float(value), 4)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value
 
 
_REGISTRY: set[str] = set()
 
 
def llm_tool(func: Callable) -> Callable:
    """Mark a method as callable by the LLM and wrap its result as {"ok": ..., "value"/"error": ...}."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return {"ok": True, "value": _jsonable(func(*args, **kwargs))}
        except CalculationError as e:
            return {"ok": False, "error": str(e)}
        except (TypeError, ValueError, InvalidOperation) as e:
            return {"ok": False, "error": f"Invalid input: {e}"}
    _REGISTRY.add(func.__name__)
    return wrapper
 
 
class CalculationTool:
    """Deterministic credit calculations for an LLM to call.
 
    Conventions:
      * Ratios, margins and headroom are fractions (0.12 = 12%).
      * Headroom and cushion are positive when the covenant is met and
        NEGATIVE when it is breached (never an error).
      * Amounts must all be in the same currency and period basis.
    """
 
    # ---- Debt and liquidity -------------------------------------------------
 
    @llm_tool
    def net_debt(self, total_debt: float, cash: float):
        """Net debt: total debt less cash."""
        return _d(total_debt, "total_debt") - _d(cash, "cash")
 
    @llm_tool
    def utilisation(self, drawn_amount: float, committed_amount: float):
        """Share of a facility that is drawn: drawn / committed."""
        return _divide(drawn_amount, committed_amount, "committed_amount")
 
    @llm_tool
    def undrawn(self, drawn_amount: float, committed_amount: float):
        """Undrawn amount of a facility: committed less drawn."""
        return _d(committed_amount, "committed_amount") - _d(drawn_amount, "drawn_amount")
 
    @llm_tool
    def liquidity(self, cash: float, available_amounts: list[float]):
        """Liquidity: cash plus the available (undrawn and accessible) amounts."""
        if not isinstance(available_amounts, (list, tuple)):
            raise CalculationError("'available_amounts' must be a list of numbers")
        return _d(cash, "cash") + sum((_d(a, "available_amounts item") for a in available_amounts), Decimal(0))
 
    @llm_tool
    def arrears(self, principal_amount: float, amount_paid: float):
        """Unpaid part of a scheduled repayment: due less paid (negative means overpaid)."""
        return _d(principal_amount, "principal_amount") - _d(amount_paid, "amount_paid")
 
    # ---- Covenant headroom --------------------------------------------------
 
    @llm_tool
    def maximum_covenant_headroom_percentage(self, actual: float, threshold: float):
        """Headroom against a MAXIMUM covenant (for example leverage must be at most 4.5x):
        (threshold - actual) / threshold. Positive = within limit, negative = breached."""
        return _divide(_d(threshold, "threshold") - _d(actual, "actual"), threshold, "threshold")
 
    @llm_tool
    def minimum_covenant_headroom_percentage(self, actual: float, threshold: float):
        """Headroom against a MINIMUM covenant (for example interest cover must be at least 2.5x):
        (actual - threshold) / threshold. Positive = within limit, negative = breached."""
        return _divide(_d(actual, "actual") - _d(threshold, "threshold"), threshold, "threshold")
 
    @llm_tool
    def leverage_covenant_cushion(self, actual: float, threshold: float):
        """EBITDA cushion on a leverage covenant: 1 - actual/threshold. The fraction EBITDA can
        fall before breach. Negative = already breached."""
        return 1 - _divide(actual, threshold, "threshold")
 
    @llm_tool
    def interest_cover_covenant_cushion(self, actual: float, threshold: float):
        """EBITDA cushion on an interest cover covenant: 1 - threshold/actual. The fraction EBITDA
        can fall before breach. Negative = already breached."""
        return 1 - _divide(threshold, actual, "actual")
 
    # ---- Cash flow ----------------------------------------------------------
 
    @llm_tool
    def free_cash_flow(self, operating_cash_flow: float, capex: float):
        """Free cash flow: operating cash flow less capex."""
        return _d(operating_cash_flow, "operating_cash_flow") - _d(capex, "capex")
 
    @llm_tool
    def cash_conversion(self, operating_cash_flow: float, ebitda: float):
        """Cash conversion: operating cash flow / EBITDA. Needs positive EBITDA."""
        if _d(ebitda, "ebitda") <= 0:
            raise CalculationError("Cash conversion is not meaningful when EBITDA is zero or negative")
        return _divide(operating_cash_flow, ebitda, "ebitda")
 
    # ---- Profitability (fractions: 0.12 = 12%) ------------------------------
    # Revenue, EBITDA, net income and D&A must be on the same period basis.
 
    @llm_tool
    def ebit(self, ebitda: float, depreciation_amortisation: float):
        """Operating profit: EBITDA less depreciation and amortisation."""
        return _d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation")
 
    @llm_tool
    def ebitda_margin(self, ebitda: float, revenue: float):
        """EBITDA / revenue."""
        return _divide(ebitda, revenue, "revenue")
 
    @llm_tool
    def ebit_margin(self, ebitda: float, depreciation_amortisation: float, revenue: float):
        """(EBITDA - D&A) / revenue."""
        return _divide(_d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation"), revenue, "revenue")
 
    @llm_tool
    def net_margin(self, net_income: float, revenue: float):
        """Net income / revenue."""
        return _divide(net_income, revenue, "revenue")
 
    @llm_tool
    def free_cash_flow_margin(self, operating_cash_flow: float, capex: float, revenue: float):
        """(Operating cash flow - capex) / revenue."""
        return _divide(_d(operating_cash_flow, "operating_cash_flow") - _d(capex, "capex"), revenue, "revenue")
 
    @llm_tool
    def return_on_assets(self, net_income: float, total_assets: float):
        """Net income / total assets."""
        return _divide(net_income, total_assets, "total_assets")
 
    @llm_tool
    def return_on_equity(self, net_income: float, net_worth: float):
        """Net income / net worth. Not meaningful when net worth is zero or negative."""
        if _d(net_worth, "net_worth") <= 0:
            raise CalculationError("Return on equity is not meaningful when net_worth is zero or negative")
        return _divide(net_income, net_worth, "net_worth")
 
    @llm_tool
    def equity_ratio(self, net_worth: float, total_assets: float):
        """Share of assets funded by equity: net worth / total assets."""
        return _divide(net_worth, total_assets, "total_assets")
 
    @llm_tool
    def debt_to_assets(self, total_debt: float, total_assets: float):
        """Total debt / total assets."""
        return _divide(total_debt, total_assets, "total_assets")
 
    @llm_tool
    def ebit_interest_cover(self, ebitda: float, depreciation_amortisation: float, net_interest_expense: float):
        """(EBITDA - D&A) / net interest expense. Stricter than EBITDA interest cover."""
        return _divide(_d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation"), net_interest_expense, "net_interest_expense")
 
    # ---- LLM plumbing -------------------------------------------------------
 
    @classmethod
    def _tools(cls) -> dict[str, Callable]:
        return {n: f for n, f in inspect.getmembers(cls, inspect.isfunction) if n in _REGISTRY}
 
    @classmethod
    def tool_definitions(cls) -> list[dict]:
        """Tool definitions in the Anthropic Messages API format, built from type hints and docstrings."""
        def schema(tp) -> dict:
            if tp is float or tp is int:
                return {"type": "number"}
            if getattr(tp, "__origin__", None) is list:
                return {"type": "array", "items": schema(tp.__args__[0])}
            return {"type": "string"}
 
        out = []
        for name, f in cls._tools().items():
            sig = inspect.signature(f)
            props = {p: schema(prm.annotation) for p, prm in sig.parameters.items() if p != "self"}
            out.append({
                "name": name,
                "description": inspect.getdoc(f) or name,
                "input_schema": {"type": "object", "properties": props, "required": list(props)},
            })
        return out
 
    def run(self, name: str, arguments: dict) -> dict:
        """Dispatch a tool call from the LLM. Always returns a JSON-serialisable dict."""
        tools = self._tools()
        if name not in tools:
            return {"ok": False, "error": f"Unknown tool '{name}'. Available: {sorted(tools)}"}
        return getattr(self, name)(**(arguments or {}))
 