"""Tests for discord webhook helpers."""

import pytest

from discord import (
    MAX_DISCORD_CONTENT_LENGTH,
    _chunk_content,
    format_discord_message,
    send_discord_message,
)


def test_format_discord_message_contains_title_and_date():
    message = format_discord_message(
        "Analysis text",
        {"title": "Upper", "workout_perform_date": "2026-02-01 10:00:00"},
    )
    assert "Upper" in message
    assert "2026-02-01" in message


def test_format_discord_message_does_not_truncate_long_content():
    message = format_discord_message(
        "x" * 5000,
        {"title": "Upper", "workout_perform_date": "2026-02-01 10:00:00"},
    )
    assert len(message) > MAX_DISCORD_CONTENT_LENGTH


def test_send_discord_message_posts_chunked_payloads(monkeypatch):
    captured = []

    class DummyResponse:
        status_code = 204
        text = ""

    def fake_post(url, json, timeout):
        captured.append((url, json, timeout))
        return DummyResponse()

    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.com/webhook")
    monkeypatch.setattr("discord.requests.post", fake_post)

    send_discord_message("x" * 5000)

    assert len(captured) == 3
    assert captured[0][0] == "https://example.com/webhook"
    assert len(captured[0][1]["content"]) == MAX_DISCORD_CONTENT_LENGTH
    assert len(captured[1][1]["content"]) == MAX_DISCORD_CONTENT_LENGTH
    assert len(captured[2][1]["content"]) == 1000


def test_send_discord_message_raises_on_http_error(monkeypatch):
    class DummyResponse:
        status_code = 400
        text = "bad request"

    def fake_post(url, json, timeout):
        return DummyResponse()

    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.com/webhook")
    monkeypatch.setattr("discord.requests.post", fake_post)

    with pytest.raises(RuntimeError, match="Discord webhook failed 400"):
        send_discord_message("test")


def test_chunk_content_avoids_mid_word_splits():
    text = ("word " * 600).strip()
    chunks = _chunk_content(text, max_length=2000)

    assert len(chunks) > 1
    assert all(len(chunk) <= 2000 for chunk in chunks)
    assert all(not chunk.endswith(" ") for chunk in chunks)
    assert " ".join(chunks) == text
