# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Test Generation (SF1)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Strings | modify the code so that the player loses an attempt only if they enter a valid guess / write pytests so that each test for valid guesses assert that the attempts increased, while each test for invalid guesses assert that the attempts didn't increase. | | yes | The answer can only be an integer, so the guesses should be too. |
| Empty guesses | modify the code so that the player loses an attempt only if they enter a valid guess / write pytests so that each test for valid guesses assert that the attempts increased, while each test for invalid guesses assert that the attempts didn't increase. | | yes | This feature is a safeguard for if the player accidentally submits the form when there's nothing in it. |
| Out of Range | is it possible to make another parse for the guesses that checks if the guess is within the range set by the difficulty, and if not, reject the guess and return a message remindiing the user what the range is? | | yes | The player shouldn't be led astray thinking their guesses can be certain numbers that they cannot be. |
| Decimals | can you modify this code so that entering a decimal number that isn't an integer raises an exception with a message saying to enter a whole number / write a pytest for this new functionality | @pytest.mark.parametrize("raw", ["3.5", "0.1", "-2.75", "99.999"]) def test_parse_guess_rejects_non_whole_decimals(raw): ok, value, err = parse_guess(raw); assert ok is False; assert value is None; assert err == "Please enter a whole number."; @pytest.mark.parametrize("raw, expected", [("3.", 3), ("42.0", 42), ("-7.0000", -7)]); def test_parse_guess_accepts_whole_number_decimals(raw, expected): ok, value, err = parse_guess(raw); assert ok is True; assert value == expected; assert err is None | yes | The answer can only be an integer, so the guesses should be too. |
| Repeat guesses | how easy would it be to modify the code to reject repeat guesses | | yes | Just another mercy feature for the player, preventing them from entering a guess that has already been found to be wrong.|

---