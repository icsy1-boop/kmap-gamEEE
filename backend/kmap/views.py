from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, DailyChallenge, DailyChallengeResult
from .serializers import UserSerializer
from . import kmap_solver
from django.utils import timezone
from datetime import datetime
import pytz


def get_or_create_daily_challenge():
    """Get today's challenge or create a new one if it doesn't exist"""
    today = timezone.now().date()
    daily_challenge, created = DailyChallenge.objects.get_or_create(
        date=today,
        defaults={
            'num_var': 5,  # Default to harder difficulty
            'form': 'min',
            'terms': [],
            'dont_cares': [],
            'groupings': []
        }
    )
    
    if created:
        # Generate a new challenge for today
        num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=3)
        daily_challenge.num_var = num_var
        daily_challenge.form = form
        daily_challenge.terms = terms
        daily_challenge.dont_cares = dont_cares
        daily_challenge.groupings = groupings
        daily_challenge.save()
    
    return daily_challenge


class CheckUser(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        difficulty = request.data.get('difficulty')
        if difficulty == 'easy':
            difficulty = 1
        elif difficulty == 'medium':
            difficulty = 2
        elif difficulty == 'hard':
            difficulty = 3
        elif difficulty == 'timed':
            difficulty = 4
        else:
            difficulty = 5

        score = 0
        time_started = None

        if difficulty == 4:
            daily_challenge = get_or_create_daily_challenge()
            num_var = daily_challenge.num_var
            form = daily_challenge.form
            terms = daily_challenge.terms
            dont_cares = daily_challenge.dont_cares
            groupings = daily_challenge.groupings
            time_started = timezone.now()
        elif difficulty == 5:
            num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=1)
        else:
            num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=difficulty)
        
        user = User(username=username, score=score, difficulty=difficulty, q_num_var=num_var, q_form=form, q_terms=terms, q_dont_cares=dont_cares, q_groupings=groupings, time_started=time_started)
        serializer = UserSerializer(user)
        
        # For timed mode, ensure time_started is properly formatted as ISO string
        response_data = serializer.data
        if time_started:
            response_data['time_started'] = time_started.isoformat()
        
        return Response(response_data, status=status.HTTP_200_OK)
        
class CheckAnswer(APIView):
    # def get(self, request):
        
    def post(self, request):
        if request.data.get('type') == 0:
            username = request.data.get('user').get('username')
            score = request.data.get('user').get('score')
            difficulty = request.data.get('user').get('difficulty')
            num_var = request.data.get('user').get('q_num_var')
            form = request.data.get('user').get('q_form')
            terms = request.data.get('user').get('q_terms')
            dont_cares = request.data.get('user').get('q_dont_cares')
            groupings = request.data.get('user').get('q_groupings')
            answer = request.data.get('user').get('answer')
            result, answers = kmap_solver.minimizeAndCheck(
                num_var = num_var, 
                form_terms = form, 
                terms = terms, 
                dont_cares = dont_cares, 
                input_answer=answer)
            
            # For timed mode, record the completion time if answer is correct
            if difficulty == 4 and result == 1:
                time_started = request.data.get('user').get('time_started')
                if time_started:
                    try:
                        # Parse time_started properly
                        if isinstance(time_started, str):
                            # Remove 'Z' suffix if present and parse as ISO format
                            time_started_clean = time_started.replace('Z', '+00:00')
                            start_time = datetime.fromisoformat(time_started_clean)
                        else:
                            start_time = time_started
                        
                        # Make sure both times are timezone-aware for proper calculation
                        time_completed = timezone.now()
                        
                        # If start_time is naive, make it aware
                        if start_time.tzinfo is None:
                            start_time = pytz.UTC.localize(start_time)
                        
                        elapsed_seconds = max(0, int((time_completed - start_time).total_seconds()))
                        
                        # Get today's daily challenge
                        today = timezone.now().date()
                        daily_challenge = DailyChallenge.objects.get(date=today)
                        
                        # Record the result
                        DailyChallengeResult.objects.update_or_create(
                            username=username,
                            daily_challenge=daily_challenge,
                            defaults={
                                'completion_time_seconds': elapsed_seconds,
                                'completed_at': time_completed
                            }
                        )
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        pass  # Silently fail if recording time doesn't work
            
            return Response({'result': result, 'answers': answers}, status=status.HTTP_200_OK)
    
        else:
            username = request.data.get('user').get('username')
            score = request.data.get('user').get('score')
            difficulty = request.data.get('user').get('difficulty')
            result = request.data.get('user').get('result')
            time_started = request.data.get('user').get('time_started')
            
            if result == 1:
                score += 1
                if score >= 10 and difficulty == 5:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=3)
                elif score >= 5 and difficulty == 5:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=2)
                elif difficulty == 5:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=1)
                elif difficulty == 4:
                    # Timed mode: stay on the daily challenge, don't change questions
                    daily_challenge = get_or_create_daily_challenge()
                    num_var = daily_challenge.num_var
                    form = daily_challenge.form
                    terms = daily_challenge.terms
                    dont_cares = daily_challenge.dont_cares
                    groupings = daily_challenge.groupings
                else:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=difficulty)
            else:
                score = 0
                if difficulty == 5:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=1)
                elif difficulty == 4:
                    # Timed mode: stay on the daily challenge, don't change questions
                    daily_challenge = get_or_create_daily_challenge()
                    num_var = daily_challenge.num_var
                    form = daily_challenge.form
                    terms = daily_challenge.terms
                    dont_cares = daily_challenge.dont_cares
                    groupings = daily_challenge.groupings
                else:
                    num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=difficulty)
            
            user = User(username=username, score=score, difficulty=difficulty, q_num_var=num_var, q_form=form, q_terms=terms, q_dont_cares=dont_cares, q_groupings=groupings, time_started=time_started)
            serializer = UserSerializer(user)
            
            # Ensure time_started is properly formatted
            response_data = serializer.data
            if time_started and isinstance(time_started, str):
                response_data['time_started'] = time_started
            elif time_started:
                response_data['time_started'] = time_started.isoformat()
            
            return Response({'result': result, 'user': response_data}, status=status.HTTP_200_OK)


class FinishTimedChallenge(APIView):
    def post(self, request):
        username = request.data.get('username')
        score = request.data.get('score')
        difficulty = request.data.get('difficulty')
        elapsed_seconds = request.data.get('elapsed_seconds')
        
        if not username or difficulty != 4:
            return Response({'error': 'Invalid request for timed challenge'}, status=status.HTTP_400_BAD_REQUEST)
        
        if elapsed_seconds is None:
            return Response({'error': 'Elapsed time is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure elapsed_seconds is a positive integer
        try:
            elapsed_seconds = max(1, int(elapsed_seconds))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid elapsed_seconds format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get today's daily challenge
        today = timezone.now().date()
        try:
            daily_challenge = DailyChallenge.objects.get(date=today)
        except DailyChallenge.DoesNotExist:
            return Response({'error': 'Daily challenge not available'}, status=status.HTTP_404_NOT_FOUND)
        
        time_completed = timezone.now()
        
        # Check if user already has a valid completion for today (to prevent duplicates)
        existing_result = DailyChallengeResult.objects.filter(
            username=username,
            daily_challenge=daily_challenge
        ).first()
        
        # Only save if this is a new completion (not already completed)
        if not existing_result:
            DailyChallengeResult.objects.create(
                username=username,
                daily_challenge=daily_challenge,
                completion_time_seconds=elapsed_seconds,
                completed_at=time_completed,
                score=score
            )
        else:
            # User already completed, return their existing record
            elapsed_seconds = existing_result.completion_time_seconds
        
        # Get the leaderboard
        leaderboard = DailyChallengeResult.objects.filter(
            daily_challenge=daily_challenge
        ).order_by('completion_time_seconds').values('username', 'completion_time_seconds')[:10]
        
        # Find user's rank
        user_rank = DailyChallengeResult.objects.filter(
            daily_challenge=daily_challenge,
            completion_time_seconds__lt=elapsed_seconds
        ).count() + 1
        
        return Response({
            'username': username,
            'score': score,
            'elapsed_seconds': elapsed_seconds,
            'rank': user_rank,
            'leaderboard': list(leaderboard)
        }, status=status.HTTP_200_OK)


class GetDailyChallenge(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        
        daily_challenge = get_or_create_daily_challenge()
        
        # Get the leaderboard
        leaderboard = DailyChallengeResult.objects.filter(
            daily_challenge=daily_challenge
        ).order_by('completion_time_seconds').values('username', 'completion_time_seconds')[:10]
        
        # Check if user has completed today's challenge
        user_completed = False
        user_time = None
        user_rank = None
        
        if username:
            try:
                user_result = DailyChallengeResult.objects.get(
                    username=username,
                    daily_challenge=daily_challenge
                )
                user_completed = True
                user_time = user_result.completion_time_seconds
                user_rank = DailyChallengeResult.objects.filter(
                    daily_challenge=daily_challenge,
                    completion_time_seconds__lt=user_time
                ).count() + 1
            except DailyChallengeResult.DoesNotExist:
                pass
        
        response_data = {
            'num_var': daily_challenge.num_var,
            'form': daily_challenge.form,
            'terms': daily_challenge.terms,
            'dont_cares': daily_challenge.dont_cares,
            'groupings': daily_challenge.groupings,
            'date': daily_challenge.date,
            'leaderboard': list(leaderboard),
            'user_completed': user_completed
        }
        
        if user_completed:
            response_data['user_time'] = user_time
            response_data['user_rank'] = user_rank
        
        return Response(response_data, status=status.HTTP_200_OK)


class GetDailyChallengeLeaderboard(APIView):
    def get(self, request):
        """Get only the leaderboard for today's daily challenge"""
        username = request.query_params.get('username')
        
        daily_challenge = get_or_create_daily_challenge()
        
        # Get the full leaderboard
        leaderboard = DailyChallengeResult.objects.filter(
            daily_challenge=daily_challenge
        ).order_by('completion_time_seconds').values('username', 'completion_time_seconds')
        
        # Check if user has completed today's challenge
        user_rank = None
        if username:
            try:
                user_result = DailyChallengeResult.objects.get(
                    username=username,
                    daily_challenge=daily_challenge
                )
                user_rank = DailyChallengeResult.objects.filter(
                    daily_challenge=daily_challenge,
                    completion_time_seconds__lt=user_result.completion_time_seconds
                ).count() + 1
            except DailyChallengeResult.DoesNotExist:
                pass
        
        response_data = {
            'date': daily_challenge.date,
            'leaderboard': list(leaderboard),
            'total_participants': len(list(leaderboard))
        }
        
        if user_rank:
            response_data['user_rank'] = user_rank
        
        return Response(response_data, status=status.HTTP_200_OK)
        # if not answer:
        #     return Response({'error': 'Answer is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # user = User.objects.get(username=username)
        # result = kmap_solver.minimizeAndCheck(num_var = user.q_num_var, form_terms = user.q_form, terms = user.q_terms, dont_cares =  user.q_dont_cares, input_answer=answer)
        # if result == 1:
        #     user.score += 1
        #     if user.score >= 5 and user.difficulty == 1:
        #         user.difficulty = 2
        #     if user.score >= 10 and user.difficulty == 2:
        #         user.difficulty = 3
        #     user.q_num_var, user.q_form, user.q_terms, user.q_dont_cares, user.q_groupings = kmap_solver.randomizeQuestion(difficulty=user.difficulty)
        #     user.save()
        #     serializer = UserSerializer(user)
        #     return Response({'result': result, 'user': serializer.data}, status=status.HTTP_200_OK)
        # else:
        #     serializer = UserSerializer(user)
        #     return Response({'result': result, 'user': serializer.data}, status=status.HTTP_200_OK)
