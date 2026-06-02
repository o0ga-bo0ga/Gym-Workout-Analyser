from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class WorkoutSet:
    """A single set: weight x reps."""

    weight_kg: float
    reps: int


@dataclass
class ExerciseDescription:
    """Description of an exercise with multiple sets."""

    name: str
    sets: list[WorkoutSet] = field(default_factory=list)

    def total_volume(self) -> int:
        return sum(s.weight_kg * s.reps for s in self.sets)


@dataclass
class Workout:
    """A workout session."""

    workout_date: date
    title: str
    total_volume: int
    exercise_count: int
    set_count: int
    description: dict[str, list[dict]] = field(default_factory=dict)
    workout_id: Optional[int] = None
    is_rest_day: bool = False
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        date_str = self.workout_date.isoformat()
        return {
            "date": date_str,
            "workout_perform_date": date_str,
            "title": self.title,
            "total_volume": self.total_volume,
            "exercise_count": self.exercise_count,
            "set_count": self.set_count,
            "description": self.description,
        }


@dataclass
class WorkoutSummary:
    """21-day workout summary."""

    total_days: int
    workout_days: int
    rest_days: int
    total_volume: int
    avg_volume: float
    avg_exercises: float
    avg_sets: float


@dataclass
class RestDay:
    """A rest day record."""

    workout_date: date
    is_rest_day: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: tuple) -> "RestDay":
        return cls(
            workout_date=row[0],
            is_rest_day=row[1],
            created_at=row[2] if len(row) > 2 else None,
        )
