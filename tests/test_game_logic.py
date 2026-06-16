"""Tests for the switched-hint bug in check_guess.

The bug: when a guess was too high, the hint told the player to go HIGHER,
and when too low it told them to go LOWER. These tests pin the hint message
(the second element of the returned tuple) to the correct direction so the
swap can't silently come back.

check_guess(guess, secret) returns (outcome, message).
"""

import os

from streamlit.testing.v1 import AppTest

# Import from logic_utils (where check_guess lives) rather than through app.
# Importing app would execute the whole Streamlit script at module-load time,
# which leaks st.form's context in bare mode and breaks later AppTest runs.
from logic_utils import check_guess

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")


def _new_game_button(at):
    """Return the 'New Game' button widget from a run AppTest."""
    return next(b for b in at.button if "New Game" in b.label)


def _submit_button(at):
    """Return the 'Submit Guess' button widget from a run AppTest."""
    return next(b for b in at.button if "Submit" in b.label)


def _start_game_with_secret(secret: int):
    """Run the app once and pin a known secret so guesses are deterministic."""
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.session_state["secret"] = secret
    at.run()
    return at


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


# The "one rerun behind" display bug on Submit Guess. The bug: the "Attempts
# left" banner and Developer Debug Info were rendered ABOVE the submit handler,
# so on the run triggered by clicking Submit they read session_state BEFORE the
# handler incremented attempts / appended history. The displays therefore showed
# stale values until the *next* rerun. The fix moves the display code BELOW the
# handler (without st.rerun(), which would have wiped the in-handler hint).
# AppTest captures each element as it was rendered during the run, so this test
# fails on the old ordering and passes on the fixed ordering.
def test_submit_click_updates_displays_on_same_run():
    # Normal difficulty (default) allows 8 attempts. Guess 10 vs secret 50 is
    # "Too Low" -> not a win, attempts goes 0 -> 1 on this single click.
    at = _start_game_with_secret(50)

    at.text_input[0].set_value("10")
    _submit_button(at).click().run()

    assert at.session_state["attempts"] == 1
    # The guess is recorded on the same run the display reads it back.
    assert at.session_state["history"] == [10]
    # The banner rendered on THIS run must already reflect the new count
    # (8 allowed - 1 used = 7). On the old ordering it would still read 8.
    banner_text = " ".join(i.value for i in at.info)
    assert "Attempts left: 7" in banner_text
    # The hint is printed inside the handler; the fix must NOT use st.rerun()
    # (which would drop it), so the HIGHER hint is still on screen this click.
    warnings = " ".join(w.value for w in at.warning)
    assert "HIGHER" in warnings


def test_winning_click_shows_win_not_already_won_notice():
    # Guarding the handler replaced st.stop(); the winning run must show the
    # fresh "You won!" message and NOT also the standing "You already won"
    # notice in the same pass.
    at = _start_game_with_secret(50)

    at.text_input[0].set_value("50")
    _submit_button(at).click().run()

    assert at.session_state["status"] == "won"
    success_text = " ".join(s.value for s in at.success)
    assert "You won!" in success_text
    assert "You already won" not in success_text


def test_already_won_notice_shows_on_later_interaction():
    # On a subsequent run after the game ended, the standing notice appears and
    # the displays still render (st.stop() no longer short-circuits them).
    at = _start_game_with_secret(50)
    at.session_state["status"] = "won"
    at.run()

    success_text = " ".join(s.value for s in at.success)
    assert "You already won" in success_text
    # Debug/attempt displays still rendered (would have been skipped by st.stop).
    assert any("Attempts left" in i.value for i in at.info)
