import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from kbo.crawler import KBODataCrawler
from kbo.models import Team
from records.models import Record
from records.serializers import TeamSelectSerializer
from records.service import RecordService


# Create your views here.
class TeamSelectAPIView(APIView):
    serializer_class = TeamSelectSerializer

    def get(self, request, *args, **kwargs):
        game_id = request.query_params.get('g_id')
        if game_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        service = RecordService()
        data = service.get_team_choices(game_id)
        context = dict(
            results=data
        )
        return render(request, 'team_choices.html', context)

    def post(self, request, *args, **kwargs):
        # user = request.user
        user = User.objects.get(email='gdare1999@gmail.com')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        team_full_name = serializer.validated_data.get('team_full_name')
        g_id = serializer.validated_data.get('g_id')
        date_str = g_id[0:8]
        date = datetime.date.fromisoformat(date_str)

        # team의 승리 정보를 불러옴
        raw_data = KBODataCrawler.get_score_board_raw_data(g_id)
        score = dict()
        score[raw_data['FULL_AWAY_NM']] = 'W' if raw_data['T_SCORE_CN'] > raw_data['B_SCORE_CN'] else 'L' if raw_data[
                                                                                                                 'T_SCORE_CN'] < \
                                                                                                             raw_data[
                                                                                                                 'B_SCORE_CN'] else 'D'
        score[raw_data['FULL_HOME_NM']] = 'W' if raw_data['B_SCORE_CN'] > raw_data['T_SCORE_CN'] else 'L' if raw_data[
                                                                                                                 'B_SCORE_CN'] < \
                                                                                                             raw_data[
                                                                                                                 'T_SCORE_CN'] else 'D'

        team = Team.objects.get(full_name=team_full_name)
        try:
            record = Record.objects.get(
                date=date,
                user=user
            )
            record.team = team
            record.g_id = g_id
            record.result = score[team_full_name]
            record.save()
        except Record.DoesNotExist:
            record = Record.objects.create(
                date=date,
                user=user,
                team=team,
                g_id=g_id,
                result=score[team_full_name]
            )
        redirect_url = f'/api/records/record?id={record.id}'
        return redirect(redirect_url)


class RecordRetrieveAPIView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        try:
            date = datetime.datetime.fromisoformat(request.query_params.get('date')).date()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            # todo: user = request.user
            record = Record.objects.get(date=date)
        except Record.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        game_id = record.g_id
        crawler = KBODataCrawler()
        service = RecordService()
        game_data = crawler.get_game_data(game_id)
        record_data = service.retrieve_by_date(date)
        data = dict(
            record=record_data,
            game=game_data
        )

        return render(request=request, template_name='record.html', context=data)


class RecordMemoAPIView(APIView):

    def get(self, request, *args, **kwargs):
        record_id = int(request.query_params.get('id'))
        service = RecordService()
        data = service.retrieve(record_id)

        return render(request, 'record_memo.html', context=data)

    def post(self, request, *args, **kwargs):
        record_id = int(request.query_params.get('id'))
        memo = request.data.get('memo')

        service = RecordService()
        service.memo(record_id, memo)

        redirect_url = f'/api/records/record/?id={record_id}'
        return redirect(redirect_url)


class CalendarView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user

        date_str = request.GET.get('date')
        cur_year = int(date_str.split('-')[0])
        cur_month = int(date_str.split('-')[1])

        month_first_day = datetime.date(cur_year, cur_month, 1)
        year_first_day = datetime.date(cur_year, 1, 1)
        last_day = month_first_day + relativedelta(months=1) - datetime.timedelta(days=1)

        service = RecordService(user=user)
        try:
            monthly_winning_rate = service.winning_rate(start=month_first_day, end=last_day)
        except ZeroDivisionError:
            monthly_winning_rate = None
        try:
            season_winning_rate = service.winning_rate(start=year_first_day, end=last_day)
        except ZeroDivisionError:
            season_winning_rate = None

        records = service.record_summaries(start=month_first_day, end=last_day)

        data = dict(
            season_winning_rate=season_winning_rate,
            monthly_winning_rate=monthly_winning_rate,
            records=records
        )
        context = dict(results=data)

        return render(request=request, template_name='calendar.html', context=context)


class RecordExistCheckView(APIView):

    def get(self, request, *args, **kwargs):
        date_str = request.GET.get('date')
        date = datetime.datetime.fromisoformat(date_str).date()
        # user = request.user

        try:
            if not Record.objects.filter(date=date).exists():
                raise Record.DoesNotExist
            # Record.objects.get(user=user, date=date)
            return Response(dict(results={"is_exist": True}))
        except Record.DoesNotExist:
            return Response(dict(results={"is_exist": False}))

