from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Ticket:
    id: str
    customer: str
    subject: str
    priority: str  # "Normal" or "Urgent"
    status: str  # "open" or "closed"
    created_at: datetime
    last_customer_reply_at: datetime
    reply_deadline: datetime
    closed_by: Optional[str] = None


def _days_ago(n: int) -> datetime:
    return datetime.now() - timedelta(days=n)


def load_sample_tickets() -> List[Ticket]:
    """Return a fresh list of sample tickets, dated relative to today."""
    return [
        Ticket(
            id="HD-1001",
            customer="Priya Shah",
            subject="Invoice PDF won't download",
            priority="Normal",
            status="open",
            created_at=_days_ago(20),
            last_customer_reply_at=_days_ago(14),
            reply_deadline=_days_ago(-2),
        ),
        Ticket(
            id="HD-1002",
            customer="Callum Reid",
            subject="Can't reset account password",
            priority="Normal",
            status="open",
            created_at=_days_ago(15),
            last_customer_reply_at=_days_ago(13),
            reply_deadline=_days_ago(-4),
        ),
        Ticket(
            id="HD-1003",
            customer="Aiswarya Menon",
            subject="Production integration returning 500s",
            priority="Urgent",
            status="open",
            created_at=_days_ago(45),
            last_customer_reply_at=_days_ago(40),
            reply_deadline=_days_ago(30),
        ),
        Ticket(
            id="HD-1004",
            customer="Ben Okafor",
            subject="Question about billing cycle",
            priority="Normal",
            status="closed",
            created_at=_days_ago(60),
            last_customer_reply_at=_days_ago(35),
            reply_deadline=_days_ago(20),
            closed_by="Jamie Ochieng",
        ),
        Ticket(
            id="HD-1005",
            customer="Freya Lindqvist",
            subject="Export button does nothing",
            priority="Normal",
            status="open",
            created_at=_days_ago(33),
            last_customer_reply_at=_days_ago(30),
            reply_deadline=_days_ago(18),
        ),
        Ticket(
            id="HD-1006",
            customer="Marcus Tan",
            subject="Feature request: dark mode",
            priority="Normal",
            status="open",
            created_at=_days_ago(10),
            last_customer_reply_at=_days_ago(2),
            reply_deadline=_days_ago(-5),
        ),
        Ticket(
            id="HD-1007",
            customer="Nadia Hassan",
            subject="Login page intermittently blank",
            priority="Urgent",
            status="open",
            created_at=_days_ago(6),
            last_customer_reply_at=_days_ago(5),
            reply_deadline=_days_ago(-1),
        ),
    ]
