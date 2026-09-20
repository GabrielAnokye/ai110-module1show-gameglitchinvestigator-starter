import pytest

from logic_utils import check_guess, get_range_for_difficulty, update_score


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


@pytest.mark.parametrize(
    "guess, secret, expected",
    [
        (1, 100, "Too Low"),
        (99, 100, "Too Low"),
        (100, 100, "Win"),
        (100, 99, "Too High"),
        (2, 1, "Too High"),
    ],
)
def test_edges_of_the_range(guess, secret, expected):
    outcome, _ = check_guess(guess, secret)
    assert outcome == expected


@pytest.mark.parametrize(
    "guess, secret, expected",
    [
        # The original bug: a string secret fell back to character-by-character
        # comparison, so "9" > "50" reported a single digit as Too High.
        (9, "50", "Too Low"),
        (60, "50", "Too High"),
        ("50", 50, "Win"),
        ("9", "50", "Too Low"),
    ],
)
def test_string_inputs_compare_numerically(guess, secret, expected):
    outcome, _ = check_guess(guess, secret)
    assert outcome == expected


def test_hint_direction_is_never_backwards():
    # Whatever the secret, a guess below it must say HIGHER and above must say LOWER.
    secret = 50
    for guess in range(1, 101):
        outcome, message = check_guess(guess, secret)
        if guess < secret:
            assert outcome == "Too Low", f"{guess} vs {secret}"
            assert "HIGHER" in message
        elif guess > secret:
            assert outcome == "Too High", f"{guess} vs {secret}"
            assert "LOWER" in message
        else:
            assert outcome == "Win"


# --- update_score -----------------------------------------------------------


@pytest.mark.parametrize("attempt_number", [1, 2, 3, 4, 5, 6, 7, 8])
def test_wrong_guess_always_costs_five(attempt_number):
    # The original bug: "Too High" awarded +5 on even attempts and -5 on odd
    # ones, so the penalty flipped sign with the attempt count's parity.
    assert update_score(100, "Too High", attempt_number) == 95
    assert update_score(100, "Too Low", attempt_number) == 95


def test_too_high_and_too_low_cost_the_same():
    # The two wrong outcomes must be symmetric — neither should be cheaper.
    for attempt_number in range(1, 21):
        high = update_score(50, "Too High", attempt_number)
        low = update_score(50, "Too Low", attempt_number)
        assert high == low == 45, f"attempt {attempt_number}: {high} vs {low}"


def test_penalties_accumulate_downward():
    # Four wrong guesses in a row should be a straight -20, not a wobble.
    score = 100
    for attempt_number in range(1, 5):
        score = update_score(score, "Too High", attempt_number)
    assert score == 80


def test_score_can_go_negative():
    # Nothing clamps the score at zero, so a bad run is allowed below it.
    assert update_score(0, "Too Low", 1) == -5


@pytest.mark.parametrize(
    "attempt_number, expected_points",
    [
        (1, 80),
        (2, 70),
        (3, 60),
        (7, 20),
        (8, 10),
        # The award is floored at 10, so a very late win still pays something.
        (9, 10),
        (20, 10),
    ],
)
def test_win_award_shrinks_with_attempts(attempt_number, expected_points):
    assert update_score(0, "Win", attempt_number) == expected_points


def test_win_adds_to_existing_score():
    assert update_score(30, "Win", 1) == 110


@pytest.mark.parametrize("outcome", ["", "Invalid", "win", "too high", None])
def test_unknown_outcome_leaves_score_untouched(outcome):
    assert update_score(42, outcome, 1) == 42


# --- get_range_for_difficulty ----------------------------------------------


@pytest.mark.parametrize(
    "difficulty, expected",
    [
        ("Easy", (1, 20)),
        ("Normal", (1, 50)),
        # The original bug: Normal and Hard had their ranges interchanged,
        # so "Hard" (1-50) was narrower than "Normal" (1-100).
        ("Hard", (1, 100)),
    ],
)
def test_range_for_each_difficulty(difficulty, expected):
    assert get_range_for_difficulty(difficulty) == expected


def test_range_widens_as_difficulty_rises():
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert easy_high < normal_high < hard_high


def test_unknown_difficulty_falls_back_to_default():
    assert get_range_for_difficulty("Nightmare") == (1, 100)
