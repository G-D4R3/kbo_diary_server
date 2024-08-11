import requests

from kbo.crawler import KBODataCrawler
from records.models import Record
from records.serializers import RecordRetrieveSerializer


class RecordService:

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