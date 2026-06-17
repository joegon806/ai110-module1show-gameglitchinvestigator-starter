"""Tests for the switched-hint bug in check_guess.

The bug: when a guess was too high, the hint told the player to go HIGHER,
and when too low it told them to go LOWER. These tests pin the hint message
(the second element of the returned tuple) to the correct direction so the
swap can't silently come back.

check_guess(guess, secret) returns (outcome, message).
"""

import os

import pytest
from streamlit.testing.v1 import AppTest

# Import from logic_utils (where check_guess lives) rather than through app.
# Importing app would execute the whole Streamlit script at module-load time,
# which leaks st.form's context in bare mode and breaks later AppTest runs.
from logic_utils import check_guess, parse_guess

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


# The front end feeds raw text input through parse_guess before check_guess,
# so these mirror that flow: parse the strings to ints first, then compare.
def test_too_high_hint_in_string_fallback_says_go_lower():
    _, guess, _ = parse_guess("60")
    _, secret, _ = parse_guess("50")
    outcome, message = check_guess(guess, secret)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message


def test_too_low_hint_in_string_fallback_says_go_higher():
    _, guess, _ = parse_guess("40")
    _, secret, _ = parse_guess("50")
    outcome, message = check_guess(guess, secret)
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


# The Enter key submits the guess because the input and the Submit button live
# in the SAME st.form. On the real frontend, pressing Enter in a form field and
# clicking the form's submit button fire the identical "form submitted" event,
# so AppTest models both the same way. What makes Enter work (rather than do
# nothing, as it did when the input was a bare text_input beside a plain button)
# is that shared form binding — that's what this test pins down.
def test_enter_key_submits_guess_via_form():
    at = _start_game_with_secret(50)

    guess_input = at.text_input[0]
    submit = _submit_button(at)
    new_game = _new_game_button(at)

    # The guess field and Submit share one form, so Enter in the field submits it.
    # New Game sits outside any form (so it can't be triggered by Enter).
    assert submit.is_form_submitter
    assert guess_input.form_id != ""
    assert guess_input.form_id == submit.form_id
    assert new_game.form_id == ""

    # Submitting the form (the same event an Enter keypress produces) processes
    # the guess on that single run.
    guess_input.set_value("10")
    submit.click().run()

    assert at.session_state["attempts"] == 1
    assert at.session_state["history"] == [10]


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


# The hint must NOT display on the player's last attempt. The bug: the hint
# (the Too High/Too Low warning) rendered on every losing guess, including the
# final one where there's no remaining guess to act on it. The fix gates the
# warning on st.session_state.attempts < attempt_limit (checked AFTER attempts
# is incremented), so the last guess shows the "Out of attempts!" message but
# no hint.
def test_hint_hidden_on_last_attempt():
    # Normal difficulty allows 8 attempts. Pre-load 7 used attempts so this
    # losing guess (10 vs 50 -> Too Low) is the 8th and final one.
    at = _start_game_with_secret(50)
    at.session_state["attempts"] = 7
    at.run()

    at.text_input[0].set_value("10")
    _submit_button(at).click().run()

    # The game ends out of attempts...
    assert at.session_state["attempts"] == 8
    assert at.session_state["status"] == "lost"
    error_text = " ".join(e.value for e in at.error)
    assert "Out of attempts!" in error_text
    # ...and no hint warning is shown on this final guess.
    warnings = " ".join(w.value for w in at.warning)
    assert "HIGHER" not in warnings
    assert "LOWER" not in warnings


def test_hint_shown_when_attempts_remain():
    # Control case: with attempts still left (this is the 1st of 8), a losing
    # guess should still show its directional hint.
    at = _start_game_with_secret(50)

    at.text_input[0].set_value("10")
    _submit_button(at).click().run()

    assert at.session_state["attempts"] == 1
    assert at.session_state["status"] == "playing"
    warnings = " ".join(w.value for w in at.warning)
    assert "HIGHER" in warnings


# The hint-direction glitch lived in app.py's even-attempt branch, which turned
# the secret into a string and made check_guess fall back to lexicographic
# comparison. With secret 50, guesses of 6 and 100 are exactly the cases that
# comparison gets backwards ("6" > "50" and "100" < "50" are both True), so they
# pin the fix. Each test guesses both numbers in a different order so each value
# lands on BOTH an odd (1st) and even (2nd) attempt across the two tests --
# proving the bug is gone regardless of which attempt parity it lived on, and
# without ever repeating a guess within a game.
def test_low_then_high_guess_give_correct_hints():
    at = _start_game_with_secret(50)

    # 1st attempt (odd): 6 < 50 -> HIGHER.
    at.text_input[0].set_value("6")
    _submit_button(at).click().run()
    assert at.session_state["attempts"] == 1
    warnings = " ".join(w.value for w in at.warning)
    assert "HIGHER" in warnings
    assert "LOWER" not in warnings

    # 2nd attempt (even): 100 > 50 -> LOWER.
    at.text_input[0].set_value("100")
    _submit_button(at).click().run()
    assert at.session_state["attempts"] == 2
    warnings = " ".join(w.value for w in at.warning)
    assert "LOWER" in warnings
    assert "HIGHER" not in warnings


def test_high_then_low_guess_give_correct_hints():
    at = _start_game_with_secret(50)

    # 1st attempt (odd): 100 > 50 -> LOWER.
    at.text_input[0].set_value("100")
    _submit_button(at).click().run()
    assert at.session_state["attempts"] == 1
    warnings = " ".join(w.value for w in at.warning)
    assert "LOWER" in warnings
    assert "HIGHER" not in warnings

    # 2nd attempt (even): 6 < 50 -> HIGHER.
    at.text_input[0].set_value("6")
    _submit_button(at).click().run()
    assert at.session_state["attempts"] == 2
    warnings = " ".join(w.value for w in at.warning)
    assert "HIGHER" in warnings
    assert "LOWER" not in warnings


# parse_guess(raw) returns (ok, guess_int, error_message). These pin its
# contract directly: valid numeric strings parse to an int with no error,
# while empty and non-numeric input fail with ok=False, no value, and a message.
@pytest.mark.parametrize(
    "raw, expected",
    [("42", 42), ("7", 7), ("100", 100)],
)
def test_parse_guess_accepts_valid_integer_strings(raw, expected):
    ok, value, err = parse_guess(raw)
    assert ok is True
    assert value == expected
    assert err is None


@pytest.mark.parametrize(
    "raw, expected_err",
    [("", "Enter a guess."), ("abc", "That is not a number.")],
)
def test_parse_guess_rejects_invalid_input(raw, expected_err):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == expected_err


# Non-whole decimals are numbers but not valid integer guesses, so parse_guess
# must reject them with the "enter a whole number" message rather than silently
# truncating (the old behavior turned "3.5" into 3).
@pytest.mark.parametrize("raw", ["3.5", "0.1", "-2.75", "99.999"])
def test_parse_guess_rejects_non_whole_decimals(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "Please enter a whole number."


# A decimal whose fractional part is zero IS a whole number, so it should be
# accepted and parsed to the equivalent int -- whether written with a trailing
# dot, a single zero, or several trailing zeros.
@pytest.mark.parametrize("raw, expected", [("3.", 3), ("42.0", 42), ("-7.0000", -7)])
def test_parse_guess_accepts_whole_number_decimals(raw, expected):
    ok, value, err = parse_guess(raw)
    assert ok is True
    assert value == expected
    assert err is None


# The attempt increment was moved so a turn is only spent on a *valid* guess.
# Each valid-guess case asserts attempts INCREASED (0 -> 1); each invalid-guess
# case asserts attempts stayed UNCHANGED (still 0). Secret is 50, so none of the
# valid guesses below win, keeping the game "playing" and the count predictable.
@pytest.mark.parametrize("raw", ["10", "7", "100"])
def test_valid_guess_increments_attempts(raw):
    at = _start_game_with_secret(50)

    at.text_input[0].set_value(raw)
    _submit_button(at).click().run()

    # Valid guess -> attempts increased.
    assert at.session_state["attempts"] == 1
    assert at.session_state["history"] == [int(raw)]


@pytest.mark.parametrize("raw", ["", "abc"])
def test_invalid_guess_keeps_attempts_unchanged(raw):
    at = _start_game_with_secret(50)

    at.text_input[0].set_value(raw)
    _submit_button(at).click().run()

    # Invalid guess -> attempts unchanged, but the raw value is still recorded
    # and a parse error is shown.
    assert at.session_state["attempts"] == 0
    assert at.session_state["history"] == [raw]
    assert len(at.error) > 0
