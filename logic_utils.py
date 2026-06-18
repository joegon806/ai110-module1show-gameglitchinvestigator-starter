def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str, difficulty: str = None, past_guesses=None):
    """
    Parse user input into an int guess.

    When difficulty is provided, its inclusive [low, high] range is derived via
    get_range_for_difficulty and the guess must fall within it; otherwise it is
    rejected with a reminder of the valid range. When difficulty is omitted, no
    range check is applied.

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
        return False, None, "Please enter a whole number."

    if not number.is_integer():
        return False, None, "Please enter a whole number."

    guess = int(number)

    #FIXED: AI added an out-of-range check that rejects guesses outside the
    # difficulty's [low, high] range and reminds the user what the range is.
    if difficulty is not None:
        low, high = get_range_for_difficulty(difficulty)
        if not (low <= guess <= high):
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

def update_score(current_score: int, status: str, attempt_limit: int, attempts_taken: int):
    #FIXED: AI implemented new scoring logic based on game outcome
    """
    Update score only when the game ends.

    The score is untouched during play; individual guesses (too high / too low)
    no longer affect it. It settles once on the game-ending event:

      - "won":  add (attempt_limit + 1 - attempts_taken) * 10, so winning in
                fewer attempts is worth more.
      - "lost": subtract 5.

    Any other status ("playing", etc.) leaves the score unchanged.
    """
    if status == "won":
        return current_score + (attempt_limit + 1 - attempts_taken) * 10

    if status == "lost":
        return current_score - 5

    return current_score
