import copy
import random

SIZE = 9
EMPTY = 0
MAX_GENERATION_ATTEMPTS = 10
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 30,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count valid solutions, stopping once the limit is reached."""
    if limit < 1:
        return 0

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                solutions = 0
                for candidate in range(1, SIZE + 1):
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        solutions += count_solutions(board, limit - solutions)
                        board[row][col] = EMPTY
                        if solutions >= limit:
                            return solutions
                return solutions

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            board[row][col] = EMPTY
            if not is_safe(board, row, col, value):
                board[row][col] = value
                return 0
            board[row][col] = value
    return 1


def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    target_removals = SIZE * SIZE - clues
    removed = 0
    coordinates = [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
    ]
    random.shuffle(coordinates)

    for row, col in coordinates:
        if removed == target_removals:
            break

        value = board[row][col]
        if value == EMPTY:
            continue

        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            removed += 1
        else:
            board[row][col] = value

    if removed != target_removals:
        raise RuntimeError('Unable to generate a unique puzzle with this clue count')


def clues_for_difficulty(difficulty):
    try:
        return DIFFICULTY_CLUES[difficulty]
    except KeyError as error:
        raise ValueError('difficulty must be easy, medium, or hard') from error


def generate_puzzle(clues=35):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    for _ in range(MAX_GENERATION_ATTEMPTS):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        try:
            remove_cells(board, clues)
        except RuntimeError:
            continue
        puzzle = deep_copy(board)
        return puzzle, solution

    raise RuntimeError('Unable to generate a unique puzzle after bounded retries')


def generate_puzzle_for_difficulty(difficulty):
    return generate_puzzle(clues_for_difficulty(difficulty))
