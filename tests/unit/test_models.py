from datetime import date

from src.models import ExerciseDescription, Workout, WorkoutSet, WorkoutSummary


class TestWorkoutSet:
    def test_total_volume_single_set(self):
        s = WorkoutSet(weight_kg=30, reps=10)
        assert s.weight_kg * s.reps == 300

    def test_total_volume_multiple_sets(self):
        sets = [WorkoutSet(30, 10), WorkoutSet(30, 8), WorkoutSet(30, 6)]
        total = sum(s.weight_kg * s.reps for s in sets)
        assert total == 720  # 300 + 240 + 180


class TestExerciseDescription:
    def test_single_exercise(self):
        ex = ExerciseDescription(
            name="Bench Press",
            sets=[WorkoutSet(30, 10), WorkoutSet(30, 8)]
        )
        assert ex.name == "Bench Press"
        assert len(ex.sets) == 2
        assert ex.total_volume() == 540

    def test_empty_sets(self):
        ex = ExerciseDescription(name="Test", sets=[])
        assert ex.total_volume() == 0


class TestWorkout:
    def test_workout_creation(self):
        w = Workout(
            workout_date=date(2025, 4, 23),
            title="Chest + Triceps",
            total_volume=15000,
            exercise_count=5,
            set_count=20,
        )
        assert w.title == "Chest + Triceps"
        assert w.is_rest_day is False

    def test_workout_to_dict(self):
        w = Workout(
            workout_date=date(2025, 4, 23),
            title="Test",
            total_volume=1000,
            exercise_count=3,
            set_count=10,
        )
        d = w.to_dict()
        assert d["date"] == "2025-04-23"
        assert d["title"] == "Test"
        assert d["total_volume"] == 1000


class TestWorkoutSummary:
    def test_summary_creation(self):
        s = WorkoutSummary(
            total_days=21,
            workout_days=12,
            rest_days=9,
            total_volume=150000,
            avg_volume=12500,
            avg_exercises=4.5,
            avg_sets=18.0,
        )
        assert s.total_days == 21
        assert s.workout_days == 12
        assert s.rest_days == 9
