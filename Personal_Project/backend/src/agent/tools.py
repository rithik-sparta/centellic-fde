import functools
import inspect
import json
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar

from data.records import (
    assessments,
    borrowers,
    covenant_tests,
    covenants,
    debt_repayments,
    facilities,
    financial_periods,
    lending_policies,
)

from agent.document_store import search


class DocumentSearchTool:
    
    @classmethod
    def schema(cls) -> dict:
        schema = {
            "name": "search_document_store",
            "description": (
                "Search the credit analysis document store for documents relevant "
                "to a question about borrowers, outlooks, credit-memos and sector outlooks."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    },
                "required": ["query"],
                },
            }
        
        return schema
        
    @classmethod
    def get_context(cls, question: str, top_k: int = 3) -> tuple[str,bool]:
        try:
            results = search(question, top_k)
            
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
    records : ClassVar[dict[str,list[dict[str,Any]]]] = {
                "borrowers" : borrowers,
                "facilities" : facilities,
                "covenants" : covenants,
                "lending_policies" : lending_policies,
                "debt_repayments" : debt_repayments,
                "financial_periods" : financial_periods,
                "covenant_tests" : covenant_tests,
                "assessments" : assessments,
            }
    
    @classmethod
    def schema(cls) -> dict:
        schema = {
            "name": "search_records",
            "description": (
                "Search the records for entities that meet a provided filter condition."
                "If the entity contains fields with borrower_id, it must provide the borrower_id of records it wishes to search for."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": f"The name of the entity to search across. One of {"".join(cls.records.keys())}"},
                    "borrower_id": {"type": "string", "description": "The borrower_id of the records you wish to search across. If the entity contains a borrower_id field, this field must be included."},
                    "filter_condition": {"type": "function", "description": "The filter condition to filter records. If a function is provided it must take a python dict and return a boolean value. Otherwise all valid records are returned."}
                    },
                "required": ["entity_name"],
                },
            }
        
        return schema
    
        
    @classmethod
    def get_records(cls, entity_name : str, borrower_id : str | None, filter_condition: Callable[[dict],bool] | None = lambda x : True) -> tuple[str,bool]:
        """Get records of a particular entity, filtering by the borrower_id if applicable."""
        if "borrower_id" in cls.records[entity_name] and borrower_id is None:
            return "Please provide a borrower_id to filter against.", False
        records = [r for r in cls.records[entity_name] if (("borrower_id" not in r) or (r.get("borrower_id")==borrower_id))]
        if filter_condition is not None:
            records = [r for r in records if filter_condition(r)]
        formatted = f"{entity_name.capitalize()}\n"
        formatted += "\n\n".join([
            "\n".join([f"{field} : {value}" for field, value in r.items()]) for r in records]
                              )
        return formatted, True


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
 
 # Set of function names
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
 
    @classmethod
    @llm_tool
    def net_debt(cls, total_debt: float, cash: float):
        """Net debt: total debt less cash."""
        return _d(total_debt, "total_debt") - _d(cash, "cash")
 
    @classmethod
    @llm_tool
    def utilisation(cls, drawn_amount: float, committed_amount: float):
        """Share of a facility that is drawn: drawn / committed."""
        return _divide(drawn_amount, committed_amount, "committed_amount")
 
    @classmethod
    @llm_tool
    def undrawn(cls, drawn_amount: float, committed_amount: float):
        """Undrawn amount of a facility: committed less drawn."""
        return _d(committed_amount, "committed_amount") - _d(drawn_amount, "drawn_amount")
 
    @classmethod
    @llm_tool
    def liquidity(cls, cash: float, available_amounts: list[float]):
        """Liquidity: cash plus the available (undrawn and accessible) amounts."""
        if not isinstance(available_amounts, (list, tuple)):
            raise CalculationError("'available_amounts' must be a list of numbers")
        return _d(cash, "cash") + sum((_d(a, "available_amounts item") for a in available_amounts), Decimal(0))
 
    @classmethod
    @llm_tool
    def arrears(cls, principal_amount: float, amount_paid: float):
        """Unpaid part of a scheduled repayment: due less paid (negative means overpaid)."""
        return _d(principal_amount, "principal_amount") - _d(amount_paid, "amount_paid")
 
    # ---- Covenant headroom --------------------------------------------------
 
    @classmethod
    @llm_tool
    def maximum_covenant_headroom_percentage(cls, actual: float, threshold: float):
        """Headroom against a MAXIMUM covenant (for example leverage must be at most 4.5x):
        (threshold - actual) / threshold. Positive = within limit, negative = breached."""
        return _divide(_d(threshold, "threshold") - _d(actual, "actual"), threshold, "threshold")
 
    @classmethod
    @llm_tool
    def minimum_covenant_headroom_percentage(cls, actual: float, threshold: float):
        """Headroom against a MINIMUM covenant (for example interest cover must be at least 2.5x):
        (actual - threshold) / threshold. Positive = within limit, negative = breached."""
        return _divide(_d(actual, "actual") - _d(threshold, "threshold"), threshold, "threshold")
 
    @classmethod
    @llm_tool
    def leverage_covenant_cushion(cls, actual: float, threshold: float):
        """EBITDA cushion on a leverage covenant: 1 - actual/threshold. The fraction EBITDA can
        fall before breach. Negative = already breached."""
        return 1 - _divide(actual, threshold, "threshold")
 
    @classmethod
    @llm_tool
    def interest_cover_covenant_cushion(cls, actual: float, threshold: float):
        """EBITDA cushion on an interest cover covenant: 1 - threshold/actual. The fraction EBITDA
        can fall before breach. Negative = already breached."""
        return 1 - _divide(threshold, actual, "actual")
 
    # ---- Cash flow ----------------------------------------------------------
 
    @classmethod
    @llm_tool
    def free_cash_flow(cls, operating_cash_flow: float, capex: float):
        """Free cash flow: operating cash flow less capex."""
        return _d(operating_cash_flow, "operating_cash_flow") - _d(capex, "capex")
 
    @classmethod
    @llm_tool
    def cash_conversion(cls, operating_cash_flow: float, ebitda: float):
        """Cash conversion: operating cash flow / EBITDA. Needs positive EBITDA."""
        if _d(ebitda, "ebitda") <= 0:
            raise CalculationError("Cash conversion is not meaningful when EBITDA is zero or negative")
        return _divide(operating_cash_flow, ebitda, "ebitda")
 
    # ---- Profitability (fractions: 0.12 = 12%) ------------------------------
    # Revenue, EBITDA, net income and D&A must be on the same period basis.
 
    @classmethod
    @llm_tool
    def ebit(cls, ebitda: float, depreciation_amortisation: float):
        """Operating profit: EBITDA less depreciation and amortisation."""
        return _d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation")
 
    @classmethod
    @llm_tool
    def ebitda_margin(cls, ebitda: float, revenue: float):
        """EBITDA / revenue."""
        return _divide(ebitda, revenue, "revenue")
 
    @classmethod
    @llm_tool
    def ebit_margin(cls, ebitda: float, depreciation_amortisation: float, revenue: float):
        """(EBITDA - D&A) / revenue."""
        return _divide(_d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation"), revenue, "revenue")
 
    @classmethod
    @llm_tool
    def net_margin(cls, net_income: float, revenue: float):
        """Net income / revenue."""
        return _divide(net_income, revenue, "revenue")
 
    @classmethod
    @llm_tool
    def free_cash_flow_margin(cls, operating_cash_flow: float, capex: float, revenue: float):
        """(Operating cash flow - capex) / revenue."""
        return _divide(_d(operating_cash_flow, "operating_cash_flow") - _d(capex, "capex"), revenue, "revenue")
 
    @classmethod
    @llm_tool
    def return_on_assets(cls, net_income: float, total_assets: float):
        """Net income / total assets."""
        return _divide(net_income, total_assets, "total_assets")
 
    @classmethod
    @llm_tool
    def return_on_equity(cls, net_income: float, net_worth: float):
        """Net income / net worth. Not meaningful when net worth is zero or negative."""
        if _d(net_worth, "net_worth") <= 0:
            raise CalculationError("Return on equity is not meaningful when net_worth is zero or negative")
        return _divide(net_income, net_worth, "net_worth")
 
    @classmethod
    @llm_tool
    def equity_ratio(cls, net_worth: float, total_assets: float):
        """Share of assets funded by equity: net worth / total assets."""
        return _divide(net_worth, total_assets, "total_assets")
 
    @classmethod
    @llm_tool
    def debt_to_assets(cls, total_debt: float, total_assets: float):
        """Total debt / total assets."""
        return _divide(total_debt, total_assets, "total_assets")
 
    @classmethod
    @llm_tool
    def ebit_interest_cover(cls, ebitda: float, depreciation_amortisation: float, net_interest_expense: float):
        """(EBITDA - D&A) / net interest expense. Stricter than EBITDA interest cover."""
        return _divide(_d(ebitda, "ebitda") - _d(depreciation_amortisation, "depreciation_amortisation"), net_interest_expense, "net_interest_expense")
 
    # ---- LLM plumbing -------------------------------------------------------
 
    @classmethod
    def _tools(cls) -> dict[str, Callable]:
        return {n: f for n, f in inspect.getmembers(cls, inspect.ismethod) if n in _REGISTRY}
    
    _PARAM_DESCRIPTIONS: ClassVar[dict[str, str]] = {
        "total_debt": "Total borrowings, in currency units (not thousands or millions).",
        "cash": "Cash and cash equivalents, in the same currency as the other amounts.",
        "drawn_amount": "Amount currently drawn on the facility.",
        "committed_amount": "Total amount the lender has committed to the facility.",
        "available_amounts": "List of undrawn or otherwise accessible amounts, for example undrawn revolving credit facility headroom.",
        "principal_amount": "Scheduled repayment amount that was due.",
        "amount_paid": "Amount actually paid against the scheduled repayment.",
        "actual": "The borrower's actual ratio as a multiple (for example 3.2 for 3.2x).",
        "threshold": "The covenant limit as a multiple (for example 4.5 for 4.5x).",
        "operating_cash_flow": "Cash generated by operations. Can be negative.",
        "capex": "Capital expenditure for the same period as operating cash flow.",
        "ebitda": "Earnings before interest, tax, depreciation and amortisation, annualised or LTM to match the other earnings figures.",
        "depreciation_amortisation": "Depreciation and amortisation charge on the same period basis as EBITDA.",
        "revenue": "Revenue on the same period basis as the earnings figure it is compared with.",
        "net_income": "Profit after interest and tax on the same period basis as revenue. Can be negative.",
        "total_assets": "Total assets from the balance sheet.",
        "net_worth": "Equity (total assets less total liabilities).",
        "net_interest_expense": "Interest expense less interest income for the period.",
    }
 
    @classmethod
    def _method_definitions(cls) -> list[dict]:
        """One definition per calculation, built from type hints and docstrings."""
        def json_type(tp: Any) -> dict:
            if tp is float or tp is int:
                return {"type": "number"}
            if getattr(tp, "__origin__", None) is list:
                return {"type": "array", "items": json_type(tp.__args__[0])}
            return {"type": "string"}
 
        definitions = []
        for name, method in cls._tools().items():
            properties = {}
            for param, spec in inspect.signature(method).parameters.items():
                if param in ["self", "cls"]:
                    continue
                properties[param] = {
                    **json_type(spec.annotation),
                    "description": cls._PARAM_DESCRIPTIONS[param],
                }
            definitions.append({
                "name": name,
                "description": inspect.getdoc(method) or name,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                },
            })
        return definitions
 
    @classmethod
    def schema(cls) -> dict:
        """Single tool definition for the LLM, matching run(name, arguments).
 
        The per-method schemas are embedded in the description of `arguments`,
        so a new @llm_tool method is picked up automatically. Use it like
        DocumentSearchTool.schema(): tools = [DocumentSearchTool.schema(), CalculationTool.schema()]
        and call tool.run(**block.input) for a tool_use block.
        """
        methods = cls._method_definitions()
        method_schemas = "\n".join(
            json.dumps(
                {
                    "name": m["name"],
                    "description": m["description"],
                    "parameters": m["input_schema"]["properties"],
                    "required": m["input_schema"]["required"],
                },
                separators=(",", ":"),
            )
            for m in methods
        )
        return {
            "name": "run_calculation",
            "description": (
                "Run a deterministic credit calculation (ratios, covenant headroom, liquidity, "
                "cash flow and profitability). Use this instead of calculating by hand. "
                "Ratios and margins are returned as fractions (0.12 = 12%). Headroom and cushion "
                "are positive when a covenant is met and negative when it is breached."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "enum": [m["name"] for m in methods],
                        "description": "The calculation to run.",
                    },
                    "arguments": {
                        "type": "object",
                        "description": (
                            "Arguments for the chosen calculation, as a JSON object keyed by parameter name. "
                            "Provide every required parameter for that calculation. "
                            "Available calculations, one JSON schema per line:\n" + method_schemas
                        ),
                    },
                },
                "required": ["name", "arguments"],
            },
        }
 
    @classmethod
    def run(cls, name: str, arguments: dict) -> tuple[str, bool]:
        """Dispatch a tool call from the LLM.
 
        Returns (content, is_error). On success content is the JSON-encoded result
        and is_error is False. On failure content is the error message and
        is_error is True.
        """
        tools = cls._tools()
        if name not in tools:
            return f"Unknown tool '{name}'. Available: {sorted(tools)}", True
        try:
            result = getattr(cls, name)(**(arguments or {}))
        except Exception as e:  # defensive: the wrapper already handles expected errors
            return f"Unexpected error in '{name}': {e}", True
        if not result["ok"]:
            return result["error"], True
        return json.dumps(result["value"]), False
 