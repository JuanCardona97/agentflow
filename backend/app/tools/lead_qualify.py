"""
Lead Qualification Tool — Scores and categorizes potential customers.

In production, this would integrate with your CRM
(Salesforce, HubSpot, Pipedrive, etc.)
"""

from langchain_core.tools import tool


@tool
def lead_qualify(
    name: str,
    company: str,
    use_case: str,
    budget: str,
    timeline: str,
    company_size: str = "unknown",
) -> str:
    """Qualify a potential customer lead based on their profile.

    Use this tool after gathering the prospect's information through
    conversation. It scores the lead and provides a recommendation.

    Args:
        name: Contact person's full name.
        company: Company or organization name.
        use_case: What they want to achieve / their pain point.
        budget: Their budget range (e.g., "$5k-10k", "under $1k", "$50k+").
        timeline: When they need the solution (e.g., "this month", "Q3 2026").
        company_size: Number of employees or team size (optional).

    Returns:
        Lead qualification score, category, and recommended next steps.
    """
    # Score the lead based on criteria
    score = 0
    factors = []

    # Budget scoring
    budget_lower = budget.lower().replace(",", "").replace("$", "")
    if any(x in budget_lower for x in ["50k", "100k", "50000", "100000"]):
        score += 40
        factors.append("High budget (40pts)")
    elif any(x in budget_lower for x in ["10k", "20k", "30k", "10000", "20000"]):
        score += 25
        factors.append("Medium budget (25pts)")
    elif any(x in budget_lower for x in ["5k", "5000"]):
        score += 15
        factors.append("Moderate budget (15pts)")
    else:
        score += 5
        factors.append("Low/unclear budget (5pts)")

    # Timeline scoring
    timeline_lower = timeline.lower()
    if any(x in timeline_lower for x in ["asap", "now", "this week", "urgent", "immediately"]):
        score += 30
        factors.append("Urgent timeline (30pts)")
    elif any(x in timeline_lower for x in ["this month", "next month", "soon"]):
        score += 20
        factors.append("Short-term timeline (20pts)")
    elif any(x in timeline_lower for x in ["quarter", "q1", "q2", "q3", "q4"]):
        score += 10
        factors.append("Quarterly timeline (10pts)")
    else:
        score += 5
        factors.append("Long/unclear timeline (5pts)")

    # Company size scoring
    size_lower = company_size.lower()
    if any(x in size_lower for x in ["enterprise", "1000", "500+"]):
        score += 20
        factors.append("Enterprise company (20pts)")
    elif any(x in size_lower for x in ["100", "200", "mid"]):
        score += 15
        factors.append("Mid-market company (15pts)")
    elif any(x in size_lower for x in ["50", "startup", "small"]):
        score += 10
        factors.append("Small/startup (10pts)")

    # Use case clarity
    if len(use_case) > 50:
        score += 10
        factors.append("Clear use case description (10pts)")

    # Categorize
    if score >= 70:
        category = "HOT"
        action = "Schedule a demo call within 24 hours. Assign to senior sales rep."
    elif score >= 45:
        category = "WARM"
        action = "Send personalized follow-up email with case studies. Schedule call within 48 hours."
    elif score >= 25:
        category = "COOL"
        action = "Add to nurture email sequence. Follow up in 1-2 weeks."
    else:
        category = "COLD"
        action = "Add to general mailing list. Monitor for engagement."

    factors_str = "\n".join(f"  - {f}" for f in factors)

    return (
        f"Lead Qualification Report\n"
        f"{'=' * 40}\n"
        f"Contact: {name}\n"
        f"Company: {company} ({company_size})\n"
        f"Use case: {use_case}\n"
        f"Budget: {budget}\n"
        f"Timeline: {timeline}\n"
        f"\n"
        f"Score: {score}/100\n"
        f"Category: {category}\n"
        f"\nScoring breakdown:\n{factors_str}\n"
        f"\nRecommended action: {action}\n"
        f"\nLead saved to CRM successfully."
    )
