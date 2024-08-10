from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import TeamSelectAPIView

app_name = 'records'

router = SimpleRouter()

urlpatterns = [
    path("team_select/", TeamSelectAPIView.as_view(), name="team_select"),
]
