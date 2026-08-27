# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The hints are interchange that is hints says "Go Lower" when the actual number is higher and vice versa.
The start new game key doesn't work when you are out of guesses or secret is found unless page is refreshed but starts a new game when you have some guess left
When you type an answer in the box you are been prompted to press "enter" key to guess but it doesn't submit
New game only refreshes guess count but does not clear the guess input box
After guessing the right number, final score shows incorrectly

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| 34    |Go LOWER           |Go HIGHER        |none                    |
|New Game|Clear guess box/32|Empty            |none
|(12)Score deduction| - 5       |-15          |none

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Claude Code
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
It suggest I interchange the condition statements for "Go HIGHER" and "Go LOWER"
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).


---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
