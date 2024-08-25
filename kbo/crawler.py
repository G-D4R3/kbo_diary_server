import datetime
import json

import pandas as pd
import requests

from kbo.models import Team
from records.serializers import TeamSerializer


class GameListRequestError(Exception):

    def __init__(self, message):
        self.message = message


class KBOService:

    def retrieve_by_name(self, team_name):
        team = Team.objects.get(name=team_name)
        serializer = TeamSerializer(team)
        return serializer.data


class KBODataCrawler:
    AWAY_IDX = 0
    HOME_IDX = 1

    GAME_LIST_URL = 'https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList'
    SCORE_BOARD_URL = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll'
    BOX_SCORE_URL = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll'

    @classmethod
    def get_score_board_raw_data(cls, g_id):
        s_id = g_id[0:4]
        post_data = dict(
            seasonId=s_id,
            gameId=g_id,
            leId=1,
            srId=0
        )
        raw_data = requests.post(cls.SCORE_BOARD_URL, post_data).json()
        return raw_data

    @classmethod
    def get_player_raw_data(cls, g_id):
        s_id = g_id[0:4]
        post_data = dict(
            seasonId=s_id,
            gameId=g_id,
            leId=1,
            srId=0
        )
        raw_data = requests.post(cls.BOX_SCORE_URL, post_data).json()
        return raw_data

    @classmethod
    def get_game_list_raw_data(cls, date: str):
        leId = 1
        srId = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        data = dict(
            date=date,
            leId=leId,
            srId=srId
        )

        raw_data = requests.post(
            url=cls.GAME_LIST_URL,
            data=data
        ).json()

        if raw_data.get('msg') != '성공':
            raise GameListRequestError('게임을 불러오는데에 실패했습니다.')

        return raw_data.get('game')

    def get_game_list(self, date: str):
        raw_data = self.get_game_list_raw_data(date)
        kbo_service = KBOService()
        data = []
        for game_data in raw_data:
            away_team_data = kbo_service.retrieve_by_name(game_data['AWAY_NM'])
            home_team_data = kbo_service.retrieve_by_name(game_data['HOME_NM'])

            data.append(dict(
                common=dict(
                    g_id=game_data['G_ID'],
                    g_tm=game_data['G_TM'],
                    s_nm=game_data['S_NM'],
                    cancel_sc_nm=game_data['CANCEL_SC_NM'],
                    game_sc_nm=game_data['GAME_SC_NM'],
                    game_state_sc=game_data['GAME_STATE_SC']
                ),
                away=dict(
                    name=game_data['AWAY_NM'],
                    starting_pitcher=game_data['T_PIT_P_NM'],
                    result_score=int(game_data['T_SCORE_CN']),
                    result=game_result(int(game_data['T_SCORE_CN']), int(game_data['B_SCORE_CN'])),
                    logo=away_team_data.get('logo')
                ),
                home=dict(
                    name=game_data['HOME_NM'],
                    starting_pitcher=game_data['B_PIT_P_NM'],
                    result_score=int(game_data['B_SCORE_CN']),
                    result=game_result(int(game_data['B_SCORE_CN']), int(game_data['T_SCORE_CN'])),
                    logo=home_team_data.get('logo')
                )
            ))
        return data

    def get_game_data(self, g_id: str):
        score_board_raw_data = self.get_score_board_raw_data(g_id)
        player_raw_data = self.get_player_raw_data(g_id)

        score_data = self.get_score_data(score_board_raw_data)
        hitter_data = self.get_hitter_data(player_raw_data)
        pitcher_data = self.get_pitcher_data(player_raw_data)

        away_data = dict(
            name=score_board_raw_data['AWAY_NM'],
            full_name=score_board_raw_data['FULL_AWAY_NM'],
            result_score=int(score_board_raw_data['T_SCORE_CN']),
            result=score_data['away']['result'],
            scores=score_data['away']['scores'],
            stats=score_data['away']['stats'],
            hitters=hitter_data['away'],
            pitchers=pitcher_data['away']
        )

        home_data = dict(
            name=score_board_raw_data['HOME_NM'],
            full_name=score_board_raw_data['FULL_HOME_NM'],
            result_score=int(score_board_raw_data['B_SCORE_CN']),
            result=score_data['home']['result'],
            scores=score_data['home']['scores'],
            stats=score_data['home']['stats'],
            hitters=hitter_data['home'],
            pitchers=pitcher_data['home']
        )

        away_team = Team.objects.get(full_name=away_data['full_name'])
        home_team = Team.objects.get(full_name=home_data['full_name'])

        away_data['logo'] = away_team.logo.url
        home_data['logo'] = home_team.logo.url
        away_data['initial_logo'] = away_team.initial_logo.url
        home_data['initial_logo'] = home_team.initial_logo.url

        data = dict(
            common=dict(
                g_id=g_id,
                date=g_id[0:8]
            ),
            away=away_data,
            home=home_data
        )

        return data

    def make_game_summary_data(self, raw_data):
        home_name = raw_data['HOME_NM']
        away_name = raw_data['AWAY_NM']
        home = Team.objects.get(name=home_name)
        away = Team.objects.get(name=away_name)

        res = dict(
            home=dict(
                full_name=raw_data['FULL_HOME_NM'],
                name=raw_data['HOME_NM'],
                score=int(raw_data['B_SCORE_CN']),
                logo=home.logo.url,
                initial_logo=home.initial_logo.url
            ),
            away=dict(
                full_name=raw_data['FULL_AWAY_NM'],
                name=raw_data['AWAY_NM'],
                score=int(raw_data['T_SCORE_CN']),
                logo=away.logo.url,
                initial_logo=away.initial_logo.url
            )
        )
        return res

    def get_score_data(self, raw_data):
        game_results = json.loads(raw_data.get('table1')).get('rows')
        away_raw_data = game_results[self.AWAY_IDX].get('row')[0]
        home_raw_data = game_results[self.HOME_IDX].get('row')[0]

        away_game_result = away_raw_data.get('Text')
        home_game_result = home_raw_data.get('Text')

        scores = json.loads(raw_data.get('table2')).get('rows')

        away_scores = [row.get('Text') for row in scores[self.AWAY_IDX].get('row')]
        home_scores = [row.get('Text') for row in scores[self.HOME_IDX].get('row')]

        stats = json.loads(raw_data.get('table3')).get('rows')
        stats_col = ["R", "H", "E", "B"]
        away_stats, home_stats = dict(), dict()
        for idx, row in enumerate(stats_col):
            away_stats[row] = stats[self.AWAY_IDX].get('row')[idx]['Text']
            home_stats[row] = stats[self.HOME_IDX].get('row')[idx]['Text']

        result = dict(
            away=dict(
                result=away_game_result,
                scores=away_scores,
                stats=away_stats
            ),
            home=dict(
                result=home_game_result,
                scores=home_scores,
                stats=home_stats
            )
        )
        return result

    def get_hitter_data(self, player_raw_data):
        hitter = player_raw_data.get('arrHitter')
        away_hitter_data = self._get_hitter_data(hitter, self.AWAY_IDX)
        home_hitter_data = self._get_hitter_data(hitter, self.HOME_IDX)

        result = dict(
            away=away_hitter_data,
            home=home_hitter_data
        )
        return result

    def _get_hitter_data(self, hitter_data, team_index):
        hitters = hitter_data[team_index]
        players = [
            dict(
                number=hitter['row'][0]['Text'],  # 타순
                position=hitter['row'][1]['Text'],  # 포지션
                name=hitter['row'][2]['Text']) for  # 선수 이름
            hitter in json.loads(hitters['table1'])['rows']]
        stats = [dict(
            PA=hitter['row'][0]['Text'],  # 타석
            H=hitter['row'][1]['Text'],  # 안타
            RBI=hitter['row'][2]['Text'],  # 타점
            R=hitter['row'][3]['Text']  # 득점
        ) for hitter in json.loads(hitters['table3'])['rows']]
        hitter_data = []
        for player, stats in zip(players, stats):
            combined_dict = {**player, **stats}
            hitter_data.append(combined_dict)

        return hitter_data

    def get_pitcher_data(self, player_raw_data):
        pitcher = player_raw_data.get('arrPitcher')
        away_pitcher = json.loads(pitcher[self.AWAY_IDX]['table'])['rows']
        away_pitcher_players = [dict(
            name=player['row'][0]['Text'],
            IP=player['row'][6]['Text'],  # 이닝
            NP=player['row'][8]['Text'],  # 투구수
            H=player['row'][10]['Text'],  # 피안타
            HR=player['row'][11]['Text'],  # 피홈런
            BB=player['row'][12]['Text'],  # 4사구
            SO=player['row'][13]['Text'],  # 삼진
            R=player['row'][14]['Text'],  # 실점
            ER=player['row'][15]['Text']  # 자책점
        ) for player in away_pitcher]

        home_pitcher = json.loads(pitcher[self.HOME_IDX]['table'])['rows']
        home_pitcher_players = [dict(
            name=player['row'][0]['Text'],
            IP=player['row'][6]['Text'],  # 이닝
            NP=player['row'][8]['Text'],  # 투구수
            H=player['row'][10]['Text'],  # 피안타
            HR=player['row'][11]['Text'],  # 피홈런
            BB=player['row'][12]['Text'],  # 4사구
            SO=player['row'][13]['Text'],  # 삼진
            R=player['row'][14]['Text'],  # 실점
            ER=player['row'][15]['Text']  # 자책점

        ) for player in home_pitcher]

        pitcher_data = dict(
            away=away_pitcher_players,
            home=home_pitcher_players
        )
        return pitcher_data


def game_result(score_a, score_b):
    return '승' if score_a > score_b else '패' if score_a < score_b else '무'
