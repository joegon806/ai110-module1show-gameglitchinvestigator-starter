"""Tests for the switched-hint bug in check_guess.

The bug: when a guess was too high, the hint told the player to go HIGHER,
and when too low it told them to go LOWER. These tests pin the hint message
(the second element of the returned tuple) to the correct direction so the
swap can't silently come back.

check_guess(guess, secret) returns (outcome, message).
"""

import os

from streamlit.testing.v1 import AppTest

from app import check_guess

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")


def _new_game_button(at):
    """Return the 'New Game' button widget from a run AppTest."""
    return next(b for b in at.button if "New Game" in b.label)


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


# The New Game button must fully reset the game so a finished game can be
# replayed. The original bug: it left status as "won"/"lost", so the status
# guard kept stopping the app and the new game never actually started. It also
# failed to reset attempts to the fresh-start value, clear the history, or
# respect the difficulty range when picking a new secret.
def test_new_game_resets_state_after_loss():
    at = AppTest.from_file(APP_PATH)
    at.run()

    # Simulate a finished (lost) game with leftover state.
    at.session_state["status"] = "lost"
    at.session_state["attempts"] = 8
    at.session_state["history"] = [10, 20, 30]
    at.run()

    _new_game_button(at).click().run()

    assert at.session_state["status"] == "playing"
    # attempts resets to the fresh-start value of 1 (not 0).
    assert at.session_state["attempts"] == 0
    # history is cleared.
    assert at.session_state["history"] == []
    # secret falls within the default ("Normal") difficulty range of 1..100.
    assert 1 <= at.session_state["secret"] <= 100


def test_new_game_resets_state_after_win():
    at = AppTest.from_file(APP_PATH)
    at.run()

    at.session_state["status"] = "won"
    at.session_state["attempts"] = 4
    at.session_state["history"] = [42]
    at.run()

    _new_game_button(at).click().run()

    assert at.session_state["status"] == "playing"
    assert at.session_state["attempts"] == 0
    assert at.session_state["history"] == []
    assert 1 <= at.session_state["secret"] <= 100
