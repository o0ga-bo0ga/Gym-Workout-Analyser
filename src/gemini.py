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
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def build_prompt(today_workout, history):
    history_text = history if history else "No prior workouts in the last 4 weeks."

    return f"""
You are a strength training and hypertrophy coach.

Analyze today's workout in the context of the past 4 weeks.

Constraints:
- Be concise and practical
- No motivational fluff
- No disclaimers
- Max 6 bullet points
- Focus on training decisions

Today's workout:
{today_workout}

Previous 4 weeks:
{history_text}

Cover:
1. Volume trend
2. Exercise balance
3. Fatigue or recovery risk
4. Progression quality
5. One concrete recommendation for the next session
"""


def mock_response(today_workout, history):
    return """- Volume is stable over the last 4 weeks
- Exercise selection is balanced but pressing dominates
- No clear fatigue signals detected
- Load progression appears consistent
- Consider adding one additional back movement next session"""
