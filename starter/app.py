from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Support both 'difficulty' and 'clues' parameters
    # Priority: difficulty > clues > default (medium/35)
    
    difficulty = request.args.get('difficulty', None)
    clues_param = request.args.get('clues', None)
    
    # If difficulty is specified and valid, use it
    if difficulty and difficulty in sudoku_logic.DIFFICULTY_LEVELS:
        clues = sudoku_logic.get_clue_count(difficulty)
    # Otherwise, if clues parameter is provided, use it
    elif clues_param:
        clues = int(clues_param)
    # Default to medium difficulty
    else:
        clues = sudoku_logic.get_clue_count('medium')
    
    puzzle, solution = sudoku_logic.generate_puzzle_unique(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/validate', methods=['POST'])
def validate_move():
    """Validate a move according to Sudoku rules.
    
    Expects JSON body with:
    - row: row index (0-8)
    - col: column index (0-8)
    - num: number to place (1-9)
    - board: current board state (for checking conflicts)
    
    Returns:
    - valid: boolean indicating if move is valid
    - message: explanation of validation result
    """
    data = request.json
    row = data.get('row')
    col = data.get('col')
    num = data.get('num')
    board = data.get('board')
    
    if row is None or col is None or num is None or board is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        row = int(row)
        col = int(col)
        num = int(num)
        
        # Check bounds
        if not (0 <= row < sudoku_logic.SIZE and 0 <= col < sudoku_logic.SIZE):
            return jsonify({'valid': False, 'message': 'Invalid cell position'}), 400
        
        if not (1 <= num <= 9):
            return jsonify({'valid': False, 'message': 'Number must be between 1 and 9'}), 400
        
        # Check if move is valid
        valid = sudoku_logic.is_move_valid(board, row, col, num)
        
        if valid:
            return jsonify({'valid': True, 'message': 'Valid move'})
        else:
            return jsonify({'valid': False, 'message': 'This number conflicts with existing entries'})
    
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid request parameters'}), 400

@app.route('/hint', methods=['POST'])
def get_hint():
    """Return the solution value for an empty, editable cell."""
    data = request.json or {}
    row = data.get('row')
    col = data.get('col')
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')

    if row is None or col is None:
        return jsonify({'error': 'Select an empty cell first'}), 400
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        row = int(row)
        col = int(col)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid cell position'}), 400

    if not (0 <= row < sudoku_logic.SIZE and 0 <= col < sudoku_logic.SIZE):
        return jsonify({'error': 'Invalid cell position'}), 400
    if puzzle[row][col] != sudoku_logic.EMPTY:
        return jsonify({'error': 'Select an empty cell first'}), 400

    return jsonify({'row': row, 'col': col, 'value': solution[row][col]})

if __name__ == '__main__':
    app.run(debug=True)