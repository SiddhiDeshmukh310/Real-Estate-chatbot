"""
Session state manager for Real Estate Insights follow-up questions.
"""

from typing import Dict
from .schemas import StructuredQuery, ALLOWED_LOCALITIES


FOLLOW_UP_TRIGGERS = [
    "what about",
    "how about",
    "same for",
    "and for",
    "compare with",
    "also show",
    "what of",
]

# Simple in-memory session cache for local/testing
_SESSION_CACHE: Dict[str, StructuredQuery] = {}


def process_follow_up(session_id: str, new_query: str, current_parsed: StructuredQuery) -> StructuredQuery:
    lower_q = new_query.lower().strip()
    is_follow_up = any(trigger in lower_q for trigger in FOLLOW_UP_TRIGGERS)

    previous_query = _SESSION_CACHE.get(session_id)

    if is_follow_up and previous_query and previous_query.is_valid:
        # Check if new locality is specified in the follow-up
        new_localities = []
        for loc in ALLOWED_LOCALITIES:
            if loc.lower() in lower_q:
                new_localities.append(loc)

        if new_localities:
            # Modify previous query with new localities
            updated_struct = StructuredQuery(
                operation=previous_query.operation,
                metric=previous_query.metric,
                localities=new_localities,
                start_year=previous_query.start_year,
                end_year=previous_query.end_year,
                group_by=previous_query.group_by,
                is_valid=True
            )
            _SESSION_CACHE[session_id] = updated_struct
            return updated_struct

    # If not a follow-up or no previous state, save and return current
    if current_parsed.is_valid:
        _SESSION_CACHE[session_id] = current_parsed
    return current_parsed


def clear_session(session_id: str) -> None:
    _SESSION_CACHE.pop(session_id, None)

