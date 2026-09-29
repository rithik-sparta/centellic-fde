from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from data import FIRMS

router = APIRouter(prefix = "/firms", tags=["firms"])


_seen_keys : dict[str,dict] = {}

class NewFirm(BaseModel):
    name : str = Field(min_length=1)
    jurisdiction : str = Field(min_length=2, max_length=5)
    revenue_usd_m : float = Field(gt=0)
    lawyers : int = Field(gt=0)
    equity_partners : int = Field(gt=0)
    
class UpdateFirm(BaseModel):
    name : str | None = Field(None, min_length=1)
    jurisdiction : str | None = Field(None, min_length=2, max_length=5)
    revenue_usd_m : float | None = Field(None, gt=0)
    lawyers : int | None = Field(None, gt=0)
    equity_partners : int | None = Field(None, gt=0)

def get_firm_or_404(firm_id: int) -> dict:
    for firm in FIRMS:
        if firm["id"] == firm_id:
            return firm
    raise HTTPException(404, f"No firm with id {firm_id}.")



# list_firms always returns everything
# add two optional query params not a path param

@router.get("")
def list_firms(jurisdiction: str | None = None, revenue_usd_m_gte: int | None = None):
    answer = FIRMS
    
    if jurisdiction is not None:
        answer = [f for f in FIRMS if f == jurisdiction]
    
    if revenue_usd_m_gte is not None:
        answer = [f for f in FIRMS if f["revenue_usd_m"] >= revenue_usd_m_gte]
            
    return answer

# get one firm
# someone asks for firm 999
@router.get("/{firm_id}")
def get_firm(firm : dict = Depends(get_firm_or_404)):  # noqa: B008
    return firm

# compute revenue per lawyer is total revenue divided by fee-earner headcount
# profit per equity partner assumes a 365 margin, then divided by the number of equity
# bother are pretty standard law firm benchmarks... the kind of things Centellic platforms provides.

@router.get("/{firm_id}/benchmarks")
def get_benchmarks(firm : dict = Depends(get_firm_or_404)):  # noqa: B008
    
    revenue : int = int(firm["revenue_usd_m"])
    return {
        "id":firm["id"],
        "name":firm["name"],
        "revenue_per_lawyer_usd" : round((revenue*1_000_000) / firm["lawyers"]),
        "profit_per_equity_partner" : round(revenue*1_000_000*0.35 / firm["equity_partners"])
    }

# 200 {"id":2,"name":"Marchetti Ruiz","revenue_per_lawyer_usd":1241667,"profit_per_equity_partner":3067647}
# 404 {"detail":"No firm with id 23."}


# everything so far has been read only
# now somebody sends you data and you have no idea what it is

"""
First, describe what you will accept (shape)
"""


    
# post endpoint
# annotating parameter with a pydantic model means request body. int or string means url or query.
# 201 means created. Want to be specific with status codes
# Find highest id and add 1
# /firms
@router.post("", status_code=201)
def add_firm(new: NewFirm, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]
    
    new_id = max([firm["id"] for firm in FIRMS])+1
    
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }

    FIRMS.append(firm)
    
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm
        
    return firm


"""CHALLENGE 1 - replace a firm's data.

    Requirements:
      - Body is validated the same way as POST /firms (how did we do this before?).
      - Update `firm`'s fields *in place* so the change persists for later
        requests (the same idea as add_firm appending to FIRMS - mutate
        the existing dict, don't just return a new one).
      - Return the updated firm.
      - Status code 200 (the default - no status_code= needed).
"""


@router.put("/{firm_id}")
def update_firm(firm : dict = Depends(get_firm_or_404), to_update: UpdateFirm | None = None):  # noqa: B008
    if to_update == None:
        return firm
        #raise HTTPException(400, "No request body found.")
    updates = to_update.model_dump(exclude_none=True)
    firm.update(updates)
    return firm

"""CHALLENGE 2 - remove a firm.

Requirements:
    - `firm` is already looked up and guaranteed to exist.
    - Remove it from the FIRMS list.
    - Return nothing (a 204 response must have an empty body - a bare
    `return` is enough; FastAPI handles the rest because of
    status_code=204 above).
"""

@router.delete("/{firm_id}", status_code=204)
def delete_firm(firm : dict = Depends(get_firm_or_404)):  # noqa: B008

    FIRMS.remove(firm)
    