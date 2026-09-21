"""Focused checks for the final UI shell."""
from pathlib import Path


ROOT = Path(__file__).parent.parent
HTML = (ROOT / 'templates' / 'index.html').read_text()
CSS = (ROOT / 'static' / 'styles.css').read_text()
JS = (ROOT / 'static' / 'main.js').read_text()


def test_final_layout_contains_theme_and_scoreboard_controls():
    assert 'id="theme-toggle"' in HTML
    assert 'id="scoreboard-body"' in HTML
    assert all(column in HTML for column in ['Rank', 'Name', 'Time', 'Level', 'Hints'])


def test_final_ui_preserves_existing_game_hooks():
    assert all(identifier in HTML for identifier in [
        'id="new-game"', 'id="check-solution"', 'id="hint"', 'id="timer"',
        'class="difficulty-btn"'
    ])


def test_theme_and_scoreboard_behavior_are_frontend_only():
    assert 'function toggleTheme()' in JS
    assert 'sessionStorage.setItem(\'sudokuTheme\'' in JS
    assert 'function renderScoreboard()' in JS
    assert 'function recordScore()' in JS
    assert 'grid-template-columns: minmax(150px, 1fr) auto minmax(150px, 1fr)' in CSS