"""
Knowledge Base Tool — Searches FAQs, policies, and product documentation.

In production, this would use a vector database with your actual docs
(similar to the RAG system in DocuChat AI).
"""

from langchain_core.tools import tool


# Simulated knowledge base entries
_KB_ENTRIES = [
    {
        "id": "kb-001",
        "title": "Return Policy",
        "category": "policies",
        "content": (
            "We offer a 30-day return policy for all unused items in original packaging. "
            "Refunds are processed within 5-7 business days after we receive the returned item. "
            "Return shipping is free for defective products. For non-defective returns, "
            "a $5.99 return shipping fee applies. Sale items are final sale and cannot be returned."
        ),
    },
    {
        "id": "kb-002",
        "title": "Shipping Information",
        "category": "shipping",
        "content": (
            "Standard shipping (5-7 business days): Free on orders over $50, otherwise $5.99. "
            "Express shipping (2-3 business days): $12.99. "
            "Overnight shipping (next business day): $24.99. "
            "We ship to all 50 US states and internationally to 30+ countries. "
            "International shipping rates vary by destination and typically take 7-14 business days."
        ),
    },
    {
        "id": "kb-003",
        "title": "Warranty Coverage",
        "category": "products",
        "content": (
            "All electronics come with a 1-year manufacturer warranty covering defects in "
            "materials and workmanship. Extended warranty (2 additional years) is available "
            "for $19.99 at checkout. Warranty does not cover accidental damage, water damage, "
            "or normal wear and tear. To file a warranty claim, contact support with your "
            "order ID and a description of the issue."
        ),
    },
    {
        "id": "kb-004",
        "title": "Payment Methods",
        "category": "billing",
        "content": (
            "We accept Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, "
            "and Google Pay. We also offer Affirm financing for orders over $100 — split "
            "your purchase into 3, 6, or 12 monthly payments with 0% APR for qualified buyers. "
            "All transactions are secured with 256-bit SSL encryption."
        ),
    },
    {
        "id": "kb-005",
        "title": "Account & Password Issues",
        "category": "technical",
        "content": (
            "To reset your password, click 'Forgot Password' on the login page and enter "
            "your email. You'll receive a reset link within 5 minutes. If you don't see the "
            "email, check your spam folder. For account lockouts after 5 failed attempts, "
            "wait 30 minutes or contact support. To delete your account, go to Settings > "
            "Privacy > Delete Account."
        ),
    },
    {
        "id": "kb-006",
        "title": "Bulk & Enterprise Orders",
        "category": "sales",
        "content": (
            "For orders of 50+ units, we offer volume discounts starting at 10% off. "
            "Enterprise customers get dedicated account management, custom invoicing (NET 30), "
            "and priority support. Contact our sales team at enterprise@example.com or use "
            "our lead qualification form to get started."
        ),
    },
]


@tool
def search_knowledge_base(query: str) -> str:
    """Search the company knowledge base for product info, policies, and FAQs.

    Use this tool when a customer asks about:
    - Return/refund policies
    - Shipping options and rates
    - Warranty information
    - Payment methods
    - Account issues
    - Product details
    - Any general company policy

    Args:
        query: The customer's question or search terms.

    Returns:
        Relevant knowledge base articles matching the query.
    """
    query_lower = query.lower()

    # Simple keyword matching (in production, use vector similarity search)
    scored_entries = []
    for entry in _KB_ENTRIES:
        score = 0
        searchable = f"{entry['title']} {entry['category']} {entry['content']}".lower()

        # Score based on word overlap
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2 and word in searchable:
                score += 1

        # Boost for category match
        if entry["category"] in query_lower:
            score += 3

        # Boost for title match
        if any(w in entry["title"].lower() for w in query_words if len(w) > 3):
            score += 5

        if score > 0:
            scored_entries.append((score, entry))

    # Sort by score and take top results
    scored_entries.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_entries[:3]

    if not top_results:
        return (
            "No relevant articles found in the knowledge base for that query. "
            "You may want to create a support ticket for further assistance."
        )

    results = []
    for _, entry in top_results:
        results.append(
            f"[{entry['id']}] {entry['title']}\n"
            f"Category: {entry['category']}\n"
            f"{entry['content']}"
        )

    return "\n\n---\n\n".join(results)
