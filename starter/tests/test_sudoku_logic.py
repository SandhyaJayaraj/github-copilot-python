import sudoku_logic
import pytest


def is_complete_valid_board(board):
    expected = list(range(1, sudoku_logic.SIZE + 1))
    rows_valid = all(sorted(row) == expected for row in board)
    columns_valid = all(
        sorted(board[row][column] for row in range(sudoku_logic.SIZE)) == expected
        for column in range(sudoku_logic.SIZE)
    )
    boxes_valid = all(
        sorted(
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        )
        == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )
    return rows_valid and columns_valid and boxes_valid


def test_create_empty_board_returns_9_by_9_zero_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_does_not_modify_original_board():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 1

    assert board[0][0] == sudoku_logic.EMPTY


def test_is_safe_rejects_duplicate_in_row():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False


def test_is_safe_rejects_duplicate_in_column():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 1, 0, 5) is False


def test_is_safe_rejects_duplicate_in_3_by_3_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 1, 1, 5) is False


def test_is_safe_accepts_valid_candidate():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5) is True


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 45), ('medium', 35), ('hard', 30)],
)
def test_clues_for_difficulty_returns_expected_clue_count(
    difficulty, expected_clues
):
    assert sudoku_logic.clues_for_difficulty(difficulty) == expected_clues


def test_clues_for_difficulty_rejects_unknown_difficulty():
    with pytest.raises(ValueError):
        sudoku_logic.clues_for_difficulty('expert')


def test_fill_board_produces_complete_valid_solution():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert is_complete_valid_board(board)


def test_count_solutions_returns_one_for_complete_solution():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_stops_after_finding_multiple_solutions():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board, limit=2) == 2


def test_count_solutions_returns_zero_for_invalid_complete_board():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)
    board[0][1] = board[0][0]

    assert sudoku_logic.count_solutions(board) == 0


def test_remove_cells_removes_requested_number_of_cells():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)

    sudoku_logic.remove_cells(board, clues=35)

    empty_cells = sum(row.count(sudoku_logic.EMPTY) for row in board)
    assert empty_cells == sudoku_logic.SIZE * sudoku_logic.SIZE - 35


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert is_complete_valid_board(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35


def test_generated_puzzle_does_not_modify_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] == sudoku_logic.EMPTY:
                assert solution[row][column] != sudoku_logic.EMPTY


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert is_complete_valid_board(solution)


def test_generated_puzzle_preserves_prefilled_solution_values():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] != sudoku_logic.EMPTY:
                assert puzzle[row][column] == solution[row][column]


def test_generate_puzzle_rejects_invalid_clue_count():
    for clues in (-1, sudoku_logic.SIZE * sudoku_logic.SIZE + 1):
        try:
            sudoku_logic.generate_puzzle(clues)
        except ValueError:
            pass
        else:
            raise AssertionError('Expected invalid clue count to raise ValueError')


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 45), ('medium', 35), ('hard', 30)],
)
def test_generated_difficulty_puzzle_is_unique_and_has_expected_clues(
    difficulty, expected_clues
):
    puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == expected_clues
    assert sudoku_logic.count_solutions(puzzle) == 1
    assert is_complete_valid_board(solution)


def test_generate_puzzle_uses_bounded_retries(monkeypatch):
    attempts = 0

    def always_fail(board, clues):
        nonlocal attempts
        attempts += 1
        raise RuntimeError('forced generation failure')

    monkeypatch.setattr(sudoku_logic, 'remove_cells', always_fail)

    try:
        sudoku_logic.generate_puzzle(clues=35)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Expected bounded generation to raise RuntimeError')

    assert attempts == sudoku_logic.MAX_GENERATION_ATTEMPTS
