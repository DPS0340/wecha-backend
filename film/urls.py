from django.urls import path

from .views import FilmRankingView

app_name = 'film'

urlpatterns = [
    path('ranking', FilmRankingView.as_view(), name="ranking"),
]