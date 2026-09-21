"""Tests for difficulty selector functionality.

This module tests the difficulty level feature including:
- Backend difficulty parameter handling
- Clue count mapping for each difficulty
- Uniqueness guarantee across all difficulties
- Backward compatibility with clues parameter
- Flask route behavior with various parameters
"""
import pytest
import json
import sudoku_logic


class TestDifficultyLevels:
    """Test cases for difficulty level constants and mappings."""

    def test_difficulty_levels_constant_exists(self):
        """Test that DIFFICULTY_LEVELS constant is defined."""
        assert hasattr(sudoku_logic, 'DIFFICULTY_LEVELS')
        assert isinstance(sudoku_logic.DIFFICULTY_LEVELS, dict)

    def test_difficulty_levels_has_required_keys(self):
        """Test that DIFFICULTY_LEVELS has easy, medium, and hard."""
        assert 'easy' in sudoku_logic.DIFFICULTY_LEVELS
        assert 'medium' in sudoku_logic.DIFFICULTY_LEVELS
        assert 'hard' in sudoku_logic.DIFFICULTY_LEVELS

    def test_difficulty_levels_correct_values(self):
        """Test that clue counts match specification."""
        assert sudoku_logic.DIFFICULTY_LEVELS['easy'] == 40
        assert sudoku_logic.DIFFICULTY_LEVELS['medium'] == 35
        assert sudoku_logic.DIFFICULTY_LEVELS['hard'] == 30

    def test_get_clue_count_function_exists(self):
        """Test that get_clue_count function is defined."""
        assert hasattr(sudoku_logic, 'get_clue_count')
        assert callable(sudoku_logic.get_clue_count)

    def test_get_clue_count_easy(self):
        """Test get_clue_count returns 40 for easy."""
        assert sudoku_logic.get_clue_count('easy') == 40

    def test_get_clue_count_medium(self):
        """Test get_clue_count returns 35 for medium."""
        assert sudoku_logic.get_clue_count('medium') == 35

    def test_get_clue_count_hard(self):
        """Test get_clue_count returns 30 for hard."""
        assert sudoku_logic.get_clue_count('hard') == 30

    def test_get_clue_count_default(self):
        """Test get_clue_count returns 35 when no parameter provided."""
        assert sudoku_logic.get_clue_count() == 35

    def test_get_clue_count_default_medium(self):
        """Test get_clue_count returns 35 for invalid difficulty."""
        assert sudoku_logic.get_clue_count('invalid') == 35

    def test_get_clue_count_default_parameter_is_medium(self):
        """Test get_clue_count default parameter is 'medium'."""
        import inspect
        sig = inspect.signature(sudoku_logic.get_clue_count)
        assert sig.parameters['difficulty'].default == 'medium'


class TestNewGameWithDifficulty:
    """Test cases for /new route with difficulty parameter."""

    def test_new_game_with_easy_difficulty(self, client):
        """Test /new?difficulty=easy returns puzzle with >= 40 clues."""
        response = client.get('/new?difficulty=easy')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 40

    def test_new_game_with_medium_difficulty(self, client):
        """Test /new?difficulty=medium returns puzzle with >= 35 clues."""
        response = client.get('/new?difficulty=medium')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 35

    def test_new_game_with_hard_difficulty(self, client):
        """Test /new?difficulty=hard returns puzzle with >= 30 clues."""
        response = client.get('/new?difficulty=hard')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 30

    def test_new_game_no_difficulty_defaults_to_medium(self, client):
        """Test /new without difficulty defaults to medium (35 clues)."""
        response = client.get('/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 35

    def test_new_game_invalid_difficulty_defaults_to_medium(self, client):
        """Test /new with invalid difficulty defaults to medium."""
        response = client.get('/new?difficulty=impossible')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 35

    def test_new_game_backward_compatible_with_clues(self, client):
        """Test /new?clues=45 still works (backward compatibility)."""
        response = client.get('/new?clues=45')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 45

    def test_new_game_difficulty_takes_precedence(self, client):
        """Test that difficulty takes precedence over clues parameter."""
        # Request with both difficulty=hard and clues=50
        # Should use difficulty=hard (30 clues), not clues=50
        response = client.get('/new?difficulty=hard&clues=50')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        # Should be closer to 30 than 50 (difficulty takes precedence)
        assert clue_count >= 30
        # Very likely to be much less than 50 (difficulty wins)
        assert clue_count < 45


class TestDifficultyUniqueSolution:
    """Test cases for uniqueness guarantee across difficulty levels."""

    def test_easy_puzzle_has_unique_solution(self):
        """Test that easy difficulty puzzles have exactly one solution."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(
            clues=sudoku_logic.DIFFICULTY_LEVELS['easy']
        )
        
        solution_count = sudoku_logic.count_solutions(puzzle)
        assert solution_count == 1

    def test_medium_puzzle_has_unique_solution(self):
        """Test that medium difficulty puzzles have exactly one solution."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(
            clues=sudoku_logic.DIFFICULTY_LEVELS['medium']
        )
        
        solution_count = sudoku_logic.count_solutions(puzzle)
        assert solution_count == 1

    def test_hard_puzzle_has_unique_solution(self):
        """Test that hard difficulty puzzles have exactly one solution."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(
            clues=sudoku_logic.DIFFICULTY_LEVELS['hard']
        )
        
        solution_count = sudoku_logic.count_solutions(puzzle)
        assert solution_count == 1

    def test_multiple_easy_puzzles_all_unique(self):
        """Test that multiple easy puzzles each have unique solutions."""
        for _ in range(3):
            puzzle, solution = sudoku_logic.generate_puzzle_unique(
                clues=sudoku_logic.DIFFICULTY_LEVELS['easy']
            )
            
            solution_count = sudoku_logic.count_solutions(puzzle)
            assert solution_count == 1

    def test_multiple_hard_puzzles_all_unique(self):
        """Test that multiple hard puzzles each have unique solutions."""
        for _ in range(3):
            puzzle, solution = sudoku_logic.generate_puzzle_unique(
                clues=sudoku_logic.DIFFICULTY_LEVELS['hard']
            )
            
            solution_count = sudoku_logic.count_solutions(puzzle)
            assert solution_count == 1


class TestDifficultyIntegration:
    """Integration tests for difficulty selector with Flask routes."""

    def test_check_solution_works_with_easy_puzzle(self, client):
        """Test that check solution works after generating easy puzzle."""
        import app
        
        client.get('/new?difficulty=easy')
        solution = app.CURRENT['solution']
        
        response = client.post('/check',
                              data=json.dumps({'board': solution}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['incorrect'] == []

    def test_check_solution_works_with_hard_puzzle(self, client):
        """Test that check solution works after generating hard puzzle."""
        import app
        
        client.get('/new?difficulty=hard')
        solution = app.CURRENT['solution']
        
        response = client.post('/check',
                              data=json.dumps({'board': solution}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['incorrect'] == []

    def test_new_game_with_difficulty_stores_in_current(self, client):
        """Test that difficulty-based game stores puzzle in CURRENT."""
        import app
        
        assert app.CURRENT['puzzle'] is None
        assert app.CURRENT['solution'] is None
        
        client.get('/new?difficulty=easy')
        
        assert app.CURRENT['puzzle'] is not None
        assert app.CURRENT['solution'] is not None

    def test_difficulty_changes_between_games(self, client):
        """Test that switching difficulty generates new puzzles."""
        import app
        
        # Generate easy puzzle
        client.get('/new?difficulty=easy')
        easy_puzzle = [row[:] for row in app.CURRENT['puzzle']]
        easy_clues = sum(1 for i in range(9) for j in range(9) 
                        if easy_puzzle[i][j] != sudoku_logic.EMPTY)
        
        # Generate hard puzzle
        client.get('/new?difficulty=hard')
        hard_puzzle = [row[:] for row in app.CURRENT['puzzle']]
        hard_clues = sum(1 for i in range(9) for j in range(9) 
                        if hard_puzzle[i][j] != sudoku_logic.EMPTY)
        
        # Puzzles should be different
        assert easy_puzzle != hard_puzzle
        # Easy should have more clues than hard (on average)
        # Note: May not always be true due to uniqueness constraints,
        # but very likely
        assert easy_clues >= hard_clues or easy_clues > hard_clues
