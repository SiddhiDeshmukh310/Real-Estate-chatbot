"""
Fallback rule-based parser for Real Estate Insights.
Translates user queries into validated StructuredQuery objects when LLM is unavailable or fails.
"""

from typing import List
from .schemas import StructuredQuery, ALLOWED_LOCALITIES

BEST_INVESTMENT_KEYWORDS = ["best", "investment", "top", "winner", "highest", "good investment"]
COMPARE_KEYWORDS = ["compare", "vs", "versus", "difference", "between"]
UNITS_KEYWORDS = ["units", "sold", "demand", "sales", "volume"]
CARPET_KEYWORDS = ["carpet", "area", "size", "sqft"]


def parse_query_rule_based(query: str) -> StructuredQuery:
    q = query.lower().strip()

    found_localities: List[str] = []
    if "wakad" in q:
        found_localities.append("Wakad")
    if "aundh" in q:
        found_localities.append("Aundh")
    if "akurdi" in q or "chinchwad" in q:
        found_localities.append("Akurdi")
    if any(x in q for x in ["ambegaon", "ambegao", "ambegaon budruk", "ambegaonbk", "ambegaon bk"]):
        found_localities.append("Ambegaon Budruk")

    # Determine metric
    metric = "flat_rate"
    if any(k in q for k in UNITS_KEYWORDS):
        metric = "units_sold"
    elif any(k in q for k in CARPET_KEYWORDS) and not any(w in q for w in ["rate", "price"]):
        metric = "carpet_area"

    # Best investment query -> analyze all 4 localities with top_n operation
    if any(k in q for k in BEST_INVESTMENT_KEYWORDS):
        return StructuredQuery(
            operation="top_n",
            metric=metric,
            localities=list(ALLOWED_LOCALITIES),
            start_year=2020,
            end_year=2024,
            group_by="location",
            is_valid=True
        )

    # Comparison query or multiple localities
    if any(k in q for k in COMPARE_KEYWORDS) or len(found_localities) > 1:
        locs = found_localities if len(found_localities) >= 2 else list(ALLOWED_LOCALITIES)
        return StructuredQuery(
            operation="compare",
            metric=metric,
            localities=locs,
            start_year=2020,
            end_year=2024,
            group_by="location",
            is_valid=True
        )

    # Single locality analysis
    if len(found_localities) == 1:
        return StructuredQuery(
            operation="locality_summary",
            metric=metric,
            localities=found_localities,
            start_year=2020,
            end_year=2024,
            group_by="year",
            is_valid=True
        )

    unsupported_cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata']
    if any(city in q for city in unsupported_cities) and not found_localities:
        return StructuredQuery(
            operation='locality_summary',
            metric='flat_rate',
            localities=[],
            is_valid=False,
            rejection_reason='Location outside supported dataset. Supported localities: Wakad, Aundh, Akurdi, Ambegaon Budruk.'
        )

    # Generic real estate query -> default to all 4 localities
    if any(w in q for w in ["area", "pune", "rate", "price", "property", "analysis", "analyze", "flat", "locality"]):
        return StructuredQuery(
            operation="locality_summary",
            metric=metric,
            localities=list(ALLOWED_LOCALITIES),
            start_year=2020,
            end_year=2024,
            group_by="location",
            is_valid=True
        )

    # If nothing matched, reject safely
    return StructuredQuery(
        operation="locality_summary",
        metric="flat_rate",
        localities=[],
        is_valid=False,
        rejection_reason="Could not identify any Pune locality or real estate metric in the query. Please mention Wakad, Aundh, Akurdi, or Ambegaon Budruk."
    )

