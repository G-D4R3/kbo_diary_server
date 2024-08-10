from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from records.service import RecordService


# Create your views here.
class TeamSelectAPIView(APIView):

    def get(self, request, *args, **kwargs):
        game_id = request.query_params.get('g_id')
        if game_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        season_id = game_id[0:4]
        service = RecordService()
        data = service.get_team_choices(season_id, game_id)
        return render(request, 'team_choices.html', data)


    def post(self, request, *args, **kwargs):
        pass