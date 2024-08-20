from django.urls import path
from rest_framework.routers import SimpleRouter

from kbo.views import GameListAPIView

app_name = 'kbo'

router = SimpleRouter()

urlpatterns = [
    path("games/", GameListAPIView.as_view(), name="game_list"),
]
