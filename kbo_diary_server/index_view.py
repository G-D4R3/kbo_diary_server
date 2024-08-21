import datetime

from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from rest_framework.request import Request

from records.service import RecordService


def index(request: Request):
    date = request.GET.get('date')
    if date is None:
        date = datetime.date.today().strftime('%Y-%m')

    return redirect(f'/api/records/calendar?date={date}')
