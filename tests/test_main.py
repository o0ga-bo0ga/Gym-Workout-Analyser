"""Tests for main.py pipeline orchestration."""

from typing import Any

import pytest

from main import PipelineServices, PipelineSettings, run_pipeline


def _build_services(recorder: dict[str, Any]) -> PipelineServices:
    def fetch_today():
        recorder["fetch_today_calls"] += 1
        return recorder.get("workout")

    def persist_today(workout):
        recorder["persist_today_calls"].append(workout)
        if recorder.get("persist_raises"):
            raise RuntimeError("db down")

    def fetch_recent_workouts(days):
        recorder["history_days"].append(days)
        return recorder.get("history", [])

    def analyze_workout(workout, history):
        recorder["analyze_calls"].append((workout, history))
        if recorder.get("analyze_raises"):
            raise RuntimeError("llm down")
        return recorder.get("analysis", "analysis ok")

    def format_discord_message(analysis, workout):
        recorder["format_calls"].append((analysis, workout))
        return f"formatted: {analysis}"

    def send_discord_message(text):
        recorder["sent_messages"].append(text)

    return PipelineServices(
        fetch_today=fetch_today,
        persist_today=persist_today,
        fetch_recent_workouts=fetch_recent_workouts,
        analyze_workout=analyze_workout,
        format_discord_message=format_discord_message,
        send_discord_message=send_discord_message,
    )


def _new_recorder() -> dict[str, Any]:
    return {
        "workout": None,
        "history": [],
        "analysis": "analysis ok",
        "fetch_today_calls": 0,
        "persist_today_calls": [],
        "history_days": [],
        "analyze_calls": [],
        "format_calls": [],
        "sent_messages": [],
    }


def test_run_pipeline_analysis_flow(capsys):
    recorder = _new_recorder()
    recorder["workout"] = {"title": "Upper", "workout_perform_date": "2026-01-01"}
    recorder["history"] = [{"title": "Lower"}]
    recorder["analysis"] = "great session"

    services = _build_services(recorder)
    settings = PipelineSettings(
        lyfta_enabled=True,
        db_enabled=True,
        analysis_enabled=True,
        history_window_days=14,
    )

    run_pipeline(services, settings)

    assert recorder["fetch_today_calls"] == 1
    assert recorder["persist_today_calls"] == [recorder["workout"]]
    assert recorder["history_days"] == [14]
    assert len(recorder["analyze_calls"]) == 1
    assert recorder["format_calls"] == [("great session", recorder["workout"])]
    assert recorder["sent_messages"] == ["formatted: great session"]
    assert "great session" in capsys.readouterr().out


def test_run_pipeline_rest_day_message_sent():
    recorder = _new_recorder()
    services = _build_services(recorder)
    settings = PipelineSettings(
        lyfta_enabled=True,
        db_enabled=True,
        analysis_enabled=True,
        history_window_days=28,
        rest_day_message="rest msg",
    )

    run_pipeline(services, settings)

    assert recorder["persist_today_calls"] == [None]
    assert recorder["analyze_calls"] == []
    assert recorder["sent_messages"] == ["rest msg"]


def test_run_pipeline_db_failure_raises():
    recorder = _new_recorder()
    recorder["workout"] = {"title": "Upper"}
    recorder["persist_raises"] = True

    services = _build_services(recorder)
    settings = PipelineSettings(
        lyfta_enabled=True,
        db_enabled=True,
        analysis_enabled=True,
        history_window_days=28,
    )

    with pytest.raises(RuntimeError, match="db down"):
        run_pipeline(services, settings)


def test_run_pipeline_analysis_disabled_does_not_send_rest_message():
    recorder = _new_recorder()
    recorder["workout"] = {"title": "Upper", "workout_perform_date": "2026-01-01"}

    services = _build_services(recorder)
    settings = PipelineSettings(
        lyfta_enabled=True,
        db_enabled=True,
        analysis_enabled=False,
        history_window_days=28,
        rest_day_message="rest msg",
    )

    run_pipeline(services, settings)

    assert recorder["persist_today_calls"] == [recorder["workout"]]
    assert recorder["analyze_calls"] == []
    assert recorder["sent_messages"] == []
