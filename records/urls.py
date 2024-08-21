from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import TeamSelectAPIView, RecordRetrieveAPIView, RecordMemoAPIView, CalendarView

app_name = 'records'

router = SimpleRouter()

urlpatterns = [
    path("team_select/", TeamSelectAPIView.as_view(), name="team_select"),
    path("record/", RecordRetrieveAPIView.as_view(), name="record"),
    path("memo/", RecordMemoAPIView.as_view(), name="memo"),
    path("calendar/", CalendarView.as_view(), name="calendar")
]
