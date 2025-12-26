from google import genai
from config import GEMINI_MODE
from log import info


def analyze_workout(today_workout, history):
    if not GEMINI_MODE:
        info("GEMINI: Using mock response")
        return mock_response(today_workout, history)

    client = genai.Client()  # API key from env

    prompt = build_prompt(today_workout, history)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text


def build_prompt(today_workout, history):
    history_text = history if history else "No prior workouts in the last 4 weeks."

    return f"""
You are a strength training and hypertrophy coach.Following is my workout plan:

MONDAY — Upper Body Strength
    1.Incline Dumbbell Bench Press
    2.Wide-Grip Lat Pulldown
    3.Seated Cable Row
    4.Dumbbell Lateral Raises
    5.Face Pulls

TUESDAY — Lower Body Strength (Deadlift-free & glute bridge skipped)
    1.Goblet Squats
    2.Leg Press
    3.Walking Dumbbell Lunges
    4.Seated Leg Curl
    5.Standing Calf Raises

WEDNESDAY — REST

THURSDAY — Chest+Tricep
    1.Incline Dumbbell Bench Press
    2.Cable Fly (High → Low)
    3.Pec Deck
    4.Cable Pushdowns
    5.Overhead Cable Triceps Extensions

FRIDAY — Back+Bicep
    1.Lat Pulldown (Neutral or Close Grip)
    2.Chest-Supported Dumbbell Row
    3.Single-Arm Cable Row
    4.Wide-Grip Seated Cable Row (elbows flared)
    5.Incline Dumbbell Curl
    6.Alternating Dumbbell Curl
    7.Hammer Curl

SATURDAY — Arms+Shoulder
    1.Seated Dumbbell Shoulder Press
    2.Dumbbell Lateral Raises
    3.Cable Lateral Raises
    4.Rear-Delt Machine Fly
    5.Rope Triceps Pushdowns
    6.Overhead Rope Extensions
    7.Preacher Curl Machine

SUNDAY — REST

Analyze today's workout in the context of the past 4 weeks workout data provided.

Constraints:
- Be concise and practical
- No motivational fluff
- No disclaimers
- Days not listed in the history should be treated as rest days.
- If you see any weird rep ranges, just know that I tried going to failure, because thats what I'm gonna do regardless of weight chosen, I'm gonna pursue failure on the end sets
- Every workout will have the muscle worked in the title, that is, it will have upper, lower/legs, chest tri, back bi, arms shoulder, in the title. please look at that, see which workout i did and then analyse.
- Keep the response under 1800 characters. This is very important as if it exceeds 2000 characters the discord messaging will fail.

Today's workout:
{today_workout}

Previous 4 weeks:
{history_text}

Cover:
1. Relevance to the workout plan
2. Progression quality
3. Good things about this workout, if none say so
4. Bad things about this workout if none say so
5. One concrete recommendation for the next session
"""


def mock_response(today_workout, history):
    return """- Volume is stable over the last 4 weeks
- Exercise selection is balanced but pressing dominates
- No clear fatigue signals detected
- Load progression appears consistent
- Consider adding one additional back movement next session"""
