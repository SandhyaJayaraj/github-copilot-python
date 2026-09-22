import pytest

import app as app_module


def test_index_route_returns_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="hint"' in response.data
    assert b'id="timer"' in response.data
    assert b'id="score-form"' in response.data
    assert b'id="leaderboard-body"' in response.data
    assert b'id="theme-toggle"' in response.data


def test_stylesheet_contains_theme_and_responsive_grid_rules(client):
    response = client.get('/static/styles.css')
    stylesheet = response.data

    assert response.status_code == 200
    assert b'[data-theme="dark"]' in stylesheet
    assert b'--box-a' in stylesheet
    assert b'--box-b' in stylesheet
    assert b'.sudoku-row:nth-child(-n+3)' in stylesheet
    assert b'.sudoku-row:nth-child(n+7)' in stylesheet
    assert b'@media (max-width: 520px)' in stylesheet


def test_new_route_returns_puzzle(client):
    response = client.get('/new?clues=35')
    data = response.get_json()

    assert response.status_code == 200
    assert data is not None
    assert data['difficulty'] == 'medium'
    assert len(data['puzzle']) == 9
    assert all(len(row) == 9 for row in data['puzzle'])


def test_new_route_defaults_to_medium_difficulty(client):
    response = client.get('/new')

    assert response.status_code == 200
    assert response.get_json()['difficulty'] == 'medium'
    assert sum(
        cell != 0
        for row in response.get_json()['puzzle']
        for cell in row
    ) == 35


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 45), ('medium', 35), ('hard', 30)],
)
def test_new_route_generates_selected_difficulty(
    client, difficulty, expected_clues
):
    response = client.get(f'/new?difficulty={difficulty}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['difficulty'] == difficulty
    assert sum(cell != 0 for row in data['puzzle'] for cell in row) == expected_clues


def test_new_route_rejects_unknown_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'difficulty must be easy, medium, or hard'
    }


def test_new_route_stores_current_game(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    assert app_module.CURRENT['puzzle'] == response.get_json()['puzzle']
    assert app_module.CURRENT['solution'] is not None


def test_check_route_without_active_game_returns_error(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_route_returns_no_incorrect_cells_for_solution(client):
    client.get('/new?clues=35')

    response = client.post('/check', json={'board': app_module.CURRENT['solution']})

    assert response.status_code == 200
    data = response.get_json()
    assert 'correct' not in data
    assert data['incorrect'] == []
    assert data['complete'] is True


def test_check_route_does_not_complete_with_empty_cells(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 0

    response = client.post('/check', json={'board': board})
    data = response.get_json()

    assert response.status_code == 200
    assert data['incorrect'] == []
    assert data['complete'] is False


def test_check_route_returns_incorrect_cells_without_solution_metadata(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 1 if board[0][0] != 1 else 2
    board[0][1] = 0

    response = client.post('/check', json={'board': board})
    data = response.get_json()

    assert response.status_code == 200
    assert data['incorrect'] == [[0, 0]]
    assert data['complete'] is False


def test_check_route_reports_incorrect_cell_coordinates(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 1 if board[0][0] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == [[0, 0]]
    assert data['complete'] is False


def test_check_route_reports_multiple_incorrect_cells(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 1 if board[0][0] != 1 else 2
    board[0][1] = 1 if board[0][1] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == [[0, 0], [0, 1]]
    assert data['complete'] is False


def test_hint_route_returns_one_empty_cell_and_correct_value(client):
    client.get('/new?clues=35')
    puzzle = app_module.CURRENT['puzzle']
    board = [row[:] for row in puzzle]

    response = client.post('/hint', json={'board': board})
    data = response.get_json()

    assert response.status_code == 200
    row, col = data['row'], data['col']
    assert puzzle[row][col] == 0
    assert data['value'] == app_module.CURRENT['solution'][row][col]


def test_hint_route_does_not_return_already_filled_cell(client):
    client.get('/new?clues=35')
    puzzle = app_module.CURRENT['puzzle']
    board = [row[:] for row in puzzle]
    empty_cells = [
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    ]
    first_row, first_col = empty_cells[0]
    board[first_row][first_col] = app_module.CURRENT['solution'][first_row][first_col]

    response = client.post('/hint', json={'board': board})
    data = response.get_json()

    assert response.status_code == 200
    assert (data['row'], data['col']) != (first_row, first_col)


def test_hint_route_requires_active_game(client):
    response = client.post('/hint', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}
