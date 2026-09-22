"""
API Views for Real Estate Insights.
Provides POST /api/analyze/ and GET /api/health/ endpoints.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from .llm_parser import parse_query_with_llm
from .session import process_follow_up
from .executor import execute_query
from .utils import make_json_safe, cache_get, cache_set
from .excel_loader import df

logger = logging.getLogger("real_estate_insights")


@api_view(["POST"])
def analyze_query(request):
    raw_query = request.data.get("query", "").strip()
    session_id = request.data.get("session_id", "default_session")

    if not raw_query:
        return Response({
            "summary": "Please send a valid query (e.g., \x27Analyze Wakad\x27 or \x27Compare Wakad and Aundh\x27).",
            "chart": [],
            "tables": {},
            "areas": []
        }, status=status.HTTP_400_BAD_REQUEST)

    if len(raw_query) > 250:
        return Response({
            "summary": "Query exceeds maximum allowed length of 250 characters.",
            "chart": [],
            "tables": {},
            "areas": []
        }, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f"{session_id}:{raw_query.lower()}"
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Serving cached query result for: \x27{raw_query}\x27")
        return Response(cached)

    # Allow mock provider via request header/context for testing
    mock_provider = getattr(request, "_mock_provider", None)

    # 1. Parse query cleanly
    query_struct = parse_query_with_llm(raw_query, mock_provider=mock_provider)

    # 2. Process session follow-up logic
    query_struct = process_follow_up(session_id, raw_query, query_struct)

    # 3. Execute query with Pandas
    result = execute_query(query_struct)

    json_safe_result = make_json_safe(result)
    cache_set(cache_key, json_safe_result)

    return Response(json_safe_result, status=status.HTTP_200_OK)


@api_view(["GET"])
def health_check(request):
    is_loaded = not df.empty
    row_count = len(df) if is_loaded else 0
    areas = list(df["final location"].unique()) if is_loaded and "final location" in df.columns else []

    return Response({
        "status": "healthy",
        "dataset_loaded": is_loaded,
        "row_count": row_count,
        "available_areas": areas,
        "version": "2.0.0"
    }, status=status.HTTP_200_OK)

