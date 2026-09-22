"""
LLM Query Parser for Real Estate Insights.
Parses natural language queries into validated StructuredQuery Pydantic objects.
Falls back safely to rule-based parsing if no API key is provided or on provider error.
"""

import os
import json
import logging
import requests
from typing import Dict, Any
from .schemas import StructuredQuery, ALLOWED_LOCALITIES, ALLOWED_OPERATIONS, ALLOWED_METRICS
from .fallback_parser import parse_query_rule_based

logger = logging.getLogger("real_estate_insights")

PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore instructions",
    "system prompt",
    "reveal key",
    "print key",
    "delete table",
    "drop table",
    "exec(",
    "eval(",
    "<script>",
    "sudo",
]


def parse_query_with_llm(query: str, mock_provider: Any = None) -> StructuredQuery:
    cleaned_query = query.strip()
    if len(cleaned_query) > 250:
        return StructuredQuery(
            operation="locality_summary",
            localities=[],
            is_valid=False,
            rejection_reason="Query exceeds maximum allowed length of 250 characters."
        )

    # Prompt injection protection check
    lower_query = cleaned_query.lower()
    if any(keyword in lower_query for keyword in PROMPT_INJECTION_KEYWORDS):
        logger.warning(f"Security Alert: Malicious prompt injection attempt detected: \x27{cleaned_query[:50]}\x27")
        return StructuredQuery(
            operation="locality_summary",
            localities=[],
            is_valid=False,
            rejection_reason="Query rejected for security reasons. Malicious code execution or prompt injection is strictly prohibited."
        )

    # If a mock provider is passed (e.g. during Pytest/Evals), use it
    if mock_provider is not None:
        try:
            raw_result = mock_provider.parse(cleaned_query)
            struct = _validate_raw_dict(raw_result)
            if not struct.is_valid:
                fallback_struct = parse_query_rule_based(cleaned_query)
                return fallback_struct if fallback_struct.is_valid else struct
            return struct
        except Exception as e:
            logger.warning(f"Mock provider error: {e}. Falling back to rule-based parser.")
            return parse_query_rule_based(cleaned_query)

    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if provider == "gemini" and gemini_key:
        try:
            struct = _call_gemini_api(cleaned_query, gemini_key)
            return struct
        except Exception as e:
            logger.warning(f"Gemini API error: {e}. Falling back to rule-based parser.")
            return parse_query_rule_based(cleaned_query)
    elif provider == "openai" and openai_key:
        try:
            struct = _call_openai_api(cleaned_query, openai_key)
            return struct
        except Exception as e:
            logger.warning(f"OpenAI API error: {e}. Falling back to rule-based parser.")
            return parse_query_rule_based(cleaned_query)
    elif provider == "groq" and groq_key:
        try:
            struct = _call_groq_api(cleaned_query, groq_key)
            return struct
        except Exception as e:
            logger.warning(f"Groq API error: {e}. Falling back to rule-based parser.")
            return parse_query_rule_based(cleaned_query)

    # Default: Fallback to rule-based parser if no API key is available
    return parse_query_rule_based(cleaned_query)


def _validate_raw_dict(raw_dict: Dict[str, Any]) -> StructuredQuery:
    try:
        return StructuredQuery(**raw_dict)
    except Exception as e:
        return StructuredQuery(
            operation="locality_summary",
            localities=[],
            is_valid=False,
            rejection_reason=f"LLM output schema validation failed: {str(e)}"
        )


def _call_gemini_api(query: str, api_key: str) -> StructuredQuery:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    system_prompt = (
        f"You are a real estate query parser. Extract structured parameters for querying Pune real estate data.\n"
        f"Allowed Localities: {ALLOWED_LOCALITIES}\n"
        f"Allowed Operations: {ALLOWED_OPERATIONS}\n"
        f"Allowed Metrics: {ALLOWED_METRICS}\n"
        f"Respond ONLY with a JSON object matching this schema:\n"
        f"{{\"operation\": \"...\", \"metric\": \"...\", \"localities\": [...], \"start_year\": 2020, \"end_year\": 2024, \"group_by\": \"year\"}}"
    )
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_prompt}\nUser Query: {query}"}]}
        ],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    res_json = resp.json()
    text = res_json["candidates"][0]["content"]["parts"][0]["text"]
    raw_dict = json.loads(text)
    return _validate_raw_dict(raw_dict)


def _call_openai_api(query: str, api_key: str) -> StructuredQuery:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system_prompt = (
        f"Extract structured parameters for Pune real estate query.\n"
        f"Allowed Localities: {ALLOWED_LOCALITIES}\n"
        f"Allowed Operations: {ALLOWED_OPERATIONS}\n"
        f"Allowed Metrics: {ALLOWED_METRICS}\n"
        f"Respond ONLY with valid JSON."
    )
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "response_format": {"type": "json_object"}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    raw_dict = json.loads(text)
    return _validate_raw_dict(raw_dict)


def _call_groq_api(query: str, api_key: str) -> StructuredQuery:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"Extract JSON matching Pune localities {ALLOWED_LOCALITIES}."},
            {"role": "user", "content": query}
        ],
        "response_format": {"type": "json_object"}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    raw_dict = json.loads(text)
    return _validate_raw_dict(raw_dict)

