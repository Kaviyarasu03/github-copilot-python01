// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let currentDifficulty = 'medium';  // Track selected difficulty level
let selectedCell = null;  // Track currently selected cell [row, col]
let playerBoard = [];  // Track player's current board state
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let scoreRecorded = false;

const LEADERBOARD_KEY = 'sudokuLeaderboard';

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  resetTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function loadScores() {
  try {
    const storedScores = JSON.parse(localStorage.getItem(LEADERBOARD_KEY));
    return Array.isArray(storedScores) ? storedScores : [];
  } catch (error) {
    return [];
  }
}

function escapeScoreText(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
}

function renderScoreboard() {
  const scores = loadScores()
    .sort((first, second) => first.seconds - second.seconds)
    .slice(0, 10);
  const body = document.getElementById('scoreboard-body');
  body.innerHTML = scores.map((score, index) => `
    <tr><td>${index + 1}</td><td>${escapeScoreText(score.name)}</td><td>${formatTime(score.seconds)}</td><td>${escapeScoreText(score.level)}</td><td>${score.hints}</td></tr>
  `).join('');
}

function recordScore() {
  if (scoreRecorded) return;
  scoreRecorded = true;
  const name = window.prompt('Enter your name:');
  const trimmedName = name ? name.trim() : '';
  if (!trimmedName) return;

  const scores = loadScores();
  scores.push({
    name: trimmedName,
    seconds: elapsedSeconds,
    level: currentDifficulty[0].toUpperCase() + currentDifficulty.slice(1),
    hints: hintsUsed
  });
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch (error) {
    // The score remains visible for this render when storage is unavailable.
  }
  scores.sort((first, second) => first.seconds - second.seconds);
  const body = document.getElementById('scoreboard-body');
  body.innerHTML = scores.slice(0, 10).map((score, index) => `
    <tr><td>${index + 1}</td><td>${escapeScoreText(score.name)}</td><td>${formatTime(score.seconds)}</td><td>${escapeScoreText(score.level)}</td><td>${score.hints}</td></tr>
  `).join('');
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  const toggle = document.getElementById('theme-toggle');
  const dark = theme === 'dark';
  toggle.innerText = dark ? '\u263E' : '\u2600';
  toggle.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
}

function toggleTheme() {
  const theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(theme);
  try {
    sessionStorage.setItem('sudokuTheme', theme);
  } catch (error) {
    // Theme remains active for the current page when storage is unavailable.
  }
}

function initializeTheme() {
  let theme = 'light';
  try {
    theme = sessionStorage.getItem('sudokuTheme') || theme;
  } catch (error) {
    // Use light mode when session storage is unavailable.
  }
  applyTheme(theme);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      
      // Handle cell selection
      input.addEventListener('click', (e) => {
        selectCell(i, j);
      });
      
      // Handle keyboard input
      input.addEventListener('keydown', (e) => {
        handleCellInput(e, i, j);
      });
      
      // Allow only numbers 1-9 in input event
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function selectCell(row, col) {
  // Select a cell and visually highlight it.
  // Remove selection from previous cell
  if (selectedCell) {
    const prevIdx = selectedCell[0] * SIZE + selectedCell[1];
    const boardDiv = document.getElementById('sudoku-board');
    const inputs = boardDiv.getElementsByTagName('input');
    inputs[prevIdx].classList.remove('selected');
  }
  
  // Set new selection
  selectedCell = [row, col];
  const idx = row * SIZE + col;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  inputs[idx].classList.add('selected');
  inputs[idx].focus();
}

function handleCellInput(e, row, col) {
  // Handle keyboard input for a cell.
  const input = e.target;
  
  // If cell is prefilled (original puzzle clue), don't allow editing
  if (input.disabled) {
    e.preventDefault();
    return;
  }
  
  // Handle Delete/Backspace - clear cell
  if (e.key === 'Delete' || e.key === 'Backspace') {
    e.preventDefault();
    input.value = '';
    input.classList.remove('invalid', 'valid');
    playerBoard[row][col] = 0;
    clearMessageIfValid();
    return;
  }
  
  // Handle number keys (1-9)
  if (e.key >= '1' && e.key <= '9') {
    e.preventDefault();
    const num = parseInt(e.key);
    input.value = num;
    playerBoard[row][col] = num;
    
    // Validate the move
    validateAndHighlight(row, col, num, input);
    
    // Move to next cell if valid (optional - just validate for now)
    checkCompletion();
  }
  
  // Handle Arrow keys for navigation
  if (e.key === 'ArrowUp' && row > 0) {
    e.preventDefault();
    selectCell(row - 1, col);
  } else if (e.key === 'ArrowDown' && row < SIZE - 1) {
    e.preventDefault();
    selectCell(row + 1, col);
  } else if (e.key === 'ArrowLeft' && col > 0) {
    e.preventDefault();
    selectCell(row, col - 1);
  } else if (e.key === 'ArrowRight' && col < SIZE - 1) {
    e.preventDefault();
    selectCell(row, col + 1);
  }
}

async function validateAndHighlight(row, col, num, inputElement) {
  // Validate a move and provide visual feedback.
  try {
    const response = await fetch('/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        row: row,
        col: col,
        num: num,
        board: playerBoard
      })
    });
    
    const data = await response.json();
    
    if (data.valid) {
      inputElement.classList.remove('invalid');
      inputElement.classList.add('valid');
    } else {
      inputElement.classList.add('invalid');
      inputElement.classList.remove('valid');
    }
  } catch (error) {
    console.error('Validation error:', error);
  }
}

function checkCompletion() {
  // Check if the puzzle is completely and correctly solved.
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  // Check if all cells are filled
  for (let idx = 0; idx < inputs.length; idx++) {
    if (inputs[idx].value === '') {
      return;  // Not all cells filled
    }
  }
  
  // All cells are filled, check if correct
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (playerBoard[i][j] !== puzzle[i][j]) {
        return;  // Not correct
      }
    }
  }
  
  // Puzzle is complete and correct!
  showCompletionMessage();
}

function showCompletionMessage() {
  // Display completion message.
  stopTimer();
  const msg = document.getElementById('message');
  msg.style.color = '#388e3c';
  msg.innerText = 'Congratulations! You solved it!';
  recordScore();
}

function clearMessageIfValid() {
  // Clear message if no errors are shown.
  const msg = document.getElementById('message');
  if (msg.innerText === 'Some cells are incorrect.') {
    msg.innerText = '';
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  
  // Initialize playerBoard with puzzle values
  playerBoard = [];
  for (let i = 0; i < SIZE; i++) {
    playerBoard[i] = [];
    for (let j = 0; j < SIZE; j++) {
      playerBoard[i][j] = puzzle[i][j];
    }
  }
  
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  
  // Select first empty cell
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (puzzle[i][j] === 0) {
        selectCell(i, j);
        return;
      }
    }
  }
}

async function newGame() {
  selectedCell = null;
  hintsUsed = 0;
  scoreRecorded = false;
  document.getElementById('message').innerText = '';
  startTimer();
  const res = await fetch(`/new?difficulty=${currentDifficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    showCompletionMessage();
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function requestHint() {
  const msg = document.getElementById('message');

  if (!selectedCell) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Select an empty cell first.';
    return;
  }

  const [row, col] = selectedCell;
  const input = document.querySelector(
    `input[data-row="${row}"][data-col="${col}"]`
  );

  if (!input || input.disabled) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Select an empty cell first.';
    return;
  }

  try {
    const response = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({row, col})
    });
    const data = await response.json();

    if (!response.ok) {
      msg.style.color = '#d32f2f';
      msg.innerText = data.error || 'Unable to provide a hint.';
      return;
    }

    input.value = data.value;
    input.disabled = true;
    input.className = 'sudoku-cell hinted selected';
    playerBoard[row][col] = data.value;
    hintsUsed += 1;
    msg.style.color = '#388e3c';
    msg.innerText = 'Hint added.';
    checkCompletion();
  } catch (error) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Unable to provide a hint.';
  }
}

// Wire buttons and difficulty selector
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  
  // Handle difficulty selector changes
  const difficultyBtns = [document.getElementById('difficulty-select')];
  difficultyBtns.forEach(btn => {
    btn.addEventListener('change', (e) => {
      e.target.dataset.difficulty = e.target.value;
      currentDifficulty = e.target.dataset.difficulty;
      resetTimer();
      newGame();
    });
  });
  
  // initialize
  initializeTheme();
  renderScoreboard();
  newGame();
});