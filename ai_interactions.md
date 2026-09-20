# AI Interactions Log




### Prompt used

```
I want to complete an advanced edge-case testing challenge. Please generate a suite of
pytest cases for my parse_guess and update_score functions in logic_utils.py. Include at
least three complex edge cases, such as:

- A user entering a negative number or zero.
- A user entering a decimal/float string (e.g., '3.14').
- A user entering a non-numeric string or special characters.

Also, provide a one-line explanation of why each edge case was chosen so I can paste it
into my ai_interactions.md.
```

### Follow-up instruction given to the assistant

```
Write the assertions against what the functions actually do, not what they ideally
should do. Probe the real behaviour first. If a test would expose a genuine gap rather
than a passing property, mark it xfail(strict=True) instead of asserting the buggy value,
and tell me about it.
```

### Result

All generated tests live in `tests/test_edge_cases.py` (76 cases, kept separate from the
42 cases in `tests/test_game_logic.py` that cover the original Phase 1 bugs).
Full suite: **117 passed, 1 xfailed** — the terminal output is pasted in `README.md`.

### The three required edge cases

| Edge Case | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------------|--------------|----------------|
| Negative number or zero | `test_negative_and_zero_parse_as_valid_numbers` | Yes | `parse_guess` is a parser, not a validator — `"0"` and `"-5"` sit outside every difficulty's 1..N range yet still return `ok=True`, so nothing in the app ever rejects them. |
| Decimal / float string (`"3.14"`) | `test_decimal_strings_are_truncated_not_rounded` | Yes | `int(float(x))` truncates instead of rounding, so `"3.99"` silently becomes 3 and a near-miss guess is altered before it is ever compared to the secret. |
| Non-numeric string or special characters | `test_non_numeric_input_returns_error_and_never_raises` | Yes | Letters, symbols, emoji and injection-style strings must all return the error tuple rather than raise, because an uncaught exception here would crash the Streamlit rerun. |

### Additional edge cases generated

| Edge Case | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------------|--------------|----------------|
| Out-of-range guess reaches scoring | `test_out_of_range_guess_is_not_rejected_anywhere` | Yes | Proves the consequence of the missing validation: `"-999"` flows through `check_guess` and costs the player a real 5 points. |
| Negative decimal (`"-3.99"`) | `test_negative_decimals_truncate_toward_zero_not_down` | Yes | Truncation runs toward zero, so the rounding direction flips with the input's sign — exactly the asymmetry that hides off-by-one bugs. |
| Lone `"."` | `test_lone_dot_is_rejected` | Yes | Input that satisfies the `"." in raw` branch but makes `float()` raise, confirming the dot check cannot be trusted as a validity test. |
| `"1e3"` vs `"1.5e2"` | `test_scientific_notation_without_a_dot_is_rejected` | Yes | Two equivalent notations get opposite verdicts purely because the float path is gated on a dot — inconsistent handling of the same concept. |
| Overflow / `inf` / `nan` | `test_infinity_and_overflow_are_rejected_not_crashed` | Yes | `int(float("1.0e999"))` raises `OverflowError`, not `ValueError`, so this verifies the broad `except Exception` is genuinely load-bearing. |
| Whitespace-only input | `test_whitespace_only_is_not_treated_as_empty` | Yes | `"   "` slips past the `raw == ""` check, so a space-bar submission shows the wrong message ("That is not a number." instead of "Enter a guess."). |
| Empty string and `None` | `test_empty_and_missing_input_get_the_prompt_message` | Yes | These two mean "you typed nothing", which is user guidance rather than a parse error, and must keep their distinct message. |
| Stray whitespace / leading `+` | `test_surrounding_whitespace_and_plus_sign_are_tolerated` | Yes | Copy-pasted input carries spaces and newlines; confirms real users are not punished for invisible characters. |
| Unicode digits and underscores | `test_python_int_quirks_accept_more_than_ascii_digits` | Yes | `int()` accepts PEP 515 underscores and any Unicode decimal, so `"1_0"` and `"٣"` reach the game as real numbers — surprising, and worth pinning before someone "fixes" it. |
| Non-string argument types | `test_non_string_inputs_fail_cleanly` | Yes | `"." in raw` raises `TypeError` on an int or bool, so this proves a non-string caller gets the error tuple instead of a stack trace. |
| Extremely large value (40 digits) | `test_very_large_number_is_accepted` | Yes | Python ints are unbounded, so there is no overflow to defend against — documents that the absence of a size guard is safe here. |
| `attempt_number = 0` | `test_win_award_is_floored_at_ten` | Yes | Reachable in practice: the New Game button resets `attempts` to 0, so attempt 0 is a live input, not a hypothetical. |
| Win award monotonicity | `test_win_award_never_increases_with_more_attempts` | Yes | A property test across attempts 0–24 — taking longer must never pay better, which catches any future change to the award formula. |
| **Negative `attempt_number`** | `test_negative_attempt_number_should_not_inflate_the_award` | **No — xfail (known gap)** | `update_score(0, "Win", -5)` returns 140, beating the 90-point maximum; marked `strict=True` so it becomes a hard failure once a guard is added. |
| Penalty vs. attempt number | `test_penalty_ignores_the_attempt_number_entirely` | Yes | Directly guards the fixed parity bug — the -5 must stay flat across attempts 0, 1, 50 and -3. |
| Score at extreme values | `test_penalty_applies_at_any_starting_score` | Yes | Nothing clamps at zero, so the test records that a negative running score is intended behaviour, not a bug to "fix" later. |
| Mis-cased / padded outcome labels | `test_outcome_matching_is_exact_and_unknown_labels_are_a_no_op` | Yes | `"win"`, `"Win "`, `None` and `True` must all be no-ops — a typo'd label should change nothing rather than silently award points. |
| Full losing round then a win | `test_score_survives_a_full_losing_round_then_a_win` | Yes | Chains `check_guess` into `update_score` over six attempts, catching sign errors that only appear once penalties and awards accumulate together. |
| End-to-end `"42.9"` | `test_parse_then_check_then_score_end_to_end` | Yes | Follows one realistic submission through all three functions, verifying truncation to 42 still registers as a win against secret 42. |

### What I had to verify manually

- The assistant probed the real return values before writing assertions, so the suite
  documents actual behaviour rather than assumed behaviour. I re-ran `pytest` myself to
  confirm the 117/1 result.
- Two genuine gaps came out of this, and I chose to record rather than "fix" both,
  because neither is reachable from the current UI:
  1. **No range validation.** `parse_guess("-999")` returns `ok=True` and `app.py` never
     bounds the guess against `low`/`high`, so an impossible guess is scored as an
     ordinary wrong guess.
  2. **Unvalidated `attempt_number`.** A negative attempt inflates the win award. This is
     the single `xfail`.
