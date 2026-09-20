"""Edge-case suite for parse_guess and update_score.

Separate from test_game_logic.py, which covers the three original bugs.
Everything here probes the *boundaries* of the two functions: inputs a real
user can type into the Streamlit text box but that no happy-path test covers.
"""

import pytest

from logic_utils import check_guess, parse_guess, update_score

# ---------------------------------------------------------------------------
# parse_guess — EDGE CASE 1: negative numbers and zero
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0", 0),
        ("-1", -1),
        ("-5", -5),
        ("-100", -100),
        ("-0", 0),
        ("0000", 0),
    ],
)
def test_negative_and_zero_parse_as_valid_numbers(raw, expected):
    # Documents current behaviour: parse_guess is a *parser*, not a validator.
    # "0" and "-5" are outside every difficulty's 1..N range but still come
    # back ok=True, so nothing in the app ever rejects them.
    ok, guess, err = parse_guess(raw)
    assert ok is True
    assert guess == expected
    assert err is None


def test_out_of_range_guess_is_not_rejected_anywhere():
    # The gap this exposes: an out-of-range guess flows straight through to
    # check_guess and costs the player 5 points like any ordinary wrong guess.
    ok, guess, _ = parse_guess("-999")
    assert ok is True
    outcome, _ = check_guess(guess, 50)
    assert outcome == "Too Low"
    assert update_score(100, outcome, 1) == 95


# ---------------------------------------------------------------------------
# parse_guess — EDGE CASE 2: decimal / float strings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("3.14", 3),
        ("3.99", 3),      # truncates, does NOT round to 4
        ("50.0", 50),
        ("0.9", 0),       # a "guess" of 0.9 silently becomes 0
        (".5", 0),
        ("1.5e2", 150),   # scientific notation only survives if it has a dot
    ],
)
def test_decimal_strings_are_truncated_not_rounded(raw, expected):
    ok, guess, err = parse_guess(raw)
    assert ok is True
    assert guess == expected
    assert err is None


@pytest.mark.parametrize("raw, expected", [("-3.99", -3), ("-0.9", 0), ("-1.5", -1)])
def test_negative_decimals_truncate_toward_zero_not_down(raw, expected):
    # int(float(x)) truncates toward zero, so -3.99 -> -3 (not -4 as floor()
    # would give). Worth pinning: the rounding direction flips sign with the
    # input, which is the kind of asymmetry that hides off-by-one bugs.
    _, guess, _ = parse_guess(raw)
    assert guess == expected


def test_lone_dot_is_rejected():
    # "." contains a dot but float(".") raises, so it must fall to the error
    # branch rather than crashing the app.
    ok, guess, err = parse_guess(".")
    assert (ok, guess, err) == (False, None, "That is not a number.")


def test_scientific_notation_without_a_dot_is_rejected():
    # Asymmetry worth documenting: "1.5e2" parses but "1e3" does not, because
    # the float() path is gated on the presence of a ".".
    assert parse_guess("1e3") == (False, None, "That is not a number.")
    assert parse_guess("1.5e2") == (True, 150, None)


def test_infinity_and_overflow_are_rejected_not_crashed():
    # float("1.0e999") is inf, and int(inf) raises OverflowError — which is an
    # Exception, not a ValueError. Confirms the broad `except` catches it.
    assert parse_guess("1.0e999") == (False, None, "That is not a number.")
    assert parse_guess("inf") == (False, None, "That is not a number.")
    assert parse_guess("nan") == (False, None, "That is not a number.")


# ---------------------------------------------------------------------------
# parse_guess — EDGE CASE 3: non-numeric text and special characters
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "abc",
        "fifty",
        "!@#$%",
        "50abc",
        "3,14",        # comma decimal separator (non-US keyboards)
        "   ",         # whitespace only — not "" so it gets the parse error
        "5 0",
        "--5",
        "0x1F",
        "💯",
        "'; DROP TABLE scores;--",
        "<script>alert(1)</script>",
    ],
)
def test_non_numeric_input_returns_error_and_never_raises(raw):
    ok, guess, err = parse_guess(raw)
    assert ok is False
    assert guess is None
    assert err == "That is not a number."


@pytest.mark.parametrize("raw", ["", None])
def test_empty_and_missing_input_get_the_prompt_message(raw):
    # Distinct message from the parse failure: "" and None mean "you typed
    # nothing", which is user guidance rather than an error.
    assert parse_guess(raw) == (False, None, "Enter a guess.")


def test_whitespace_only_is_not_treated_as_empty():
    # A space-bar-only submission is NOT caught by the `raw == ""` check, so
    # the user sees "That is not a number." instead of "Enter a guess."
    assert parse_guess("   ")[2] == "That is not a number."
    assert parse_guess("")[2] == "Enter a guess."


@pytest.mark.parametrize("raw, expected", [(" 7 ", 7), ("7\n", 7), ("+7", 7), ("\t42", 42)])
def test_surrounding_whitespace_and_plus_sign_are_tolerated(raw, expected):
    # int() strips whitespace and accepts a leading "+", so copy-pasted input
    # with stray spaces still works.
    assert parse_guess(raw) == (True, expected, None)


@pytest.mark.parametrize("raw, expected", [("1_0", 10), ("１２", 12), ("٣", 3)])
def test_python_int_quirks_accept_more_than_ascii_digits(raw, expected):
    # int() also accepts PEP 515 underscores and any Unicode decimal digit, so
    # these reach the game as real numbers. Surprising, but harmless here.
    assert parse_guess(raw) == (True, expected, None)


@pytest.mark.parametrize("raw", [3, 3.9, True, [3], {"guess": 3}, object()])
def test_non_string_inputs_fail_cleanly(raw):
    # Streamlit always hands over a str, but a caller passing an int gets a
    # clean error rather than a TypeError from `"." in raw`.
    ok, guess, err = parse_guess(raw)
    assert (ok, guess) == (False, None)
    assert err == "That is not a number."


def test_very_large_number_is_accepted():
    # Python ints are unbounded, so a 40-digit guess parses fine and only
    # loses on the compare. No overflow to guard against.
    ok, guess, err = parse_guess("9" * 40)
    assert ok is True
    assert guess == int("9" * 40)
    assert err is None


# ---------------------------------------------------------------------------
# update_score — edge cases around the attempt number
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attempt_number, expected",
    [(0, 90), (1, 80), (8, 10), (9, 10), (100, 10)],
)
def test_win_award_is_floored_at_ten(attempt_number, expected):
    # attempt_number=0 is reachable: app.py resets attempts to 0 on New Game.
    assert update_score(0, "Win", attempt_number) == expected


def test_win_award_never_increases_with_more_attempts():
    # Monotonic: taking longer must never pay better.
    awards = [update_score(0, "Win", n) for n in range(0, 25)]
    assert awards == sorted(awards, reverse=True)


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN GAP: attempt_number is never validated, so a negative "
           "attempt inflates the win award above the first-attempt maximum.",
)
def test_negative_attempt_number_should_not_inflate_the_award():
    best_legitimate = update_score(0, "Win", 0)
    assert update_score(0, "Win", -5) <= best_legitimate


@pytest.mark.parametrize("attempt_number", [0, 1, 50, -3])
def test_penalty_ignores_the_attempt_number_entirely(attempt_number):
    # The fixed behaviour: a wrong guess is a flat -5 no matter when it lands.
    assert update_score(100, "Too High", attempt_number) == 95
    assert update_score(100, "Too Low", attempt_number) == 95


# ---------------------------------------------------------------------------
# update_score — edge cases around score value and outcome label
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("score", [0, -5, -1000, 10**9])
def test_penalty_applies_at_any_starting_score(score):
    # Nothing clamps at zero, so the score is free to run negative.
    assert update_score(score, "Too Low", 1) == score - 5


@pytest.mark.parametrize(
    "outcome",
    ["win", "WIN", "Too high", "TOO LOW", "toolow", "Win ", " Win", "", None, 0, True],
)
def test_outcome_matching_is_exact_and_unknown_labels_are_a_no_op(outcome):
    # Case- and whitespace-sensitive by design: a typo'd label silently
    # changes nothing rather than awarding or deducting points.
    assert update_score(42, outcome, 1) == 42


def test_score_survives_a_full_losing_round_then_a_win():
    # Integration: five wrong guesses then a win on attempt 6.
    score = 0
    for attempt in range(1, 6):
        outcome, _ = check_guess(10 * attempt, 55)
        score = update_score(score, outcome, attempt)
    assert score == -25

    outcome, _ = check_guess(55, 55)
    score = update_score(score, outcome, 6)
    assert outcome == "Win"
    assert score == -25 + 30


def test_parse_then_check_then_score_end_to_end():
    # The full path a submitted "42.9" takes through the app.
    ok, guess, err = parse_guess("42.9")
    assert (ok, guess, err) == (True, 42, None)
    outcome, message = check_guess(guess, 42)
    assert outcome == "Win"
    assert "Correct" in message
    assert update_score(0, outcome, 1) == 80
