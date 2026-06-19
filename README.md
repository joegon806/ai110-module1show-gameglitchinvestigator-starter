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

- [x] Describe the game's purpose.
   - **The game is to guess the secret number. For each guess, you are told if the answer is higher or lower than your guess.**
- [x] Detail which bugs you found.
   - **The hints are backwards, where guesses higher than the answer say you should go higher, and guesses lower than the answer say you should go lower.**
   - **Clicking New Game doesn’t start a new game.**
   - **Attempts left starts at 7 and stays at 7 after the first guess before counting down for other guesses, and the game finishes while Attempts left says 1.**
   - **In Debug Info, Attempts starts at 1 instead of 0, although the number becomes 1 after one attempt and counts up afterwards as expected.**
   - **Attempts Allowed on the sidebar is 1 higher than the actual attempts allowed.**
   - **Guesses add to History after the next guess instead of after being guessed.**
   - **The Submit Guess button submits the guess, but the answer isn’t processed in the Debug Info or the attempt displays unless you change the typed text in the guess bar and either press the Enter key or click anywhere that isn’t the guess bar.**
   - **Sometimes the secret number gets converted to a string.**
   - **A hint is still shown after the last guess.**
   - **Confusing scoring algorithm.**
   - **If the user selects a new difficulty, the game continues with the same secret. (Problematic if the previous game has an answer out of range of the new difficulty's limit)**
   - **Edge Cases:**
      - **Guesses that except a TypeError (Strings, empty guesses) still get compared and processed in the Debug info (i.e. decreases attempts).**
      - **Guesses that are out of range, decimal values, or repeats are still accepted.**
- [x] Explain what fixes you applied.
   - **switched the hints around and made them conditional to only the guess**
   - **made the New Game button start a new game**
   - **made the number of attempts set to 0 at the start of a new game**
   - **made the debug data update after the latest guess instead of after the guess after it**
   - **made the guess bar a form so that the Enter key could be used to submit a guess**
   - **removed the string conversion of the answer**
   - **prevented the hint from being shown after the last attempt**
   - **redesigned the scoring algorithm**
   - **made the game restart if the user changes the difficulty.**
   - **guesses are acceptable only if they're integers, in range, and not repeated**
   - **made the attempts amount decreased only on valid guesses and not on invalid guesses**
   - **made the "Guess a number" bar display only when the game is playing**

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Select a difficulty from the Difficulty dropdown menu on the left side, if wanted.
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

## 🧪 Test Results

```
tests\test_game_logic.py ..................................................................................................... [100%]
========================= 106 passed in 11.30s =========================
```