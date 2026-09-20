# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

1. The hints are interchange that is hints says "Go Lower" when the actual number is higher and vice versa.
2. The start new game key doesn't work when you are out of guesses or secret is found unless page is refreshed but starts a new game when you have some guess left
3. When you type an answer in the box you are been prompted to press "enter" key to guess but it doesn't submit
4. New game only refreshes guess count but does not clear the guess input box
5. After guessing the right number, final score shows incorrectly
6. The difficulty range should be easy(1-20), medium(1-50), hard(1-100) instead medium and hard are interchanged

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| 34    |Go LOWER           |Go HIGHER        |none                    |
|New Game|Game reset and guess input cleared|Guess count resets, but previous guess remains|none
|(12)Score deduction| - 5       |-15          |none
|Difficulty medium    |1-50         |1-100    |none

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Claude Code, Copilot
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
It suggest I interchange the condition statements for "Go HIGHER" and "Go LOWER"
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
It suggested since Mediumm difficulty range was 1-100, then hard difficulty should be 1-200 even though medium and hard difficulty ranges were just interchanged.



---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
I generated tests in test_game_logic.py and run pytest, I manually also run the app and verified. it was correct
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  I typed 20 and it return GO LOWER so I typed 15 and it says GO HIGHER and 13 and it says YOU WIN
- Did AI help you design or understand any tests? How?
  Yes, it did actually gave the test cases which upon verification took care of all edge cases.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
When a user press a button or check a box, the app forget everything and executes the entire Python scripts from line 1 all over again
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
I want to continue to refactor logics from the main big class so it's easily read and maintained
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  Also I would commit each step in the process so I always have a backup
- What is one thing you would do differently next time you work with AI on a coding task?
Next time I will be more skeptical about accepting AI changes as it hallucinates for example when it things hard difficulty should range 1-200 instead of 1-100
- In one or two sentences, describe how this project changed the way you think about AI generated code.
It can generate code per the instructions given but might hallucinate on where instruction are not clearer so it's always good to review before accepting.
