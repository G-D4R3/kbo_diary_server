import datetime

from django.shortcuts import render, redirect
from rest_framework.request import Request


def index(request: Request):
    if request.user.is_authenticated:
        date_str = datetime.date.today().strftime('%Y-%m')
        return redirect(to=f'/api/records/calendar/?date={date_str}')
    return render(request, 'main.html')
