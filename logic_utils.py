#FIX: Refactored get_range_for_difficulty into logic_utils.py, and swapped the
# Normal/Hard ranges back into the right order.
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20

    # Normal and Hard had their ranges interchanged: Hard was 1-50 while
    # Normal was 1-100, so "Hard" was actually the easier of the two.
    # The range now widens as difficulty goes up: 20 -> 50 -> 100.
    if difficulty == "Normal":
        return 1, 50

    if difficulty == "Hard":
        return 1, 100

    return 1, 100


#FIX: Refactored parse_guess into logic_utils.py (behaviour unchanged).
def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        # A guess like "42.7" is truncated rather than rejected, so float()
        # first and then int() — int("42.7") on its own raises ValueError.
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


#FIX: Refactored check guess logic into logic_utils.py using manual mode for personal acceptance
def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # Compare as numbers. If either side arrives as a string, a plain
    # `>` would compare character by character ("9" > "50" is True) and
    # the high/low hint would come out backwards.
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"

    return "Too Low", "📈 Go HIGHER!"


#FIX: Refactored update_score into logic_utils.py, and made a wrong guess cost
# the same 5 points whether it was too high or too low.
def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    # "Too High" used to award +5 on even attempts and -5 on odd ones, so the
    # penalty flipped sign based on nothing but the attempt count's parity.
    # Both wrong outcomes now cost a flat 5 points, so the attempt number no
    # longer affects the penalty at all.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
