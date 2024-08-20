import datetime

from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from rest_framework.request import Request

from records.service import RecordService


def calendar(request: Request):
    user = request.user

    date_str = request.GET.get('date')
    if date_str is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    month_first_day = datetime.date(date.year, date.month, 1)
    year_first_day = datetime.date(date.year, 1, 1)
    last_day = month_first_day + relativedelta(months=1) - datetime.timedelta(days=1)

    service = RecordService(user=user)
    monthly_winning_rate = service.winning_rate(start=month_first_day, end=last_day)
    season_winning_rate = service.winning_rate(start=year_first_day, end=last_day)
    data = dict(
        season_winning_rate=season_winning_rate,
        monthly_winning_rate=monthly_winning_rate
    )

    return render(request, 'calendar.html', context=data)
