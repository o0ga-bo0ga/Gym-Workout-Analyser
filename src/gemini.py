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

1. Flat Dumbbell Bench Press
2. Bent-Over Dumbbell Rows (Heavy)
3. Single-Arm Dumbbell Row (Bench Supported)
4. Seated Dumbbell Overhead Press
5. Lat Pulldown (Wide Grip)
6. Dumbbell Skullcrushers

TUESDAY — Lower Body Strength (Deadlift-free & glute bridge skipped)

1. Heavy Goblet Squats
2. Leg Curl Machine
3. Heel-Elevated Dumbbell Squats OR Leg Press
4. Standing Calf Raises (Holding Dumbbell)

WEDNESDAY — REST

THURSDAY — Push Hypertrophy

1. Incline Dumbbell Press (30°)
2. Dumbbell Lateral Raises
3. Flat Dumbbell Flyes (or DB Press)
4. Arnold Press / Light Shoulder Press
5. Rope Tricep Pushdowns

FRIDAY — Pull Hypertrophy

1. Lat Pulldown (V-Grip / Neutral)
2. Single-Arm Dumbbell Row
3. Face Pulls
4. Rear Delt Dumbbell Flyes
5. Standing Dumbbell Curls
6. Hammer Curls (Wall-Supported)

SATURDAY — Legs Volume (High Rep)

1. Bulgarian Split Squats
2. Goblet Squats (Volume)
3. Dumbbell Lunges
4. Leg Curl Machine
5. Seated Calf Raises (DBs on knees)

SUNDAY — REST

Analyze today's workout in the context of the past 4 weeks workout data provided.

Constraints:
- Be concise and practical
- No motivational fluff
- No disclaimers
- Days not listed in the history should be treated as rest days.

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
