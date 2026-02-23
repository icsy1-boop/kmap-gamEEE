from django.urls import path
from .views import (
    CheckUser, CheckAnswer, FinishTimedChallenge, GetDailyChallenge, 
    GetDailyChallengeLeaderboard, StartTimeAttack, CheckTimeAttackAnswer, 
    FinishTimeAttack, GetTimeAttackLeaderboard
)

urlpatterns = [
    path('user', CheckUser.as_view(), name='check-user'),
    path('game', CheckAnswer.as_view(), name='check-answer'),
    path('finish-timed', FinishTimedChallenge.as_view(), name='finish-timed'),
    path('daily-challenge', GetDailyChallenge.as_view(), name='get-daily-challenge'),
    path('daily-leaderboard', GetDailyChallengeLeaderboard.as_view(), name='get-daily-leaderboard'),
    path('start-time-attack', StartTimeAttack.as_view(), name='start-time-attack'),
    path('check-time-attack', CheckTimeAttackAnswer.as_view(), name='check-time-attack'),
    path('finish-time-attack', FinishTimeAttack.as_view(), name='finish-time-attack'),
    path('time-attack-leaderboard', GetTimeAttackLeaderboard.as_view(), name='get-time-attack-leaderboard'),
]
