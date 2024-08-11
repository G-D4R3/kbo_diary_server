from django.contrib.auth.models import User
from django.db import models

WIN = 'W'
LOSE = 'L'
DRAW = 'D'

GAME_RESULTS = (
    (WIN, 'win'),
    (LOSE, 'lose'),
    (DRAW, 'draw'),
)


class Record(models.Model):
    date = models.DateField()
    g_id = models.CharField(help_text='kbo game id', max_length=30)
    result = models.CharField(max_length=5, choices=GAME_RESULTS)
    team = models.ForeignKey('kbo.Team', related_name='records', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='records', on_delete=models.CASCADE)
    memo = models.TextField(null=True, blank=True, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'user'], name='record user and date unique constraint')
        ]
