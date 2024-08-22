import datetime

from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from rest_framework.request import Request

from records.service import RecordService


def index(request: Request):
    if request.user:
        date_str = datetime.date.today().strftime('%Y-%m')
        return redirect(to=f'/api/records/calendar/?date={date_str}')
    return render(request, 'main.html')
