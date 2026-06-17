def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def parse_guess(raw: str, low: int = None, high: int = None, past_guesses=None):
    """
    Parse user input into an int guess.

    When low and high are both provided, the guess must fall within the
    inclusive [low, high] range; otherwise it is rejected with a reminder of
    the valid range. When they are omitted, no range check is applied.

    When past_guesses is provided, a guess already present in it is rejected so
    the player can't waste a turn repeating a number. When omitted, no repeat
    check is applied.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    #FIXED: AI refactored this section to be less clunky and added a check for non-integer values.
    try:
        number = float(raw)
    except Exception:
        return False, None, "That is not a number."

    if not number.is_integer():
        return False, None, "Please enter a whole number."

    guess = int(number)

    #FIXED: AI added an out-of-range check that rejects guesses outside the
    # difficulty's [low, high] range and reminds the user what the range is.
    if low is not None and high is not None and not (low <= guess <= high):
        return False, None, f"Out of range. Guess a number between {low} and {high}."
    
    #FIXED: AI added a repeat-guess check that rejects a number the player has
    # already guessed this game, so a duplicate doesn't waste a turn.
    if past_guesses is not None and guess in past_guesses:
        return False, None, f"You already guessed {guess}. Try a different number."

    return True, guess, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIXED: Removed the except TypeError fallback that did lexicographic string
    # comparison. It only existed to mask int-vs-str mismatches and produced wrong
    # hints. Guess and secret are always ints now, so compare them numerically.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
