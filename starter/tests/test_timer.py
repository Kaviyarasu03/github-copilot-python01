"""Tests for the frontend Sudoku timer wiring."""
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
MAIN_JS = (PROJECT_ROOT / 'static' / 'main.js').read_text()
INDEX_HTML = (PROJECT_ROOT / 'templates' / 'index.html').read_text()


class TestTimer:
    def test_timer_display_is_present_and_starts_at_zero(self):
        assert 'id="timer"' in INDEX_HTML
        assert '00:00' in INDEX_HTML

    def test_timer_formats_elapsed_time_as_minutes_and_seconds(self):
        assert 'function formatTime(seconds)' in MAIN_JS
        assert "padStart(2, '0')" in MAIN_JS
        assert "return `${minutes}:${remainingSeconds}`" in MAIN_JS

    def test_new_game_starts_and_resets_timer(self):
        new_game_start = MAIN_JS.index('async function newGame()')
        new_game_end = MAIN_JS.index('async function checkSolution()')
        new_game_body = MAIN_JS[new_game_start:new_game_end]

        assert 'startTimer();' in new_game_body
        assert 'function startTimer()' in MAIN_JS
        assert 'resetTimer();' in MAIN_JS

    def test_completion_stops_timer(self):
        completion_start = MAIN_JS.index('function showCompletionMessage()')
        completion_end = MAIN_JS.index('function clearMessageIfValid()')
        completion_body = MAIN_JS[completion_start:completion_end]

        assert 'stopTimer();' in completion_body

    def test_difficulty_selection_resets_timer(self):
        difficulty_start = MAIN_JS.index('difficultyBtns.forEach')
        difficulty_body = MAIN_JS[difficulty_start:]

        assert 'resetTimer();' in difficulty_body