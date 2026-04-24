import os

if os.environ.get("LANGSMITH_ENABLED", "true").lower() in ("1", "true", "yes"):
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = os.environ.get("LANGSMITH_PROJECT", "gym-workout-analysis")

from langchain_groq import ChatGroq
from langsmith import traceable

from config import LANGSMITH_ENABLED, LLM_ENABLED, LLM_MOCK, LLM_MODEL, LLM_PROVIDER
from log import info, warn


def analyze_workout(today_workout: dict, history_28_days: list | None = None) -> str:
    if LLM_ENABLED and not LLM_MOCK:
        return _analyze_with_llm(today_workout, history_28_days)
    else:
        info(f"{LLM_PROVIDER.upper()}: Using mock response")
        return mock_response(today_workout, history_28_days)


def _analyze_with_llm(today_workout: dict, history_28_days: list | None = None) -> str:
    llm = ChatGroq(
        model=LLM_MODEL,
        groq_api_key=get_api_key(),
    )

    prompt = build_prompt(today_workout, history_28_days)

    try:
        if LANGSMITH_ENABLED:
            return _analyze_with_tracing(llm, prompt)
        else:
            response = llm.invoke(prompt)
            return response.content
    except Exception as e:
        warn(f"LLM API call failed: {e}")
        raise


@traceable(name="gym_workout_analysis")
def _analyze_with_tracing(llm, prompt: str):
    return llm.invoke(prompt)


def get_api_key() -> str:
    provider = LLM_PROVIDER.lower()
    if provider == "groq":
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set")
        return key
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def build_prompt(today_workout: dict, history_28_days: list | None = None) -> str:
    history_text = history_28_days if history_28_days else "No prior workouts in the last 4 weeks."

    return f"""
You are a strength training and hypertrophy coach.Following is my workout plan:

MONDAY — Chest + Triceps
    1.Incline Dumbbell Bench Press
    2.Flat DB Press
    3.Cable Fly (high to low)
    4.Tricep Pushdown
    5.Overhead Cable Extension

TUESDAY — Back + Biceps
    1.Lat Pulldown
    2.Single-Arm Cable Row
    3.Cable Lat Pullover
    4.Wide-Grip Cable Row
    5.Incline DB Curl
    6.Hammer Curl
    7.Reverse Curl or Wrist Curl

WEDNESDAY — REST

THURSDAY — Shoulders + Arms
    1.Seated DB Shoulder Press
    2.Lateral Raises
    3.Cable Lateral Raises
    4.Rear Delt Fly
    5.Tricep Pushdown
    6.Preacher Curl

FRIDAY — Legs
    1.Smith Squats
    2.Leg Press
    3.Walking Lunges
    4.Seated Leg Curl
    5.Standing Calf Raises

SATURDAY — REST
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


def mock_response(today_workout: dict, history_28_days: list | None = None) -> str:
    return """- Volume is stable over the last 4 weeks
- Exercise selection is balanced but pressing dominates
- No clear fatigue signals detected
- Load progression appears consistent
- Consider adding one additional back movement next session"""
