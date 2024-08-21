import datetime
import requests
from django.contrib.auth.models import User
from django.db.models import Q

from kbo.crawler import KBODataCrawler
from kbo.models import Team
from records.models import Record
from records.serializers import RecordRetrieveSerializer, RecordSummarySerializer


class RecordService:

    def __init__(self, user: User = None):
        self._user = user

    def get_team_choices(self, g_id: str):
        crawler = KBODataCrawler()
        raw_data = crawler.get_score_board_raw_data(g_id)

        home_name = raw_data['HOME_NM']
        away_name = raw_data['AWAY_NM']
        home = Team.objects.get(name=home_name)
        away = Team.objects.get(name=away_name)

        data = dict(
            common=dict(
                g_id=g_id,
                date=g_id[0:8]
            ),
            away=dict(
                full_name=away.full_name,
                name=away.name,
                logo=away.logo.url
            ),
            home=dict(
                full_name=home.full_name,
                name=away.name,
                logo=home.logo.url
            )
        )
        return data

    def retrieve(self, id):
        record = self._retrieve(id)
        serializer = RecordRetrieveSerializer(record)
        return serializer.data

    def retrieve_by_date(self, date: datetime.date):
        # todo: user = self.user
        record = Record.objects.filter(date=date).first()
        serializer = RecordRetrieveSerializer(record)
        return serializer.data

    def _retrieve(self, id):
        record = Record.objects.get(id=id)
        return record

    def memo(self, id, memo) -> Record:
        record = self._retrieve(id)
        record.memo = memo
        record.save()

        return record

    def winning_rate(self, start: datetime.date, end: datetime.date) -> int:
        user = self.user
        records = Record.objects.filter(  # todo: user filter
            date__gte=start, date__lte=end
        ).filter(
            ~Q(result='D')
        )
        game_count = records.count()
        won_game_count = records.filter(result='W').count()
        winning_rate = int((won_game_count / game_count) * 100)

        return winning_rate


    def record_summaries(self, start: datetime.date, end: datetime.date):
        # user = self.user
        records = Record.objects.filter(  # todo: user filter
            date__gte=start, date__lte=end
        )
        serializer = RecordSummarySerializer(records, many=True)

        return serializer.data



    @property
    def user(self):
        return self._user
