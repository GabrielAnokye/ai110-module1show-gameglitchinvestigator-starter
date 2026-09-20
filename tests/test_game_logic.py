import pytest

from logic_utils import check_guess


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
