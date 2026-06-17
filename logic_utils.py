def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

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
    
    #FIXME: reject guesses that are out of range 

    return True, int(number), None


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
