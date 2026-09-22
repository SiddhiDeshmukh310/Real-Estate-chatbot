"""
URL routing for api app (supports paths with and without trailing slashes).
"""

from django.urls import path
from .views import analyze_query, health_check

urlpatterns = [
    path("analyze/", analyze_query, name="analyze_query"),
    path("analyze", analyze_query),
    path("health/", health_check, name="health_check"),
    path("health", health_check),
]

