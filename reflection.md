# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  - **The hints were switched.**
  - **The controls for pressing Enter were confusing.**
  - **Recorded data including the Attempts remaining and the Debug data were confusing.**
  - **Pressing New Game did not start a new game.**
  - **The Submit Guess button submits the guess, but the answer isn’t processed in the Debug Info or the attempt displays unless you change the typed text in the guess bar and either press the Enter key or click anywhere that isn’t the guess bar.**
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| A guess lower than the answer | The hint says Go HIGHER! | The hint says Go LOWER! | none |
| A guess higher than the answer | The hint says Go LOWER! | The hint says Go HIGHER! | none |
| Click New Game | A new game starts | A new game doesn't start | none |
| Player makes the first guess | Attempts left decreases | Attempts left doesn't decrease | none |
| Player types a guess and presses Enter | Hint appears, data updates | Previous hint disappears but the new one doesn't appear; data doesn't update | none |
| Player enters the wrong number for the last attempt | No hint appears because it's not needed | A hint appears | none |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - **Claude Code**
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - **I closely inspected the AI-coded tests to ensure they properly tested the fixed functionality.**
  - **I opened the app manually and tested out the fixed functionality as a user.**
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?
  - **I asked the AI to generate pytests for every modification made to the code, including in logic and in app display.**

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - **Streamlit reruns by executing the code from top to bottom. Streamlit reruns whenever a user interacts with the app.**
  - **Session state refers to the data contained in a run of the app. On one run, there could be 8 Attempts remaining, but after the user makes a guess, the app reruns, and on that next run, the state contains 7 Attempts remaining.**

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
