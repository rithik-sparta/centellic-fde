"""Reports API — handed over by a contractor. Not reviewed.

SYNTHETIC PLACEHOLDER DATA ONLY.
"""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
import json
import hashlib

router = APIRouter(prefix="/reports", tags=["reports"])


REPORTS: list[dict[str, Any]] = [
    {"id": 1, "title": "UK Market Outlook", "firm_id": 1, "revisions": ["v1"]},
    {"id": 2, "title": "US Partner Compensation", "firm_id": 2, "revisions": ["v1"]},
]

_view_counts: dict[int, int] = {}

_idempotency_cache: dict[str, dict] = {}

def generate_request_hash(request_body: dict) -> str:
    """Generate hash of request payload"""
    body_str = json.dumps(request_body, sort_keys=True)
    return hashlib.sha256(body_str.encode()).hexdigest()

class NewReport(BaseModel):
    title: str = Field(min_length=1)
    firm_id: int


def get_report_or_404(report_id: int) -> dict:
    for report in REPORTS:
        if report["id"] == report_id:
            return report
    raise HTTPException(status_code=404, detail=f"No report with id {report_id}")


@router.get("")
def list_reports():
    return REPORTS


@router.get("/{report_id}")
async def get_report(report_id: int):
    report = get_report_or_404(report_id)
    _view_counts[report_id] = _view_counts.get(report_id, 0) + 1
    return {**report, "views": _view_counts[report_id]}


@router.post("", status_code=201)
def create_report(new: NewReport,
                #   idempotency_key: str = Header(None)
                  ):
    # # Check if idempotency key already exists
    # if idempotency_key:
    #     if idempotency_key in _idempotency_cache:
    #         cached = _idempotency_cache[idempotency_key]
            
    #         # Validate request body matches
    #         request_hash = generate_request_hash(new.dict())
    #         if cached["request_hash"] != request_hash:
    #             raise HTTPException(
    #                 status_code=422,
    #                 detail="Idempotency key reused with different request body"
    #             )
            
    #         # Return cached response
    #         return cached["response"]
        
    new_id = max(report["id"] for report in REPORTS) + 1
    report = {
        "id": new_id,
        "title": new.title,
        "firm_id": new.firm_id,
        "revisions": ["v1"],
    }
    
    REPORTS.append(report)
    
    # # Cache the response
    # if idempotency_key:
    #     _idempotency_cache[idempotency_key] = {
    #         "response": report,
    #         "request_hash": generate_request_hash(new.dict())
    #     }
    
    return report


@router.put("/{report_id}")
def update_report(report_id: int, new: NewReport):
    report = get_report_or_404(report_id)
    report["title"] = new.title
    report["firm_id"] = new.firm_id
    report["revisions"].append(f"v{len(report['revisions']) + 1}")
    return report


@router.get("/{report_id}/export")
async def export_report(report_id: int):
    report = get_report_or_404(report_id)
    time.sleep(3)
    return {"id": report["id"], "title": report["title"], "format": "pdf"}


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: int):
    report = get_report_or_404(report_id)
    _view_counts.pop(report_id, None)
    REPORTS.remove(report)
    return
