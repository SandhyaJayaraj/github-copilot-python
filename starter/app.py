from flask import Flask, render_template, jsonify, request
import random
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    if 'difficulty' in request.args:
        try:
            puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(
                difficulty
            )
        except ValueError as error:
            return jsonify({'error': str(error)}), 400
    else:
        clues = int(request.args.get('clues', 35))
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    incomplete = False
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                incomplete = True
                continue
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    complete = not incorrect and not incomplete
    return jsonify({
        'incorrect': incorrect,
        'incomplete': incomplete,
        'complete': complete,
    })


@app.route('/hint', methods=['POST'])
def provide_hint():
    data = request.json or {}
    board = data.get('board')
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_cells = [
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] == sudoku_logic.EMPTY
        and board[row][col] == sudoku_logic.EMPTY
    ]
    if not empty_cells:
        return jsonify({'error': 'No empty cells available for a hint'}), 400

    row, col = random.choice(empty_cells)
    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col],
    })

if __name__ == '__main__':
    app.run(debug=True)