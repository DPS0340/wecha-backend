from django.urls import path

from .views import (
    FilmRankingByServiceProvierView,
    FilmDetailView
)

app_name = 'film'

urlpatterns = [
    path('ranking', FilmRankingByServiceProvierView.as_view(), name="ranking"),
    path('<int:film_id>', FilmDetailView.as_view(), name="detail"),
]