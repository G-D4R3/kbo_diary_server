from django.urls import path
from rest_framework.routers import SimpleRouter

from kbo.views import GameListAPIView, GameDataAPIView

app_name = 'kbo'

router = SimpleRouter()

urlpatterns = [
    path("games/", GameListAPIView.as_view(), name="game_list"),
    path("game_data/", GameDataAPIView.as_view(), name="game_data"),
]
