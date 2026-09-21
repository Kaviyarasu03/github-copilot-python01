"""Pytest configuration and fixtures for the Sudoku Flask application."""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app and sudoku_logic
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import app
import sudoku_logic


@pytest.fixture
def client():
    """Create a Flask test client.
    
    This fixture:
    - Creates a Flask app in testing mode
    - Provides a test client for making requests
    - Isolates each test with a fresh app context
    """
    app.app.config['TESTING'] = True
    
    with app.app.test_client() as client:
        yield client
        # Reset the CURRENT store after each test
        app.CURRENT['puzzle'] = None
        app.CURRENT['solution'] = None


@pytest.fixture
def fresh_board():
    """Create a fresh empty Sudoku board for testing.
    
    This fixture provides a clean board without any numbers,
    useful for testing board creation and manipulation functions.
    """
    return sudoku_logic.create_empty_board()


@pytest.fixture
def sample_puzzle_and_solution():
    """Generate a sample puzzle and solution for testing.
    
    This fixture:
    - Creates a complete valid solution
    - Generates a puzzle with unique solution (35 clues)
    - Can be used in multiple tests
    """
    puzzle, solution = sudoku_logic.generate_puzzle_unique(clues=35)
    return puzzle, solution
