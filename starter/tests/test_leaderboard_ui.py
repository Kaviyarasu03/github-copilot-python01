"""Focused checks for real-name leaderboard behavior."""
from pathlib import Path


ROOT = Path(__file__).parent.parent
HTML = (ROOT / 'templates' / 'index.html').read_text()
JS = (ROOT / 'static' / 'main.js').read_text()


def test_difficulty_uses_native_select():
    assert 'id="difficulty-select"' in HTML
    assert '<option value="easy">Easy</option>' in HTML
    assert '<option value="medium" selected>Medium</option>' in HTML
    assert '<option value="hard">Hard</option>' in HTML


def test_leaderboard_uses_real_names_and_local_storage():
    assert "const LEADERBOARD_KEY = 'sudokuLeaderboard';" in JS
    assert 'localStorage.getItem(LEADERBOARD_KEY)' in JS
    assert 'localStorage.setItem(LEADERBOARD_KEY' in JS
    assert "window.prompt('Enter your name:')" in JS
    assert "const trimmedName = name ? name.trim() : '';" in JS
    assert "if (!trimmedName) return;" in JS


def test_leaderboard_records_actual_game_metadata():
    assert 'name: trimmedName' in JS
    assert 'seconds: elapsedSeconds' in JS
    assert 'level: currentDifficulty' in JS
    assert 'hints: hintsUsed' in JS
    assert 'hintsUsed = 0;' in JS
    assert "document.getElementById('theme-toggle').addEventListener('click', toggleTheme)" in JS