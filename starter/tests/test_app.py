import app as app_module


def test_index_route_returns_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_route_returns_puzzle(client):
    response = client.get('/new?clues=35')
    data = response.get_json()

    assert response.status_code == 200
    assert data is not None
    assert len(data['puzzle']) == 9
    assert all(len(row) == 9 for row in data['puzzle'])


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
    assert response.get_json() == {'incorrect': []}


def test_check_route_reports_incorrect_cell_coordinates(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 1 if board[0][0] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_route_reports_multiple_incorrect_cells(client):
    client.get('/new?clues=35')
    board = [row[:] for row in app_module.CURRENT['solution']]
    board[0][0] = 1 if board[0][0] != 1 else 2
    board[0][1] = 1 if board[0][1] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0], [0, 1]]
