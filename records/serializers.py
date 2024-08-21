from rest_framework import serializers

from kbo.models import Team
from records.models import Record


class TeamSelectSerializer(serializers.Serializer):
    team_full_name = serializers.CharField()
    g_id = serializers.CharField()


class TeamSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    initial_logo = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('full_name', 'name', 'logo', 'initial_logo',)

    def get_logo(self, obj):
        return obj.logo.url

    def get_initial_logo(self, obj):
        return obj.initial_logo.url


class RecordRetrieveSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Record
        fields = ('id', 'g_id', 'date', 'result', 'memo', 'team',)


class RecordSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'date', 'g_id', 'result',)