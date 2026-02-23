from django.db import models
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=50)
    score = models.IntegerField()
    difficulty = models.IntegerField()

    q_num_var = models.IntegerField()
    q_form = models.CharField(max_length=5)
    q_terms = models.JSONField()
    q_dont_cares = models.JSONField()
    q_groupings = models.JSONField()
    
    time_started = models.DateTimeField(null=True, blank=True)
    time_completed = models.DateTimeField(null=True, blank=True)


class DailyChallenge(models.Model):
    date = models.DateField(unique=True)
    num_var = models.IntegerField()
    form = models.CharField(max_length=5)
    terms = models.JSONField()
    dont_cares = models.JSONField()
    groupings = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Daily Challenge - {self.date}"


class DailyChallengeResult(models.Model):
    username = models.CharField(max_length=50)
    daily_challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='results')
    completion_time_seconds = models.IntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completion_time_seconds']
        unique_together = ('username', 'daily_challenge')

    def __str__(self):
        return f"{self.username} - {self.daily_challenge.date}"


class TimeAttackResult(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]
    
    username = models.CharField(max_length=50)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    questions_solved = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-questions_solved', 'created_at']

    def __str__(self):
        return f"{self.username} - {self.get_difficulty_display()} - {self.questions_solved} solved"
