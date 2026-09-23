# Sudoku Project Instructions

## Project Overview

This project is a Sudoku game built using Flask that will need
to be refactored from old Python code into a well-structured and
maintainable app.

Your final application must include:

- Easy, medium and hard difficulty levels;
- Unique solutions to all Sudoku puzzles;
- Locked prefilled cells;
- Real-time feedback in case of an incorrect move;
- Check functionality;
- Hint functionality;
- Completion check functionality;
- Timer;
- Top 10 leaderboard;
- Persistence using LocalStorage;
- Light and dark theme;
- Mobile-first design;
- Alternating color scheme for the 3x3 Sudoku box.

## Development Best Practices

- Try to keep the current functionality unless specified otherwise
  by the requirements;
- Code should be written in readable Python;
- Use modular and reusable functions;
- Separate Sudoku logic from Flask routes;
- Avoid unnecessary use of global variables;
- Use clear variable names;
- Use clear function names;
- Use concise comments for non-obvious logic, clear function names, modular
  reusable functions, and consistent error handling;
- Add comments only when they add value;
- Gracefully handle errors;
- Avoid duplication of logic where possible.

## Python Best Practices

- Follow PEP 8 guidelines;
- Use type hints where appropriate;
- Functions should do one thing;
- Write maintainable and testable code;
- Use no unnecessary dependencies.

## Flask Standards

- Routes should be structured properly.
- Distinguish business/game logic from HTTP communication.
- Use templates for rendering.
- Use CSS/JS in a way that is separated from HTML.

## Testing

- Create automated tests before refactoring.
- Run all tests after every feature implementation or refactoring.
- Never change any tests just to make failing tests pass.
- Test both ordinary and edge cases.

## Sudoku Requirements

- Any generated puzzle should have one unique solution.
- Difficulties should be regulated through the number of prefilled fields.
- Prefilled cells should be fixed.
- All user inputs should be validated.
- All invalid entries should be provided with appropriate feedback.
- Hints should provide a valid answer and fix the field.
- Valid completion should prompt the message about that.

## Frontend Requirements

- Interface should be functional on mobile and desktop.
- There should be support for light and dark mode.
- Text and controls should be readable in both modes.
- Alternate colors of 3x3 Sudoku squares.
- Avoid layout shifts while playing the game.
- Make use of accessible labels, buttons, and form controls.

## GitHub Copilot Recommendations

The Copilot recommendations should be verified before accepting them.

Do not blindly accept the recommendations produced by the Copilot.

In case there is confusion about the recommendation,
1. Seek an explanation from Copilot.
2. See whether it meets the requirements of the project.
3. Test the code recommendation.
4. Reject or modify the recommendation.

While doing major modifications, make them one-by-one
and test the application after each modification.