from django.urls import path

from analyzer.views.analyze_view import AnalyzeView
from analyzer.views.health_view import health

urlpatterns = [
    path("analyze/", AnalyzeView.as_view(), name="analyze"),
    path("health/", health, name="health"),
]
