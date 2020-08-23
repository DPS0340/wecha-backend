from django.urls import path

from .views import (
    FilmRankingView,
    FilmDetailView,
    FilmRecommendationView
)

app_name = 'film'

urlpatterns = [
    path('ranking', FilmRankingView.as_view(), name="ranking"),
    path('<int:film_id>', FilmDetailView.as_view(), name="detail"),
    path('recommendation', FilmRecommendationView.as_view(), name="recommendation")
]