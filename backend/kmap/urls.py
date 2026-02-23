from django.urls import path
from .views import CheckUser, CheckAnswer, FinishTimedChallenge, GetDailyChallenge, GetDailyChallengeLeaderboard

urlpatterns = [
    path('user', CheckUser.as_view(), name='check-user'),
    path('game', CheckAnswer.as_view(), name='check-answer'),
    path('finish-timed', FinishTimedChallenge.as_view(), name='finish-timed'),
    path('daily-challenge', GetDailyChallenge.as_view(), name='get-daily-challenge'),
    path('daily-leaderboard', GetDailyChallengeLeaderboard.as_view(), name='get-daily-leaderboard'),
]
