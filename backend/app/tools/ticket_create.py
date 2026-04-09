"""
Ticket Creation Tool — Creates support tickets for human follow-up.

In production, this would integrate with your helpdesk
(Zendesk, Freshdesk, Intercom, Jira Service Desk, etc.)
"""

import uuid
from datetime import datetime, timezone

from langchain_core.tools import tool


# In-memory ticket store (replace with database in production)
_TICKETS: dict[str, dict] = {}


@tool
def ticket_create(
    subject: str,
    description: str,
    priority: str = "medium",
    category: str = "general",
    customer_email: str | None = None,
    order_id: str | None = None,
) -> str:
    """Create a support ticket for issues that need human follow-up.

    Use this tool when:
    - The issue requires human investigation (refunds, disputes, etc.)
    - You cannot resolve the customer's problem with available tools
    - The customer explicitly requests to speak with a human
    - There's a technical issue that needs engineering attention

    Args:
        subject: Brief summary of the issue (max 100 chars).
        description: Detailed description including relevant context from the conversation.
        priority: Ticket priority — "low", "medium", "high", or "urgent".
        category: Issue category — "general", "billing", "shipping", "technical", "refund", "complaint".
        customer_email: Customer's email for follow-up notifications.
        order_id: Related order ID, if applicable.

    Returns:
        Confirmation with the ticket ID and estimated response time.
    """
    # Validate priority
    valid_priorities = {"low", "medium", "high", "urgent"}
    priority = priority.lower().strip()
    if priority not in valid_priorities:
        priority = "medium"

    # Validate category
    valid_categories = {"general", "billing", "shipping", "technical", "refund", "complaint"}
    category = category.lower().strip()
    if category not in valid_categories:
        category = "general"

    # Generate ticket
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.now(timezone.utc)

    ticket = {
        "ticket_id": ticket_id,
        "subject": subject[:100],
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "customer_email": customer_email,
        "order_id": order_id,
        "created_at": now.isoformat(),
        "assigned_to": _auto_assign(priority, category),
    }

    _TICKETS[ticket_id] = ticket

    # Estimate response time based on priority
    response_times = {
        "urgent": "1 hour",
        "high": "4 hours",
        "medium": "24 hours",
        "low": "48 hours",
    }

    return (
        f"Ticket created successfully!\n"
        f"\n"
        f"Ticket ID: {ticket_id}\n"
        f"Subject: {subject}\n"
        f"Priority: {priority.upper()}\n"
        f"Category: {category.capitalize()}\n"
        f"Status: Open\n"
        f"Assigned to: {ticket['assigned_to']}\n"
        f"Created: {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"\n"
        f"Estimated response time: {response_times[priority]}\n"
        f"{'The customer will receive email updates at ' + customer_email if customer_email else 'No email provided for updates.'}"
    )


def _auto_assign(priority: str, category: str) -> str:
    """Auto-assign ticket to the appropriate team."""
    assignments = {
        "billing": "Billing Team",
        "refund": "Billing Team",
        "shipping": "Logistics Team",
        "technical": "Engineering Team",
        "complaint": "Customer Success Team",
        "general": "Support Team",
    }

    team = assignments.get(category, "Support Team")

    if priority == "urgent":
        team += " (Escalated — Manager notified)"

    return team
