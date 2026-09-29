from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from tickets import Ticket, load_sample_tickets

SYSTEM_ACTOR = "system:auto-close"
AUTO_CLOSE_EXEMPT_PRIORITIES = {"Urgent"}
DEFAULT_WARNING_WINDOW_DAYS = 2


@dataclass
class AutoCloseResult:
    closed: List[Ticket]
    needs_warning: List[Ticket]


def run_auto_close(
    tickets: List[Ticket],
    now: Optional[datetime] = None,
    warning_window_days: int = DEFAULT_WARNING_WINDOW_DAYS,
) -> AutoCloseResult:
    """Close open tickets past their reply_deadline and flag tickets needing a nudge.

    Urgent tickets are never auto-closed, even once overdue - they land in
    needs_warning instead so a human decides what to do with them.
    """
    now = now or datetime.now()
    closed = []
    needs_warning = []

    for ticket in tickets:
        if ticket.status != "open":
            continue

        if now > ticket.reply_deadline:
            if ticket.priority in AUTO_CLOSE_EXEMPT_PRIORITIES:
                needs_warning.append(ticket)
            else:
                ticket.status = "closed"
                ticket.closed_by = SYSTEM_ACTOR
                closed.append(ticket)
        elif (ticket.reply_deadline - now).days <= warning_window_days:
            needs_warning.append(ticket)

    return AutoCloseResult(closed=closed, needs_warning=needs_warning)


if __name__ == "__main__":
    result = run_auto_close(load_sample_tickets())

    print("Closed:")
    for ticket in result.closed:
        print(f"  {ticket.id} ({ticket.customer}) - {ticket.subject}")

    print("Needs warning:")
    for ticket in result.needs_warning:
        print(f"  {ticket.id} ({ticket.customer}) - {ticket.subject}")
