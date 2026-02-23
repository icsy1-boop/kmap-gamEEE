from rest_framework import serializers
from .models import User, DailyChallenge, DailyChallengeResult, TimeAttackResult


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class DailyChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyChallenge
        fields = '__all__'


class DailyChallengeResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyChallengeResult
        fields = '__all__'


class TimeAttackResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeAttackResult
        fields = '__all__'
        