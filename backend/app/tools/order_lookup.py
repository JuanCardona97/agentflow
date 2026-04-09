"""
Order Lookup Tool — Searches orders by ID or customer email.

In production, this would connect to your database or e-commerce API
(Shopify, WooCommerce, Stripe, etc.)
"""

from langchain_core.tools import tool


# Simulated order database
_ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_name": "Sarah Johnson",
        "customer_email": "sarah@example.com",
        "status": "shipped",
        "tracking_number": "1Z999AA10123456784",
        "carrier": "UPS",
        "items": [
            {"name": "Wireless Headphones Pro", "qty": 1, "price": 149.99},
            {"name": "USB-C Cable", "qty": 2, "price": 12.99},
        ],
        "total": 175.97,
        "order_date": "2026-03-15",
        "estimated_delivery": "2026-04-02",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_name": "Mike Chen",
        "customer_email": "mike@example.com",
        "status": "processing",
        "tracking_number": None,
        "carrier": None,
        "items": [
            {"name": "Ergonomic Keyboard", "qty": 1, "price": 89.99},
        ],
        "total": 89.99,
        "order_date": "2026-03-28",
        "estimated_delivery": "2026-04-08",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_name": "Sarah Johnson",
        "customer_email": "sarah@example.com",
        "status": "delivered",
        "tracking_number": "1Z999AA10123456799",
        "carrier": "UPS",
        "items": [
            {"name": "Monitor Stand", "qty": 1, "price": 59.99},
            {"name": "Desk Lamp LED", "qty": 1, "price": 34.99},
        ],
        "total": 94.98,
        "order_date": "2026-03-01",
        "estimated_delivery": "2026-03-10",
    },
}


@tool
def order_lookup(
    order_id: str | None = None,
    customer_email: str | None = None,
) -> str:
    """Look up order details by order ID or customer email.

    Use this tool when a customer asks about their order status,
    tracking information, or order details.

    Args:
        order_id: The order ID (e.g., ORD-1001). Preferred lookup method.
        customer_email: Customer's email address. Returns all orders for that email.

    Returns:
        Order details including status, tracking, items, and delivery estimate.
    """
    if not order_id and not customer_email:
        return "Error: Please provide either an order_id or customer_email to look up."

    # Search by order ID
    if order_id:
        order_id = order_id.upper().strip()
        order = _ORDERS.get(order_id)
        if not order:
            return f"No order found with ID '{order_id}'. Please verify the order number."
        return _format_order(order)

    # Search by email
    if customer_email:
        email = customer_email.lower().strip()
        matches = [o for o in _ORDERS.values() if o["customer_email"] == email]
        if not matches:
            return f"No orders found for email '{email}'."
        return "\n---\n".join(_format_order(o) for o in matches)

    return "No results found."


def _format_order(order: dict) -> str:
    """Format an order dict into a readable string."""
    items_str = ", ".join(
        f"{item['name']} (x{item['qty']}, ${item['price']})"
        for item in order["items"]
    )

    tracking = order["tracking_number"] or "Not yet available"
    carrier = order["carrier"] or "Pending"

    return (
        f"Order: {order['order_id']}\n"
        f"Customer: {order['customer_name']} ({order['customer_email']})\n"
        f"Status: {order['status'].upper()}\n"
        f"Items: {items_str}\n"
        f"Total: ${order['total']}\n"
        f"Ordered: {order['order_date']}\n"
        f"Estimated delivery: {order['estimated_delivery']}\n"
        f"Tracking: {tracking} ({carrier})"
    )
