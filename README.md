# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [ ] Describe the game's purpose.
   This game is to give the user attempts to guess a secret number while giving guides after each entry to assist them get it right
- [ ] Detail which bugs you found.
1. The hints are interchange that is hints says "Go Lower" when the actual number is higher and vice versa.
2. The start new game key doesn't work when you are out of guesses or secret is found unless page is refreshed but starts a new game when you have some guess left
3. When you type an answer in the box you are been prompted to press "enter" key to guess but it doesn't submit
4. New game only refreshes guess count but does not clear the guess input box
5. After guessing the right number, final score shows incorrectly
6. The difficulty range should be easy(1-20), medium(1-50), hard(1-100) instead medium and hard are interchanged
- [ ] Explain what fixes you applied.
The hint displays correctly when user types in incorrect answer, either to go higher or lower if the value is smaller or greater respectively.
Made the medium range 1-50 and hard range 1- 100
In the score section, made the subtraction of points no matter the wrong input same.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User enters a guess of 65
2. Game returns "Go LOWER"
3. User enters a guess of 58 → "Go HIGHER"
4. User enters a guess of 59 - "Correct!"
5. Game ends "You won! The secret is 13. Final score:50"

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->
![alt text](image.png)

## 🧪 Test Results

Two suites run from the project root with `python -m pytest`:

- `tests/test_game_logic.py` — 42 cases covering the three logic bugs found in Phase 1
  (backwards hints, swapped Normal/Hard ranges, parity-flipping score penalty).
- `tests/test_edge_cases.py` — 76 cases added for Stretch Challenge 1, probing the
  boundaries of `parse_guess` and `update_score`.

```
======================================= test session starts ========================================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/gabrielanokye/AI Engineer/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 118 items

tests/test_edge_cases.py ......................................................x............ [ 56%]
.........                                                                                    [ 64%]
tests/test_game_logic.py ..........................................                          [100%]

===================================== short test summary info ======================================
XFAIL tests/test_edge_cases.py::test_negative_attempt_number_should_not_inflate_the_award - KNOWN GAP: attempt_number is never validated, so a negative attempt inflates the win award above the first-attempt maximum.
================================== 117 passed, 1 xfailed in 0.07s ==================================
```

### About the one `xfail`

That single `x` is not a failure and does not break the build — it is a deliberate
marker for a gap the edge-case tests uncovered. `update_score` never validates
`attempt_number`, so a negative attempt inflates the win award:
`update_score(0, "Win", -5)` returns **140**, which beats the 90-point first-attempt
maximum. The case is not reachable from the current UI (the attempt counter only ever
goes up), so the game logic was left alone. The test is marked `strict=True`, which
means it will convert into a hard failure the moment a guard is added — the fix cannot
be forgotten.

![alt text](image-1.png)


## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
