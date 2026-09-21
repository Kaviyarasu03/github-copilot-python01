import copy
import random

SIZE = 9
EMPTY = 0

# Difficulty level configuration
DIFFICULTY_LEVELS = {
    'easy': 40,      # More clues = easier puzzle
    'medium': 35,    # Balanced difficulty
    'hard': 30,      # Fewer clues = harder puzzle
}

def get_clue_count(difficulty='medium'):
    """Get the clue count for a specified difficulty level.
    
    Args:
        difficulty: Difficulty level ('easy', 'medium', 'hard')
        
    Returns:
        Number of clues for the difficulty level. Defaults to 35 (medium)
        if difficulty is not recognized.
    """
    return DIFFICULTY_LEVELS.get(difficulty, 35)


def is_move_valid(board, row, col, num):
    """Check if placing a number at a position is valid according to Sudoku rules.
    
    Validates that the number doesn't conflict with:
    - Other numbers in the same row
    - Other numbers in the same column
    - Other numbers in the same 3x3 box
    
    Args:
        board: Current board state (may have empty cells)
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)
    
    Returns:
        True if the move is valid, False otherwise
    """
    if num < 1 or num > 9:
        return False
    
    # Check row for the number (excluding the target cell)
    for x in range(SIZE):
        if x != col and board[row][x] == num:
            return False
    
    # Check column for the number (excluding the target cell)
    for x in range(SIZE):
        if x != row and board[x][col] == num:
            return False
    
    # Check 3x3 box for the number
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            cell_row = start_row + i
            cell_col = start_col + j
            if (cell_row != row or cell_col != col) and board[cell_row][cell_col] == num:
                return False
    
    return True

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

def count_solutions(board, max_count=2):
    """Count the number of valid solutions for a given puzzle.
    
    Uses backtracking to find all valid solutions. Stops early after finding
    max_count solutions for efficiency.
    
    Args:
        board: Sudoku board (may be partially filled)
        max_count: Return early once this many solutions is found (default 2)
    
    Returns:
        Number of valid solutions (will be at most max_count + 1)
    """
    solutions = [0]  # Use list for mutable counter in nested function
    
    def solve(board):
        # Early termination if we've already found enough solutions
        if solutions[0] > max_count:
            return
        
        # Find next empty cell
        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] == EMPTY:
                    # Try each number 1-9
                    for num in range(1, SIZE + 1):
                        if is_safe(board, row, col, num):
                            board[row][col] = num
                            solve(board)
                            board[row][col] = EMPTY
                    return
        
        # No empty cells found - we have a complete solution
        solutions[0] += 1
    
    # Work on a copy to avoid modifying the input
    board_copy = deep_copy(board)
    solve(board_copy)
    return solutions[0]


def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution


def generate_puzzle_unique(clues=35):
    """Generate a Sudoku puzzle that has exactly one unique solution.
    
    Uses incremental cell removal with solution counting to ensure the
    generated puzzle has exactly one valid solution.
    
    Args:
        clues: Target number of clues (default 35)
    
    Returns:
        Tuple of (puzzle, solution) where puzzle has exactly one solution
    """
    # Generate a complete valid solution
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    
    # Start with complete board and remove cells one by one
    puzzle = deep_copy(board)
    current_clues = SIZE * SIZE
    
    # Create list of all positions and shuffle them
    positions = [(i, j) for i in range(SIZE) for j in range(SIZE)]
    random.shuffle(positions)
    
    # Try removing cells one by one while maintaining unique solution
    for row, col in positions:
        # Stop if we've reached target clues
        if current_clues <= clues:
            break
        
        # Only try to remove if cell is not empty
        if puzzle[row][col] != EMPTY:
            # Save the value in case we need to restore it
            saved_value = puzzle[row][col]
            puzzle[row][col] = EMPTY
            
            # Check if puzzle still has exactly one solution
            if count_solutions(puzzle, max_count=2) == 1:
                # Keep the removal
                current_clues -= 1
            else:
                # Restore the cell - removing it creates multiple solutions
                puzzle[row][col] = saved_value
    
    return puzzle, solution
