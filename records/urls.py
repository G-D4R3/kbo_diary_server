from django.urls import path
from rest_framework.routers import SimpleRouter

from records.views import TeamSelectAPIView, RecordRetrieveAPIView, RecordMemoAPIView, CalendarView, \
    RecordExistCheckView, RecordDeleteView

app_name = 'records'

router = SimpleRouter()

urlpatterns = [
    path("team_select/", TeamSelectAPIView.as_view(), name="team_select"),
    path("record/", RecordRetrieveAPIView.as_view(), name="record"),
    path("record/exists/", RecordExistCheckView.as_view(), name="record_exists_check"),
    path("record/delete/", RecordDeleteView.as_view(), name="record_delete"),
    path("memo/", RecordMemoAPIView.as_view(), name="memo"),
    path("calendar/", CalendarView.as_view(), name="calendar")
]
