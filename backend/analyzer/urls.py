from django.urls import path


from analyzer.views.analyze_view import AnalyzeView

urlpatterns = [
    
    path("analyze/", AnalyzeView.as_view(), name="analyze"),
]
