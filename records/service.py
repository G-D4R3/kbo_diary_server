import datetime
import requests
from django.contrib.auth.models import User
from django.db.models import Q

from kbo.crawler import KBODataCrawler
from kbo.models import Team
from records.models import Record
from records.serializers import RecordRetrieveSerializer


class RecordService:

    def __init__(self, user: User = None):
        self._user = user

    def get_team_choices(self, s_id: str, g_id: str):
        post_data = dict(
            seasonId=s_id,
            gameId=g_id,
            leId=1,
            srId=0
        )
        crawler = KBODataCrawler()
        raw_data = requests.post(crawler.SCORE_BOARD_URL, post_data).json()
        summary = crawler.make_game_summary_data(raw_data)

        summary['g_id'] = g_id
        summary['date'] = g_id[0:8]
        return summary

    def retrieve(self, id):
        record = self._retrieve(id)
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

    @property
    def user(self):
        return self._user
