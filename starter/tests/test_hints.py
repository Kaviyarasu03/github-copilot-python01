"""Tests for the Sudoku hint endpoint."""
import json

import app


def post_hint(client, row=0, col=0):
    return client.post(
        '/hint',
        data=json.dumps({'row': row, 'col': col}),
        content_type='application/json'
    )


def find_empty_cell(puzzle):
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                return row, col
    raise AssertionError('Generated puzzle has no empty cells')


class TestHintEndpoint:
    def test_hint_returns_solution_value_for_empty_cell(self, client):
        client.get('/new?difficulty=easy')
        row, col = find_empty_cell(app.CURRENT['puzzle'])

        response = post_hint(client, row, col)
        data = response.get_json()

        assert response.status_code == 200
        assert data == {
            'row': row,
            'col': col,
            'value': app.CURRENT['solution'][row][col]
        }

    def test_hint_rejects_prefilled_cell(self, client):
        client.get('/new')
        puzzle = app.CURRENT['puzzle']
        row, col = next(
            (row, col)
            for row in range(9)
            for col in range(9)
            if puzzle[row][col] != 0
        )

        response = post_hint(client, row, col)

        assert response.status_code == 400
        assert 'empty cell' in response.get_json()['error'].lower()

    def test_hint_requires_selected_cell(self, client):
        client.get('/new')

        response = client.post(
            '/hint',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert 'empty cell' in response.get_json()['error'].lower()

    def test_hint_requires_game_in_progress(self, client):
        response = post_hint(client, 0, 0)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'No game in progress'

    def test_hint_rejects_invalid_position(self, client):
        client.get('/new')

        response = post_hint(client, 9, 0)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'Invalid cell position'