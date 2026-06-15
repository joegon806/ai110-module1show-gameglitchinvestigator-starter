"""Tests for the switched-hint bug in check_guess.

The bug: when a guess was too high, the hint told the player to go HIGHER,
and when too low it told them to go LOWER. These tests pin the hint message
(the second element of the returned tuple) to the correct direction so the
swap can't silently come back.

check_guess(guess, secret) returns (outcome, message).
"""

from app import check_guess


def test_too_high_hint_says_go_lower():
    # Guess is above the secret -> player should aim LOWER next.
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_hint_says_go_higher():
    # Guess is below the secret -> player should aim HIGHER next.
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message


def test_correct_guess_wins():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


# The same swap existed in the TypeError fallback path, which runs when the
# secret is a string (the app passes a stringified secret on even attempts).
def test_too_high_hint_in_string_fallback_says_go_lower():
    outcome, message = check_guess(60, "50")
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_hint_in_string_fallback_says_go_higher():
    outcome, message = check_guess(40, "50")
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message
