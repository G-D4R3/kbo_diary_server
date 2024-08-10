from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from kbo.crawler import KBODataCrawler


# Create your views here.
class GameListAPIView(ListAPIView):
    queryset = ''
    serializer_class = None

    def list(self, request, *args, **kwargs):
        game_date = request.query_params.get('date')
        crawler = KBODataCrawler()
        data = crawler.get_game_list(game_date)
        results = dict(
            games=data,
            date=game_date
        )

        return render(
            request=request,
            template_name='game_list.html',
            context=results
        )

class GameDataAPIView(RetrieveAPIView):
    queryset = ''
    serializer_class = None

    def get(self, request, *args, **kwargs):
        game_id = request.query_params.get('g_id')
        if game_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        season_id = game_id[0:4]

        crawler = KBODataCrawler()
        data = crawler.get_game_data(season_id, game_id)

        return render(request=request, template_name='game_data.html', context=data)

