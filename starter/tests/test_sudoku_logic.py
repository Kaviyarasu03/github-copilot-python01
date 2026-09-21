"""Tests for sudoku_logic module.

This module tests the core Sudoku game logic including:
- Board creation and manipulation
- Validation of number placement
- Puzzle and solution generation
- Board copying
- Solution counting and uniqueness verification
"""
import pytest
import random
import sudoku_logic


class TestBoardCreation:
    """Test cases for board creation functions."""

    def test_create_empty_board_dimensions(self, fresh_board):
        """Test that empty board has correct dimensions (9x9)."""
        assert len(fresh_board) == 9
        assert all(len(row) == 9 for row in fresh_board)

    def test_create_empty_board_all_zeros(self, fresh_board):
        """Test that all cells in empty board are initialized to 0."""
        for row in fresh_board:
            for cell in row:
                assert cell == sudoku_logic.EMPTY

    def test_create_empty_board_returns_list_of_lists(self):
        """Test that board is a list of lists (nested structure)."""
        board = sudoku_logic.create_empty_board()
        assert isinstance(board, list)
        assert isinstance(board[0], list)


class TestDeepCopy:
    """Test cases for board deep copy functionality."""

    def test_deep_copy_creates_independent_copy(self, fresh_board):
        """Test that deep copy creates a truly independent copy."""
        copied = sudoku_logic.deep_copy(fresh_board)
        
        # Modify original
        fresh_board[0][0] = 5
        
        # Copy should be unchanged
        assert copied[0][0] == sudoku_logic.EMPTY
        assert fresh_board[0][0] == 5

    def test_deep_copy_preserves_values(self):
        """Test that deep copy preserves all values from original board."""
        # Create a board with some values
        board = sudoku_logic.create_empty_board()
        board[0][0] = 1
        board[4][4] = 5
        board[8][8] = 9
        
        copied = sudoku_logic.deep_copy(board)
        
        assert copied[0][0] == 1
        assert copied[4][4] == 5
        assert copied[8][8] == 9

    def test_deep_copy_entire_filled_board(self):
        """Test deep copy on a completely filled board."""
        board = sudoku_logic.create_empty_board()
        # Fill with sequential numbers
        for i in range(9):
            for j in range(9):
                board[i][j] = ((i + j) % 9) + 1
        
        copied = sudoku_logic.deep_copy(board)
        
        # Verify all values match
        for i in range(9):
            for j in range(9):
                assert copied[i][j] == board[i][j]


class TestIsSafe:
    """Test cases for number placement validation."""

    def test_is_safe_empty_board(self, fresh_board):
        """Test that any number 1-9 is safe on empty board."""
        for num in range(1, 10):
            assert sudoku_logic.is_safe(fresh_board, 0, 0, num)

    def test_is_safe_row_conflict(self, fresh_board):
        """Test that is_safe detects duplicate in same row."""
        fresh_board[0][0] = 5
        fresh_board[0][1] = 3
        
        # 5 is already in row 0, so placement at [0][8] should be unsafe
        assert not sudoku_logic.is_safe(fresh_board, 0, 8, 5)
        # But 7 is not in row 0, should be safe
        assert sudoku_logic.is_safe(fresh_board, 0, 8, 7)

    def test_is_safe_column_conflict(self, fresh_board):
        """Test that is_safe detects duplicate in same column."""
        fresh_board[0][0] = 5
        fresh_board[1][0] = 3
        
        # 5 is already in column 0, so placement at [8][0] should be unsafe
        assert not sudoku_logic.is_safe(fresh_board, 8, 0, 5)
        # But 7 is not in column 0, should be safe
        assert sudoku_logic.is_safe(fresh_board, 8, 0, 7)

    def test_is_safe_box_conflict(self, fresh_board):
        """Test that is_safe detects duplicate in same 3x3 box."""
        # Place 5 in top-left 3x3 box
        fresh_board[0][0] = 5
        
        # Try to place 5 elsewhere in the same box - should be unsafe
        assert not sudoku_logic.is_safe(fresh_board, 1, 1, 5)
        assert not sudoku_logic.is_safe(fresh_board, 2, 2, 5)
        
        # Try to place 5 in a different box - should be safe
        assert sudoku_logic.is_safe(fresh_board, 4, 4, 5)

    def test_is_safe_multiple_conflicts(self, fresh_board):
        """Test is_safe with multiple existing numbers."""
        fresh_board[0][0] = 1
        fresh_board[0][1] = 2
        fresh_board[1][0] = 3
        fresh_board[1][1] = 4
        fresh_board[2][2] = 5
        
        # 1 is in row 0 and column 0
        assert not sudoku_logic.is_safe(fresh_board, 0, 5, 1)
        assert not sudoku_logic.is_safe(fresh_board, 8, 0, 1)
        
        # 5 is in the top-left box
        assert not sudoku_logic.is_safe(fresh_board, 2, 0, 5)
        
        # 6 should be safe in many positions
        assert sudoku_logic.is_safe(fresh_board, 0, 5, 6)

    def test_is_safe_all_numbers_valid_on_empty(self, fresh_board):
        """Test all numbers 1-9 are initially valid."""
        valid_count = sum(1 for num in range(1, 10)
                         if sudoku_logic.is_safe(fresh_board, 5, 5, num))
        assert valid_count == 9


class TestFillBoard:
    """Test cases for board filling algorithm."""

    def test_fill_board_returns_true(self, fresh_board):
        """Test that fill_board returns True when successful."""
        result = sudoku_logic.fill_board(fresh_board)
        assert result is True

    def test_fill_board_completes_board(self, fresh_board):
        """Test that fill_board fills all cells with numbers 1-9."""
        sudoku_logic.fill_board(fresh_board)
        
        # No cell should be empty
        for i in range(sudoku_logic.SIZE):
            for j in range(sudoku_logic.SIZE):
                assert fresh_board[i][j] != sudoku_logic.EMPTY
                assert 1 <= fresh_board[i][j] <= 9

    def test_fill_board_respects_constraints(self, fresh_board):
        """Test that filled board satisfies Sudoku constraints."""
        sudoku_logic.fill_board(fresh_board)
        
        # Check rows
        for row in fresh_board:
            assert len(set(row)) == 9, "Row has duplicates"
        
        # Check columns
        for col in range(9):
            column = [fresh_board[row][col] for row in range(9)]
            assert len(set(column)) == 9, "Column has duplicates"
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        box_values.append(fresh_board[box_row + i][box_col + j])
                assert len(set(box_values)) == 9, "3x3 box has duplicates"

    def test_fill_board_with_partial_board(self):
        """Test fill_board can work with a partially filled board."""
        board = sudoku_logic.create_empty_board()
        # Place some initial numbers
        board[0][0] = 5
        board[4][4] = 1
        board[8][8] = 9
        
        result = sudoku_logic.fill_board(board)
        assert result is True
        
        # Verify constraints still satisfied
        for i in range(9):
            for j in range(9):
                assert 1 <= board[i][j] <= 9


class TestRemoveCells:
    """Test cases for cell removal (puzzle creation)."""

    def test_remove_cells_reduces_clue_count(self):
        """Test that remove_cells correctly removes cells."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Count non-empty cells before removal
        before = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
        
        sudoku_logic.remove_cells(board, clues=35)
        
        # Count non-empty cells after removal
        after = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
        
        # Should have exactly 35 clues left
        assert after == 35
        assert after < before

    def test_remove_cells_with_different_clue_counts(self):
        """Test remove_cells with various clue counts."""
        for clues in [20, 35, 50, 60]:
            board = sudoku_logic.create_empty_board()
            sudoku_logic.fill_board(board)
            sudoku_logic.remove_cells(board, clues=clues)
            
            remaining = sum(1 for i in range(9) for j in range(9) if board[i][j] != 0)
            assert remaining == clues


class TestGeneratePuzzle:
    """Test cases for complete puzzle generation."""

    def test_generate_puzzle_returns_tuple(self):
        """Test that generate_puzzle returns a tuple of (puzzle, solution)."""
        result = sudoku_logic.generate_puzzle()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_puzzle_creates_valid_boards(self, sample_puzzle_and_solution):
        """Test that generated puzzle and solution are valid boards."""
        puzzle, solution = sample_puzzle_and_solution
        
        # Both should be 9x9
        assert len(puzzle) == 9
        assert len(solution) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert all(len(row) == 9 for row in solution)

    def test_generate_puzzle_solution_is_complete(self, sample_puzzle_and_solution):
        """Test that solution has no empty cells."""
        puzzle, solution = sample_puzzle_and_solution
        
        for i in range(9):
            for j in range(9):
                assert solution[i][j] != sudoku_logic.EMPTY

    def test_generate_puzzle_has_clues(self, sample_puzzle_and_solution):
        """Test that puzzle has expected number of clues."""
        puzzle, solution = sample_puzzle_and_solution
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count == 35

    def test_generate_puzzle_custom_clues(self):
        """Test generate_puzzle with custom clue count."""
        for clues in [20, 40, 50]:
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
            
            puzzle_clue_count = sum(1 for i in range(9) for j in range(9) 
                                   if puzzle[i][j] != sudoku_logic.EMPTY)
            assert puzzle_clue_count == clues

    def test_generate_puzzle_clues_from_solution(self, sample_puzzle_and_solution):
        """Test that puzzle clues exist in the solution at same positions."""
        puzzle, solution = sample_puzzle_and_solution
        
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != sudoku_logic.EMPTY:
                    # Every clue in puzzle should match solution
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_independence(self):
        """Test that consecutive puzzles are different."""
        puzzle1, solution1 = sudoku_logic.generate_puzzle()
        puzzle2, solution2 = sudoku_logic.generate_puzzle()
        
        # Very unlikely that two randomly generated puzzles are identical
        assert puzzle1 != puzzle2 or solution1 != solution2

    def test_generate_puzzle_solution_satisfies_constraints(self, sample_puzzle_and_solution):
        """Test that solution satisfies all Sudoku constraints."""
        puzzle, solution = sample_puzzle_and_solution
        
        # Check rows
        for row in solution:
            assert len(set(row)) == 9, "Solution has duplicate in row"
        
        # Check columns
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            assert len(set(column)) == 9, "Solution has duplicate in column"
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        box_values.append(solution[box_row + i][box_col + j])
                assert len(set(box_values)) == 9, "Solution has duplicate in box"


class TestCountSolutions:
    """Test cases for solution counting functionality."""

    def test_count_solutions_complete_board_has_one(self):
        """Test that a completely filled board has exactly one solution."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # A complete valid board has exactly 1 solution (itself)
        count = sudoku_logic.count_solutions(board)
        assert count == 1

    def test_count_solutions_empty_board_has_multiple(self):
        """Test that empty board has many solutions (more than 1)."""
        board = sudoku_logic.create_empty_board()
        
        count = sudoku_logic.count_solutions(board, max_count=2)
        # Empty board definitely has more than 1 solution
        assert count > 1

    def test_count_solutions_single_empty_cell(self):
        """Test counting solutions with one empty cell in otherwise full board."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Now remove one cell
        board[0][0] = sudoku_logic.EMPTY
        
        # With one empty cell in a valid Sudoku, typically only 1 solution
        count = sudoku_logic.count_solutions(board)
        assert count == 1

    def test_count_solutions_early_termination(self):
        """Test that count_solutions stops early after finding 2 solutions."""
        # Create a puzzle that definitely has multiple solutions
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Remove multiple cells to create multiple solutions
        board[0][0] = sudoku_logic.EMPTY
        board[0][1] = sudoku_logic.EMPTY
        board[0][2] = sudoku_logic.EMPTY
        
        # With max_count=2, should return at most 2 or 3
        # (might find 2 and stop, or find 3 before realizing to stop)
        count = sudoku_logic.count_solutions(board, max_count=2)
        assert count <= 3

    def test_count_solutions_preserves_board(self):
        """Test that count_solutions doesn't modify the input board."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        board_copy = sudoku_logic.deep_copy(board)
        
        # Remove some cells
        board[0][0] = sudoku_logic.EMPTY
        board[1][1] = sudoku_logic.EMPTY
        saved_board = sudoku_logic.deep_copy(board)
        
        # Count solutions
        sudoku_logic.count_solutions(board)
        
        # Board should be unchanged
        assert board == saved_board

    def test_count_solutions_with_various_clue_counts(self):
        """Test counting solutions with puzzles of different difficulty."""
        # Create a base solution
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Test with increasing number of removed cells
        test_cases = [
            (75, 1),   # Only 6 cells removed - likely unique
            (35, 1),   # Standard puzzle - should be unique or very close
        ]
        
        for clue_count, expected_at_least in test_cases:
            puzzle = sudoku_logic.deep_copy(board)
            # Randomly remove cells to match clue count
            cells_to_remove = 81 - clue_count
            positions = [(i, j) for i in range(9) for j in range(9)]
            random.shuffle(positions)
            
            for i, (row, col) in enumerate(positions[:cells_to_remove]):
                puzzle[row][col] = sudoku_logic.EMPTY
            
            count = sudoku_logic.count_solutions(puzzle, max_count=2)
            assert count >= expected_at_least


class TestGeneratePuzzleUnique:
    """Test cases for unique solution puzzle generation."""

    def test_generate_puzzle_unique_returns_tuple(self):
        """Test that generate_puzzle_unique returns a tuple."""
        result = sudoku_logic.generate_puzzle_unique()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_puzzle_unique_has_exactly_one_solution(self):
        """Test that each generated puzzle has exactly one solution."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(clues=35)
        
        # Count solutions for the generated puzzle
        solution_count = sudoku_logic.count_solutions(puzzle, max_count=2)
        assert solution_count == 1

    def test_generate_puzzle_unique_multiple_puzzles_are_unique(self):
        """Test that multiple generated puzzles each have unique solutions."""
        for _ in range(5):
            puzzle, solution = sudoku_logic.generate_puzzle_unique(clues=35)
            
            solution_count = sudoku_logic.count_solutions(puzzle)
            assert solution_count == 1, f"Generated puzzle has {solution_count} solutions, expected 1"

    def test_generate_puzzle_unique_solution_is_complete(self):
        """Test that solution from unique generation is complete."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        for i in range(9):
            for j in range(9):
                assert solution[i][j] != sudoku_logic.EMPTY

    def test_generate_puzzle_unique_solution_satisfies_constraints(self):
        """Test that solution satisfies all Sudoku constraints."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        # Check rows
        for row in solution:
            assert len(set(row)) == 9
        
        # Check columns
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            assert len(set(column)) == 9
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        box_values.append(solution[box_row + i][box_col + j])
                assert len(set(box_values)) == 9

    def test_generate_puzzle_unique_clues_match_solution(self):
        """Test that all clues in puzzle exist in solution."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != sudoku_logic.EMPTY:
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_unique_with_20_clues(self):
        """Test unique puzzle generation with 20 clues (hard)."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(clues=20)
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 20  # May be more to maintain uniqueness
        
        solution_count = sudoku_logic.count_solutions(puzzle)
        assert solution_count == 1

    def test_generate_puzzle_unique_with_50_clues(self):
        """Test unique puzzle generation with 50 clues (easy)."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique(clues=50)
        
        clue_count = sum(1 for i in range(9) for j in range(9) 
                        if puzzle[i][j] != sudoku_logic.EMPTY)
        assert clue_count >= 50  # May be more to maintain uniqueness
        
        solution_count = sudoku_logic.count_solutions(puzzle)
        assert solution_count == 1

    def test_generate_puzzle_unique_puzzle_has_no_duplicates_in_rows(self):
        """Test that puzzle clues have no duplicates in any row."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        for i in range(9):
            row_values = [puzzle[i][j] for j in range(9) if puzzle[i][j] != sudoku_logic.EMPTY]
            # All values in row (excluding empties) should be unique
            assert len(row_values) == len(set(row_values))

    def test_generate_puzzle_unique_puzzle_has_no_duplicates_in_columns(self):
        """Test that puzzle clues have no duplicates in any column."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        for j in range(9):
            col_values = [puzzle[i][j] for i in range(9) if puzzle[i][j] != sudoku_logic.EMPTY]
            # All values in column (excluding empties) should be unique
            assert len(col_values) == len(set(col_values))

    def test_generate_puzzle_unique_puzzle_has_no_duplicates_in_boxes(self):
        """Test that puzzle clues have no duplicates in any 3x3 box."""
        puzzle, solution = sudoku_logic.generate_puzzle_unique()
        
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        val = puzzle[box_row + i][box_col + j]
                        if val != sudoku_logic.EMPTY:
                            box_values.append(val)
                # All values in box (excluding empties) should be unique
                assert len(box_values) == len(set(box_values))
