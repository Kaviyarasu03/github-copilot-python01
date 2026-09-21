"""Tests for New Game and difficulty reset behavior."""
from pathlib import Path


MAIN_JS = (Path(__file__).parent.parent / 'static' / 'main.js').read_text()


class TestResetBehavior:
    def test_new_game_clears_transient_state_before_loading(self):
        new_game_start = MAIN_JS.index('async function newGame()')
        new_game_end = MAIN_JS.index('async function checkSolution()')
        new_game_body = MAIN_JS[new_game_start:new_game_end]

        assert 'selectedCell = null;' in new_game_body
        assert "document.getElementById('message').innerText = '';" in new_game_body
        assert 'startTimer();' in new_game_body

    def test_rendering_a_new_puzzle_rebuilds_player_board(self):
        render_start = MAIN_JS.index('function renderPuzzle(puz)')
        render_end = MAIN_JS.index('async function newGame()')
        render_body = MAIN_JS[render_start:render_end]

        assert 'createBoardElement();' in render_body
        assert 'playerBoard = [];' in render_body
        assert 'inp.disabled = true;' in render_body

    def test_difficulty_selection_starts_a_fresh_game(self):
        difficulty_start = MAIN_JS.index('difficultyBtns.forEach')
        difficulty_body = MAIN_JS[difficulty_start:]

        assert 'currentDifficulty = e.target.dataset.difficulty;' in difficulty_body
        assert 'resetTimer();' in difficulty_body
        assert 'newGame();' in difficulty_body

    def test_new_game_does_not_clear_selected_difficulty(self):
        new_game_start = MAIN_JS.index('async function newGame()')
        new_game_end = MAIN_JS.index('async function checkSolution()')
        new_game_body = MAIN_JS[new_game_start:new_game_end]

        assert 'currentDifficulty =' not in new_game_body
        assert 'currentDifficulty}' in new_game_body