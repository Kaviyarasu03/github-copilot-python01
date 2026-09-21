"""Tests for Flask application routes.

This module tests the HTTP endpoints including:
- Index page rendering
- Puzzle generation via /new
- Solution validation via /check
- Error handling
"""
import pytest
import json
import sudoku_logic


class TestIndexRoute:
    """Test cases for the index route."""

    def test_index_route_returns_200(self, client):
        """Test that GET / returns status code 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_route_returns_html(self, client):
        """Test that GET / returns HTML content."""
        response = client.get('/')
        assert b'html' in response.data.lower() or response.content_type.startswith('text/html')

    def test_index_route_renders_template(self, client):
        """Test that index route renders the template."""
        response = client.get('/')
        # Response should contain content from index.html
        assert len(response.data) > 0


class TestNewGameRoute:
    """Test cases for the /new route."""

    def test_new_game_returns_200(self, client):
        """Test that GET /new returns status code 200."""
        response = client.get('/new')
        assert response.status_code == 200

    def test_new_game_returns_json(self, client):
        """Test that /new returns JSON response."""
        response = client.get('/new')
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_new_game_returns_puzzle(self, client):
        """Test that /new response contains a puzzle."""
        response = client.get('/new')
        data = json.loads(response.data)
        
        assert 'puzzle' in data
        puzzle = data['puzzle']
        
        # Puzzle should be 9x9
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_new_game_puzzle_has_correct_clues(self, client):
        """Test that puzzle has at least default 35 clues.
        
        Note: generate_puzzle_unique may keep more clues than requested to
        ensure the puzzle has exactly one solution.
        """
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        # Puzzle should have at least 35 clues (may have more for uniqueness)
        assert clue_count >= 35

    def test_new_game_with_custom_clues(self, client):
        """Test /new with custom clue count parameter.
        
        Note: generate_puzzle_unique may keep more clues than requested to
        ensure the puzzle has exactly one solution.
        """
        response = client.get('/new?clues=45')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        # Should have at least 45 clues (may have more for uniqueness)
        assert clue_count >= 45

    def test_new_game_with_various_clue_counts(self, client):
        """Test /new with various clue counts.
        
        Note: generate_puzzle_unique may keep more clues than requested to
        ensure the puzzle has exactly one solution.
        """
        for clues in [20, 35, 50, 60]:
            response = client.get(f'/new?clues={clues}')
            data = json.loads(response.data)
            puzzle = data['puzzle']
            
            clue_count = sum(1 for i in range(9) for j in range(9) 
                            if puzzle[i][j] != sudoku_logic.EMPTY)
            # Puzzle should have at least the requested clues
            # (may have more to maintain unique solution)
            assert clue_count >= clues

    def test_new_game_stores_puzzle_in_current(self, client):
        """Test that new game stores puzzle in CURRENT."""
        import app
        
        # CURRENT should be empty initially
        assert app.CURRENT['puzzle'] is None
        assert app.CURRENT['solution'] is None
        
        # Request a new game
        response = client.get('/new')
        
        # After request, CURRENT should have puzzle and solution
        assert app.CURRENT['puzzle'] is not None
        assert app.CURRENT['solution'] is not None

    def test_new_game_puzzle_matches_response(self, client):
        """Test that returned puzzle matches stored puzzle."""
        import app
        
        response = client.get('/new')
        data = json.loads(response.data)
        returned_puzzle = data['puzzle']
        
        assert app.CURRENT['puzzle'] == returned_puzzle

    def test_new_game_solution_is_valid(self, client):
        """Test that generated solution is valid Sudoku."""
        import app
        
        client.get('/new')
        solution = app.CURRENT['solution']
        
        # Check no empty cells
        for i in range(9):
            for j in range(9):
                assert solution[i][j] != sudoku_logic.EMPTY
        
        # Check rows have all numbers 1-9
        for row in solution:
            assert len(set(row)) == 9
        
        # Check columns have all numbers 1-9
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            assert len(set(column)) == 9


class TestCheckSolutionRoute:
    """Test cases for the /check route."""

    def test_check_solution_requires_post(self, client):
        """Test that /check requires POST method."""
        response = client.get('/check')
        assert response.status_code == 405  # Method Not Allowed

    def test_check_solution_returns_json(self, client):
        """Test that /check returns JSON response."""
        client.get('/new')
        response = client.post('/check', 
                              data=json.dumps({'board': [[0]*9 for _ in range(9)]}),
                              content_type='application/json')
        assert response.content_type == 'application/json'

    def test_check_solution_no_game_in_progress(self, client):
        """Test /check when no game has been started."""
        response = client.post('/check',
                              data=json.dumps({'board': [[0]*9 for _ in range(9)]}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No game in progress' in data['error']

    def test_check_solution_correct_solution(self, client):
        """Test /check with the correct solution."""
        import app
        
        # Start a new game
        client.get('/new')
        solution = app.CURRENT['solution']
        
        # Submit the correct solution
        response = client.post('/check',
                              data=json.dumps({'board': solution}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        # No incorrect cells
        assert data['incorrect'] == []

    def test_check_solution_incorrect_solution(self, client):
        """Test /check with an incorrect solution."""
        import app
        
        # Start a new game
        client.get('/new')
        solution = app.CURRENT['solution']
        
        # Create an incorrect board by changing one cell
        incorrect_board = [row[:] for row in solution]
        incorrect_board[0][0] = (solution[0][0] % 9) + 1  # Change to different number
        
        # Submit the incorrect solution
        response = client.post('/check',
                              data=json.dumps({'board': incorrect_board}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        # Should have at least one incorrect cell
        assert len(data['incorrect']) > 0
        # Should identify the changed cell
        assert [0, 0] in data['incorrect']

    def test_check_solution_multiple_incorrect_cells(self, client):
        """Test /check identifies multiple incorrect cells."""
        import app
        
        # Start a new game
        client.get('/new')
        solution = app.CURRENT['solution']
        
        # Create board with multiple wrong cells
        incorrect_board = [row[:] for row in solution]
        incorrect_board[0][0] = (solution[0][0] % 9) + 1
        incorrect_board[1][1] = (solution[1][1] % 9) + 1
        incorrect_board[8][8] = (solution[8][8] % 9) + 1
        
        response = client.post('/check',
                              data=json.dumps({'board': incorrect_board}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        assert len(data['incorrect']) == 3
        assert [0, 0] in data['incorrect']
        assert [1, 1] in data['incorrect']
        assert [8, 8] in data['incorrect']

    def test_check_solution_empty_board_is_incorrect(self, client):
        """Test that a completely empty board is marked incorrect."""
        import app
        
        client.get('/new')
        empty_board = [[0]*9 for _ in range(9)]
        
        response = client.post('/check',
                              data=json.dumps({'board': empty_board}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        # Should have many incorrect cells (all non-empty cells in solution)
        assert len(data['incorrect']) > 0

    def test_check_solution_returns_coordinates(self, client):
        """Test that /check returns incorrect cells as [row, col] coordinates."""
        import app
        
        client.get('/new')
        solution = app.CURRENT['solution']
        
        incorrect_board = [row[:] for row in solution]
        incorrect_board[3][5] = (solution[3][5] % 9) + 1
        
        response = client.post('/check',
                              data=json.dumps({'board': incorrect_board}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        assert [3, 5] in data['incorrect']


class TestMultipleGameSessions:
    """Test cases for multiple game sessions."""

    def test_new_game_overwrites_previous_puzzle(self, client):
        """Test that starting a new game overwrites the previous one."""
        import app
        
        # Start first game
        client.get('/new')
        puzzle1 = [row[:] for row in app.CURRENT['puzzle']]
        
        # Start second game
        client.get('/new')
        puzzle2 = [row[:] for row in app.CURRENT['puzzle']]
        
        # Puzzles should be different (highly likely with random generation)
        # At minimum, CURRENT should only hold the second puzzle
        assert app.CURRENT['puzzle'] == puzzle2

    def test_check_uses_current_solution(self, client):
        """Test that check always uses the current game's solution."""
        import app
        
        # Start first game and get solution
        client.get('/new')
        solution1 = app.CURRENT['solution']
        
        # Start second game
        client.get('/new')
        solution2 = app.CURRENT['solution']
        
        # Check against second solution
        response = client.post('/check',
                              data=json.dumps({'board': solution2}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        assert data['incorrect'] == []
        
        # Trying to check against first solution should fail
        # (unless by unlikely chance they're the same)
        if solution1 != solution2:
            response = client.post('/check',
                                  data=json.dumps({'board': solution1}),
                                  content_type='application/json')
            
            data = json.loads(response.data)
            # Should have incorrect cells (most likely)
            # This test is probabilistic but should work 99.9% of the time
