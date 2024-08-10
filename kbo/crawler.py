import datetime
import json

import pandas as pd
import requests


class KBODataCrawler:
    AWAY_IDX = 0
    HOME_IDX = 1

    GAME_LIST_URL = 'https://www.koreabaseball.com/ws/Main.asmx/GetKboGameList'
    SCORE_BOARD_URL = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll'
    BOX_SCORE_URL = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll'

    def get_game_list(self, date: str):
        leId = 1
        srId = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        data = dict(
            date=date,
            leId=leId,
            srId=srId
        )

        res = requests.post(
            url=self.GAME_LIST_URL,
            data=data
        )

        game_list = res.json().get('game')
        columns = [
            'G_ID',  # game id
            'G_TM',  # game start time
            'S_NM',  # stadium name
            'AWAY_NM',  # away team name
            'HOME_NM',  # home team name
            'T_PIT_P_NM',  # away team starting pitcher
            'B_PIT_P_NM',  # home team starting pitcher
            'CANCEL_SC_NM',  # 경기 취소 사유
            'GAME_SC_NM'  # 시즌 이름
        ]
        df_game = pd.DataFrame(game_list, columns=columns)
        for column in columns:
            df_game[column] = df_game[column].str.strip()
        data = df_game.to_dict(orient="records")

        return data

    def get_game_data(self, s_id: str, g_id: str):
        post_data = dict(
            seasonId=s_id,
            gameId=g_id,
            leId=1,
            srId=0
        )

        score_board_raw_data = requests.post(self.SCORE_BOARD_URL, post_data).json()
        player_raw_data = requests.post(self.BOX_SCORE_URL, post_data).json()

        game_summary = self.make_game_summary_data(score_board_raw_data)
        score_data = self.get_score_data(score_board_raw_data)
        hitter_data = self.get_hitter_data(player_raw_data)
        pitcher_data = self.get_pitcher_data(player_raw_data)

        return dict(
            home=dict(
                summary=game_summary['home'],
                score=score_data['home'],
                hitter=hitter_data['home'],
                pitcher=pitcher_data['home']
            ),
            away=dict(
                summary=game_summary['away'],
                score=score_data['away'],
                hitter=hitter_data['away'],
                pitcher=pitcher_data['away']
            )
        )


    def make_game_summary_data(self, raw_data):
        res = dict(
            home=dict(
                full_name=raw_data['FULL_HOME_NM'],
                name=raw_data['HOME_NM'],
                score=raw_data['T_SCORE_CN']
            ),
            away=dict(
                full_name=raw_data['FULL_AWAY_NM'],
                name=raw_data['AWAY_NM'],
                score=raw_data['T_SCORE_CN']
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