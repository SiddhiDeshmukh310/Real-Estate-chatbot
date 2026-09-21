"""
URL routing for api app.
"""

from django.urls import path
from .views import analyze_query, health_check

urlpatterns = [
    path("analyze/", analyze_query, name="analyze_query"),
    path("health/", health_check, name="health_check"),
]

