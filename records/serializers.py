from rest_framework import serializers

from kbo.models import Team
from records.models import Record


class TeamSelectSerializer(serializers.Serializer):
    team_full_name = serializers.CharField()
    g_id = serializers.CharField()


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('full_name', 'name',)


class RecordRetrieveSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Record
        fields = ('id', 'g_id', 'date', 'result', 'memo', 'team',)
