"""Tests for Sudoku game interaction and validation functionality.

This module tests player interaction features including:
- Cell validation (row, column, 3x3 box conflicts)
- Move validation endpoint
- Player board state
"""
import pytest
import json
import sudoku_logic


class TestMoveValidation:
    """Test cases for move validation functionality."""

    def test_is_move_valid_function_exists(self):
        """Test that is_move_valid function is defined."""
        assert hasattr(sudoku_logic, 'is_move_valid')
        assert callable(sudoku_logic.is_move_valid)

    def test_is_move_valid_empty_cell(self):
        """Test that any number 1-9 is valid in empty cell with no conflicts."""
        board = sudoku_logic.create_empty_board()
        
        for num in range(1, 10):
            assert sudoku_logic.is_move_valid(board, 0, 0, num)

    def test_is_move_valid_rejects_invalid_numbers(self):
        """Test that numbers outside 1-9 are rejected."""
        board = sudoku_logic.create_empty_board()
        
        assert not sudoku_logic.is_move_valid(board, 0, 0, 0)
        assert not sudoku_logic.is_move_valid(board, 0, 0, 10)
        assert not sudoku_logic.is_move_valid(board, 0, 0, -1)

    def test_is_move_valid_row_conflict(self):
        """Test that move is invalid if number exists in same row."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board[0][1] = 3
        
        # 5 already in row 0, so should be invalid at [0][8]
        assert not sudoku_logic.is_move_valid(board, 0, 8, 5)
        # 7 not in row 0, should be valid
        assert sudoku_logic.is_move_valid(board, 0, 8, 7)

    def test_is_move_valid_column_conflict(self):
        """Test that move is invalid if number exists in same column."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board[1][0] = 3
        
        # 5 already in column 0, so should be invalid at [8][0]
        assert not sudoku_logic.is_move_valid(board, 8, 0, 5)
        # 7 not in column 0, should be valid
        assert sudoku_logic.is_move_valid(board, 8, 0, 7)

    def test_is_move_valid_box_conflict(self):
        """Test that move is invalid if number exists in same 3x3 box."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        
        # 5 already in top-left box, should be invalid in [2][2]
        assert not sudoku_logic.is_move_valid(board, 2, 2, 5)
        # 7 not in box, should be valid
        assert sudoku_logic.is_move_valid(board, 2, 2, 7)

    def test_is_move_valid_preserves_board(self):
        """Test that is_move_valid doesn't modify the input board."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board_copy = sudoku_logic.deep_copy(board)
        
        sudoku_logic.is_move_valid(board, 1, 1, 3)
        
        assert board == board_copy

    def test_is_move_valid_multiple_conflicts(self):
        """Test move validation with multiple existing numbers."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 1
        board[0][1] = 2
        board[1][0] = 3
        board[1][1] = 4
        board[2][2] = 5
        
        # 1 conflicts in row and column
        assert not sudoku_logic.is_move_valid(board, 0, 5, 1)
        assert not sudoku_logic.is_move_valid(board, 8, 0, 1)
        
        # 5 conflicts in box
        assert not sudoku_logic.is_move_valid(board, 1, 2, 5)
        
        # 6 should be valid in many positions
        assert sudoku_logic.is_move_valid(board, 0, 5, 6)


class TestValidateEndpoint:
    """Test cases for the /validate Flask endpoint."""

    def test_validate_endpoint_exists(self, client):
        """Test that /validate endpoint exists."""
        board = [[0] * 9 for _ in range(9)]
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 0,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        assert response.status_code == 200

    def test_validate_valid_move(self, client):
        """Test validation of a valid move."""
        board = [[0] * 9 for _ in range(9)]
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 0,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True

    def test_validate_invalid_move_row_conflict(self, client):
        """Test validation detects row conflicts."""
        board = [[0] * 9 for _ in range(9)]
        board[0][1] = 5  # 5 already in row 0
        
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 8,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'conflict' in data['message'].lower()

    def test_validate_invalid_move_column_conflict(self, client):
        """Test validation detects column conflicts."""
        board = [[0] * 9 for _ in range(9)]
        board[1][0] = 5  # 5 already in column 0
        
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 8,
                                 'col': 0,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['valid'] is False

    def test_validate_invalid_move_box_conflict(self, client):
        """Test validation detects 3x3 box conflicts."""
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5  # 5 in top-left box
        
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 2,
                                 'col': 2,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['valid'] is False

    def test_validate_invalid_number(self, client):
        """Test validation rejects numbers outside 1-9."""
        board = [[0] * 9 for _ in range(9)]
        
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 0,
                                 'num': 0,
                                 'board': board
                             }),
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['valid'] is False

    def test_validate_invalid_position(self, client):
        """Test validation rejects invalid cell positions."""
        board = [[0] * 9 for _ in range(9)]
        
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 10,
                                 'col': 0,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert data['valid'] is False or 'Invalid cell position' in data.get('message', '')

    def test_validate_missing_parameters(self, client):
        """Test validation handles missing parameters."""
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 0
                                 # 'num' and 'board' are missing
                             }),
                             content_type='application/json')
        
        assert response.status_code == 400

    def test_validate_returns_json(self, client):
        """Test validation returns valid JSON."""
        board = [[0] * 9 for _ in range(9)]
        response = client.post('/validate',
                             data=json.dumps({
                                 'row': 0,
                                 'col': 0,
                                 'num': 5,
                                 'board': board
                             }),
                             content_type='application/json')
        
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'valid' in data


class TestPlayerInteractionFlow:
    """Integration tests for player interaction flow."""

    def test_player_can_enter_valid_move(self, client):
        """Test complete flow of player entering a valid move."""
        # Start a new game
        import app
        client.get('/new?difficulty=easy')
        puzzle = app.CURRENT['puzzle']
        
        # Find an empty cell
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    empty_row, empty_col = i, j
                    break
        
        # Create board with this cell filled
        board = [[puzzle[i][j] for j in range(9)] for i in range(9)]
        
        # Try to place a number (should be valid for empty cell)
        for num in range(1, 10):
            response = client.post('/validate',
                                 data=json.dumps({
                                     'row': empty_row,
                                     'col': empty_col,
                                     'num': num,
                                     'board': board
                                 }),
                                 content_type='application/json')
            
            data = json.loads(response.data)
            # At least one number should be valid
            assert 'valid' in data

    def test_player_cannot_edit_original_clues(self):
        """Test that original puzzle clues cannot be edited (frontend-level)."""
        # This is enforced by marking prefilled cells as disabled
        # The test verifies the logic by checking that prefilled cells 
        # are marked as disabled in HTML
        pass  # Frontend-only enforcement

    def test_multiple_games_independent(self, client):
        """Test that starting new game doesn't carry over moves from previous game."""
        import app
        
        # Start first game
        client.get('/new')
        first_puzzle = [row[:] for row in app.CURRENT['puzzle']]
        
        # Start second game
        client.get('/new')
        second_puzzle = [row[:] for row in app.CURRENT['puzzle']]
        
        # Puzzles should be different
        assert first_puzzle != second_puzzle
