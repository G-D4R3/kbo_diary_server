import requests

from kbo.crawler import KBODataCrawler


class RecordService:

    def get_team_choices(self, s_id: str, g_id: str):
        post_data = dict(
            seasonId=s_id,
            gameId=g_id,
            leId=1,
            srId=0
        )
        crawler = KBODataCrawler()
        score_board_raw_data = requests.post(crawler.SCORE_BOARD_URL, post_data).json()
        summary = crawler.make_game_summary_data(score_board_raw_data)
        summary['g_id'] = g_id
        return summary