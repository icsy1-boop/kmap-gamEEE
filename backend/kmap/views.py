from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, DailyChallenge, DailyChallengeResult, TimeAttackResult
from .serializers import UserSerializer
from . import kmap_solver
from django.utils import timezone
from datetime import datetime
import pytz
import re


TIME_LIMIT = 30
BLOCKED_USERNAME_TERMS = (
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "dick",
    "cock",
    "cunt",
    "pussy",
    "nigger",
    "faggot",
    "bastard ",
    "slut",
    "whore",
    "rape",
    "rapist",
    "kill",
    "suicide",
    "terrorist",
    "nazi",
    "nigga",
    "jew",
    "diddy",
    "gay",
    "DLSU",
    "Ateneo",
    "puta",
    "tangina",
    "gago",
    "bobo",
    "DDS",
    "titi",
    "dede",
    "tae",
    "xijinping",
    "netanyahu",
    "epstein",
    "duterte",
    "tanga",
    "fag ",
    "ching chong",
    "chigga",
    "fucked",
    "chink",
    "cuck",
    "fag",
    "dyke",
    "queer",
    "fag",
    "faggot",
    "cunt ",
    "inutil",
    "tangengot",
    "bakla",
    "cunt",
    "n1gg3r",
    "n1gger",
    "n1gga",
    "n1gg4",
    "trans",
    "lgbt",
    "transgender",
    "lgbtq",
    "cis",
    "bastard ",
    "bbm",
    "squirrel",
    "tranny",
    "homo",
    "kirk",
    "job",
    "cracker",
    "nigga",
    "chink",
    "jap",
    "jerk",
    "hoe",
    "putin",
    "pockfucker",
    "bongbong marcos",
    "puta ka",
    "putang ina",
    "tang ina",
    "tangina",
    "burat",
    "bayag",
    "bobo",
    "nognog",
    "tanga",
    "ulol",
    "kantot",
    "anak ka ng puta",
    "ulol",
    "jakol",
    "footjob",
    "retard",
    "autistic",
    "phaggot",
    "indio",
    "cp",
    "netanyahu",
    "bantot",
    "Tel aviv",
    "kike",
    "memek",
    "kontol",
    "ngentot",
    "anjing",
    "cibai",
    "knnccb",
    "ochinpo",
    "chinchin",
    "omanko",
    "mongoloid",
    "dumbfuck",
    "dumbshit",
    "kantutan",
    "iyot",
    "eut",
    "iyotan",
    "eutan",
    "chupa",
    "chupaan",
    "chuchupain",
    "pachupa",
    "rimming",
    "rimjob",
    "goatse",
    "puke",
    "ekup",
    "tite",
    "tits",
    "etits",
    "boobs",
    "anus",
    "phallus",
    "phallic",
    "cum",
    "cumshot",
    "semen",
    "jizz",
    "queef",
    "fisting",
    "penis",
    "vagina",
    "porn",
    "bdsm",
    "anal",
    "bembang",
    "titjob",
    "testicle",
    "yagballs",
    "suso",
    "bbw",
    "yawa",
    "pisti",
    "pisting yawa",
    "totnak",
    "kingina",
    "puking ina",
    "pucha",
    "pota",
    "pekpek",
    "kipay",
    "tamod",
    "jakolero",
    "salsal",
    "salsalero",
    "kiffy",
    "kupal",
    "ogag",
    "betlog",
    "himas",
    "lamas",
    "himasin",
    "lamasin",
    "tarantado",
    "pwet",
    "puwet",
    "pwetan",
    "puwetan",
    "utong",
    "ukinam",
    "potaena",
    "pepe",
    "keps",
    "kepyas",
    "pokpok",
    "bullshit",
    "kinantot",
    "pakantot",
    "kantotero",
    "kantotera",
    "bilat",
    "lubot",
    "bayot",
    "biot",
    "2g1c",
    "2 girls 1 cup",
    "acrotomophilia",
    "alabama hot pocket",
    "alaskan pipeline",
    "anal",
    "anilingus",
    "anus",
    "apeshit",
    "arsehole",
    "ass",
    "asshole",
    "assmunch",
    "auto erotic",
    "autoerotic",
    "babeland",
    "baby batter",
    "baby juice",
    "ball gag",
    "ball gravy",
    "ball kicking",
    "ball licking",
    "ball sack",
    "ball sucking",
    "bangbros",
    "bangbus",
    "bareback",
    "barely legal",
    "barenaked",
    "bastard",
    "bastardo",
    "bastinado",
    "bbw",
    "bdsm",
    "beaner",
    "beaners",
    "beaver cleaver",
    "beaver lips",
    "beastiality",
    "bestiality",
    "big black",
    "big breasts",
    "big knockers",
    "big tits",
    "bimbos",
    "birdlock",
    "bitch",
    "bitches",
    "black cock",
    "blonde action",
    "blonde on blonde action",
    "blowjob",
    "blow job",
    "blow your load",
    "blue waffle",
    "blumpkin",
    "bollocks",
    "bondage",
    "boner",
    "boob",
    "boobs",
    "booty call",
    "brown showers",
    "brunette action",
    "bukkake",
    "bulldyke",
    "bullet vibe",
    "bullshit",
    "bung hole",
    "bunghole",
    "busty",
    "butt",
    "buttcheeks",
    "butthole",
    "camel toe",
    "camgirl",
    "camslut",
    "camwhore",
    "carpet muncher",
    "carpetmuncher",
    "chocolate rosebuds",
    "cialis",
    "circlejerk",
    "cleveland steamer",
    "clit",
    "clitoris",
    "clover clamps",
    "clusterfuck",
    "cock",
    "cocks",
    "coprolagnia",
    "coprophilia",
    "cornhole",
    "coon",
    "coons",
    "creampie",
    "cum",
    "cumming",
    "cumshot",
    "cumshots",
    "cunnilingus",
    "cunt",
    "darkie",
    "date rape",
    "daterape",
    "deep throat",
    "deepthroat",
    "dendrophilia",
    "dick",
    "dildo",
    "dingleberry",
    "dingleberries",
    "dirty pillows",
    "dirty sanchez",
    "doggie style",
    "doggiestyle",
    "doggy style",
    "doggystyle",
    "dog style",
    "dolcett",
    "domination",
    "dominatrix",
    "dommes",
    "donkey punch",
    "double dong",
    "double penetration",
    "dp action",
    "dry hump",
    "dvda",
    "eat my ass",
    "ecchi",
    "ejaculation",
    "erotic",
    "erotism",
    "escort",
    "eunuch",
    "fag",
    "faggot",
    "fecal",
    "felch",
    "fellatio",
    "feltch",
    "female squirting",
    "femdom",
    "figging",
    "fingerbang",
    "fingering",
    "fisting",
    "foot fetish",
    "footjob",
    "frotting",
    "fuck",
    "fuck buttons",
    "fuckin",
    "fucking",
    "fucktards",
    "fudge packer",
    "fudgepacker",
    "futanari",
    "gangbang",
    "gang bang",
    "gay sex",
    "genitals",
    "giant cock",
    "girl on",
    "girl on top",
    "girls gone wild",
    "goatcx",
    "goatse",
    "god damn",
    "gokkun",
    "golden shower",
    "goodpoop",
    "goo girl",
    "goregasm",
    "grope",
    "group sex",
    "g-spot",
    "guro",
    "hand job",
    "handjob",
    "hard core",
    "hardcore",
    "hentai",
    "homoerotic",
    "honkey",
    "hooker",
    "horny",
    "hot carl",
    "hot chick",
    "how to kill",
    "how to murder",
    "huge fat",
    "humping",
    "incest",
    "intercourse",
    "jack off",
    "jail bait",
    "jailbait",
    "jelly donut",
    "jerk off",
    "jigaboo",
    "jiggaboo",
    "jiggerboo",
    "jizz",
    "juggs",
    "kike",
    "kinbaku",
    "kinkster",
    "kinky",
    "knobbing",
    "leather restraint",
    "leather straight jacket",
    "lemon party",
    "livesex",
    "lolita",
    "lovemaking",
    "make me come",
    "male squirting",
    "masturbate",
    "masturbating",
    "masturbation",
    "menage a trois",
    "milf",
    "missionary position",
    "mong",
    "motherfucker",
    "mound of venus",
    "mr hands",
    "muff diver",
    "muffdiving",
    "nambla",
    "nawashi",
    "negro",
    "neonazi",
    "nigga",
    "nigger",
    "nig nog",
    "nimphomania",
    "nipple",
    "nipples",
    "nsfw",
    "nsfw images",
    "nude",
    "nudity",
    "nutten",
    "nympho",
    "nymphomania",
    "octopussy",
    "omorashi",
    "one cup two girls",
    "one guy one jar",
    "orgasm",
    "orgy",
    "paedophile",
    "paki",
    "panties",
    "panty",
    "pedobear",
    "pedophile",
    "pegging",
    "penis",
    "phone sex",
    "piece of shit",
    "pikey",
    "pissing",
    "piss pig",
    "pisspig",
    "playboy",
    "pleasure chest",
    "pole smoker",
    "ponyplay",
    "poof",
    "poon",
    "poontang",
    "punany",
    "poop chute",
    "poopchute",
    "porn",
    "porno",
    "pornography",
    "prince albert piercing",
    "pthc",
    "pubes",
    "pussy",
    "queaf",
    "queef",
    "quim",
    "raghead",
    "raging boner",
    "rape",
    "raping",
    "rapist",
    "rectum",
    "reverse cowgirl",
    "rimjob",
    "rimming",
    "rosy palm",
    "rosy palm and her 5 sisters",
    "rusty trombone",
    "sadism",
    "santorum",
    "scat",
    "schlong",
    "scissoring",
    "semen",
    "sex",
    "sexcam",
    "sexo",
    "sexy",
    "sexual",
    "sexually",
    "sexuality",
    "shaved beaver",
    "shaved pussy",
    "shemale",
    "shibari",
    "shit",
    "shitblimp",
    "shitty",
    "shota",
    "shrimping",
    "skeet",
    "slanteye",
    "slut",
    "s&m",
    "smut",
    "snatch",
    "snowballing",
    "sodomize",
    "sodomy",
    "spastic",
    "spic",
    "splooge",
    "splooge moose",
    "spooge",
    "spread legs",
    "spunk",
    "strap on",
    "strapon",
    "strappado",
    "strip club",
    "style doggy",
    "suck",
    "sucks",
    "suicide girls",
    "sultry women",
    "swastika",
    "swinger",
    "tainted love",
    "taste my",
    "tea bagging",
    "threesome",
    "throating",
    "thumbzilla",
    "tied up",
    "tight white",
    "tit",
    "tits",
    "titties",
    "titty",
    "tongue in a",
    "topless",
    "tosser",
    "towelhead",
    "tranny",
    "tribadism",
    "tub girl",
    "tubgirl",
    "tushy",
    "twat",
    "twink",
    "twinkie",
    "two girls one cup",
    "undressing",
    "upskirt",
    "urethra play",
    "urophilia",
    "vagina",
    "venus mound",
    "viagra",
    "vibrator",
    "violet wand",
    "vorarephilia",
    "voyeur",
    "voyeurweb",
    "voyuer",
    "vulva",
    "wank",
    "wetback",
    "wet dream",
    "white power",
    "whore",
    "worldsex",
    "wrapping men",
    "wrinkled starfish",
    "xx",
    "xxx",
    "yaoi",
    "yellow showers",
    "yiffy",
    "zoophilia",
    "🖕",
)


def validate_username(username):
    if not username or not str(username).strip():
        return "Username is required"

    cleaned = str(username).strip()
    if len(cleaned) < 3 or len(cleaned) > 20:
        return "Username must be 3 to 20 characters long"

    if not re.fullmatch(r"[A-Za-z_ ]+", cleaned):
        return "Username can only contain letters, spaces, and underscores"

    normalized_letters = re.sub(r"[^a-z]", "", cleaned.lower())
    if any(term in normalized_letters for term in BLOCKED_USERNAME_TERMS):
        return "This username is not allowed"

    return None



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
        username_error = validate_username(username)
        if username_error:
            return Response({'error': username_error}, status=status.HTTP_400_BAD_REQUEST)

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
        ).order_by('completion_time_seconds').values('username', 'completion_time_seconds')[:5]
        
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


class StartTimeAttack(APIView):
    def post(self, request):
        username = request.data.get('username')
        difficulty = request.data.get('difficulty')
        
        username_error = validate_username(username)
        if username_error:
            return Response({'error': username_error}, status=status.HTTP_400_BAD_REQUEST)

        if not username or difficulty not in [1, 2, 3]:
            return Response({'error': 'Invalid username or difficulty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate first question
        num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=difficulty)
        
        return Response({
            'username': username,
            'difficulty': difficulty,
            'questions_solved': 0,
            'time_remaining': TIME_LIMIT,
            'q_num_var': num_var,
            'q_form': form,
            'q_terms': terms,
            'q_dont_cares': dont_cares,
            'q_groupings': groupings
        }, status=status.HTTP_200_OK)


class CheckTimeAttackAnswer(APIView):
    def post(self, request):
        username = request.data.get('username')
        difficulty = request.data.get('difficulty')
        questions_solved = request.data.get('questions_solved', 0)
        time_remaining = request.data.get('time_remaining', 0)
        
        num_var = request.data.get('q_num_var')
        form = request.data.get('q_form')
        terms = request.data.get('q_terms')
        dont_cares = request.data.get('q_dont_cares')
        answer = request.data.get('answer')
        
        # Check the answer
        result, answers = kmap_solver.minimizeAndCheck(
            num_var=num_var,
            form_terms=form,
            terms=terms,
            dont_cares=dont_cares,
            input_answer=answer)
        
        if result != 1:
            # Wrong answer - game over, don't save to leaderboard
            return Response({
                'result': 0,
                'answers': answers,
                'game_over': True,
                'reason': 'Wrong answer - run is invalid'
            }, status=status.HTTP_200_OK)
        
        # Correct answer
        questions_solved += 1
        
        # Generate next question
        num_var, form, terms, dont_cares, groupings = kmap_solver.randomizeQuestion(difficulty=difficulty)
        
        return Response({
            'result': 1,
            'answers': answers,
            'questions_solved': questions_solved,
            'time_remaining': time_remaining,
            'q_num_var': num_var,
            'q_form': form,
            'q_terms': terms,
            'q_dont_cares': dont_cares,
            'q_groupings': groupings
        }, status=status.HTTP_200_OK)


class FinishTimeAttack(APIView):
    def post(self, request):
        username = request.data.get('username')
        difficulty = request.data.get('difficulty')
        questions_solved = request.data.get('questions_solved', 0)
        is_valid = request.data.get('is_valid', False)
        
        if not username or difficulty not in [1, 2, 3]:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Only save to leaderboard if run is valid (no wrong answers)
        if is_valid and questions_solved > 0:
            TimeAttackResult.objects.create(
                username=username,
                difficulty=difficulty,
                questions_solved=questions_solved
            )
        
        # Get leaderboard for this difficulty
        leaderboard = TimeAttackResult.objects.filter(
            difficulty=difficulty
        ).order_by('-questions_solved', 'created_at').values('username', 'questions_solved')[:10]
        
        # Find user's rank if they have a valid entry
        user_rank = None
        if is_valid and questions_solved > 0:
            user_rank = TimeAttackResult.objects.filter(
                difficulty=difficulty,
                questions_solved__gt=questions_solved
            ).count() + 1
        
        return Response({
            'username': username,
            'difficulty': difficulty,
            'questions_solved': questions_solved,
            'is_valid': is_valid,
            'rank': user_rank,
            'leaderboard': list(leaderboard)
        }, status=status.HTTP_200_OK)


class GetTimeAttackLeaderboard(APIView):
    def get(self, request):
        difficulty = request.query_params.get('difficulty')
        
        if difficulty not in ['1', '2', '3']:
            return Response({'error': 'Invalid difficulty'}, status=status.HTTP_400_BAD_REQUEST)
        
        difficulty = int(difficulty)
        
        leaderboard = TimeAttackResult.objects.filter(
            difficulty=difficulty
        ).order_by('-questions_solved', 'created_at').values('username', 'questions_solved')[:100]
        
        return Response({
            'difficulty': difficulty,
            'leaderboard': list(leaderboard)
        }, status=status.HTTP_200_OK)
