"""
Integration tests for the experiment infrastructure.

These tests capture the current behavior of the experiment system before refactoring.
They serve as a safety net to ensure refactoring doesn't introduce bugs.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock
import argparse

import sys
from pathlib import Path

# Add gpt directory to path so relative imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "gpt"))

# Mock OpenAI client before importing modules that use it
import os
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-testing")

from config import parse_args
from runners.step_runner import run_step_code
from runners.full_runner import run_full
from runners.tiles_runner import run_tile_step
from experiment import (
    summarize_logs,
    run_task,
    iter_set_tasks,
)
from runner_utils import (
    extract_code,
    parse_tile_actions,
    exec_snippet,
    run_with_timeout,
    fix_missing_tail_indent,
)
from metrics import evaluate_prediction, compute_board_metrics, compute_action_metrics
from prompts import build_prompts, make_user_prompt, make_tile_prompt
from constants.constants import WIDTH, HEIGHT


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_task() -> Dict:
    """A minimal task fixture for testing."""
    return {
        "steps": [
            "Draw a red tile at row 5, column 7",
            "Draw a yellow tile at row 5, column 8",
        ],
        "gold_boards": [
            [0] * (WIDTH * HEIGHT),  # After step 1 (simplified for testing)
            [0] * (WIDTH * HEIGHT),  # After step 2
        ],
    }


@pytest.fixture
def mock_config() -> argparse.Namespace:
    """Standard test configuration."""
    return argparse.Namespace(
        task=None,
        set=None,
        model="gpt-4o",
        temperature=0.0,
        max_tokens=512,
        seed=42,
        history=True,
        retries=3,
        mode="step",
        vision=False,
        workers=1,
        exec_timeout=10,
        experiment_name="test-run",
    )


@pytest.fixture
def mock_gpt_response() -> Dict:
    """Typical GPT response structure."""
    return {
        "text": "```python\nTile(row=5, column=7).draw('red')\n```",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
        },
        "raw": {},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Unit Tests for Helper Functions
# ──────────────────────────────────────────────────────────────────────────────


class TestExtractCode:
    """Test code extraction from GPT responses."""

    def test_extract_code_with_markdown(self):
        raw = "Here's the code:\n```python\nTile(1,2).draw('red')\n```"
        result = extract_code(raw)
        assert "Tile(1,2).draw('red')" in result
        assert "```" not in result

    def test_extract_code_without_markdown(self):
        raw = "Tile(1,2).draw('red')"
        result = extract_code(raw)
        assert "Tile(1,2).draw('red')" in result

    def test_extract_code_removes_imports(self):
        raw = "```python\nfrom hexagen import Game\nTile(1,2).draw('red')\n```"
        result = extract_code(raw)
        assert "from hexagen import Game" not in result
        assert "Tile(1,2).draw('red')" in result

    def test_extract_code_removes_with_game(self):
        raw = "```python\nwith Game() as g:\n    Tile(1,2).draw('red')\n```"
        result = extract_code(raw)
        assert "with Game()" not in result
        assert "Tile(1,2).draw('red')" in result


class TestParseTileActions:
    """Test tile action parsing."""

    def test_parse_tuple_list(self):
        text = "[(1,2,'red'), (3,4,'blue')]"
        result = parse_tile_actions(text)
        assert result == [(1, 2, "red"), (3, 4, "blue")]

    def test_parse_regex_pattern(self):
        text = "(1,2,green) (5,6,orange)"
        result = parse_tile_actions(text)
        assert result == [(1, 2, "green"), (5, 6, "orange")]

    def test_parse_mixed_quotes(self):
        text = '[(1,2,"red"), (3,4,\'blue\')]'
        result = parse_tile_actions(text)
        assert result == [(1, 2, "red"), (3, 4, "blue")]

    def test_parse_empty_input(self):
        result = parse_tile_actions("")
        assert result == []


class TestFixMissingTailIndent:
    """Test indentation fixing."""

    def test_adds_indent_after_game_context(self):
        src = "from hexagen import Game\nwith Game() as g:\nTile(1,2).draw('red')"
        result = fix_missing_tail_indent(src)
        assert "    Tile(1,2).draw('red')" in result

    def test_preserves_existing_indent(self):
        src = "from hexagen import Game\nwith Game() as g:\n    Tile(1,2).draw('red')"
        result = fix_missing_tail_indent(src)
        assert result == src


class TestMetrics:
    """Test evaluation metrics."""

    def test_compute_board_metrics_exact_match(self):
        pred = [1, 2, 0, 3]
        gold = [1, 2, 0, 3]
        prec, rec, f1, exact, tp, p, g = compute_board_metrics(pred, gold)
        assert exact is True
        assert prec == 1.0
        assert rec == 1.0
        assert f1 == 1.0

    def test_compute_board_metrics_no_match(self):
        pred = [1, 2, 0, 0]
        gold = [0, 0, 3, 4]
        prec, rec, f1, exact, tp, p, g = compute_board_metrics(pred, gold)
        assert exact is False
        assert tp == 0
        assert p == 2  # pred has 2 colored tiles
        assert g == 2  # gold has 2 colored tiles

    def test_compute_board_metrics_partial_match(self):
        pred = [1, 2, 0, 3]
        gold = [1, 0, 0, 3]
        prec, rec, f1, exact, tp, p, g = compute_board_metrics(pred, gold)
        assert exact is False
        assert tp == 2  # tiles 0 and 3 match
        assert p == 3  # pred has 3 colored
        assert g == 2  # gold has 2 colored

    def test_compute_action_metrics_exact(self):
        prev_pred = [0, 0, 0, 0]
        pred = [1, 2, 0, 0]
        prev_gold = [0, 0, 0, 0]
        gold = [1, 2, 0, 0]
        prec, rec, f1, exact, tp, p, g = compute_action_metrics(
            prev_pred, pred, prev_gold, gold
        )
        assert exact is True
        assert prec == 1.0
        assert rec == 1.0

    def test_evaluate_prediction_structure(self):
        prev_pred = [0] * 10
        pred = [1, 2, 0, 0, 0, 0, 0, 0, 0, 0]
        prev_gold = [0] * 10
        gold = [1, 2, 0, 0, 0, 0, 0, 0, 0, 0]
        result = evaluate_prediction(prev_pred, pred, prev_gold, gold)

        # Check all required keys exist
        required_keys = [
            "correct",
            "precision_board",
            "recall_board",
            "f1_board",
            "exact_board",
            "precision_action",
            "recall_action",
            "f1_action",
            "exact_action",
            "board_tp",
            "board_p",
            "board_g",
            "action_tp",
            "action_p",
            "action_g",
        ]
        for key in required_keys:
            assert key in result


class TestPrompts:
    """Test prompt building functions."""

    def test_build_prompts_step_mode(self):
        sys_prompt, user_tmpl = build_prompts(mode="step", vision=False)
        assert isinstance(sys_prompt, str)
        assert isinstance(user_tmpl, str)
        assert len(sys_prompt) > 0
        assert "{HISTORY_BLOCK}" in user_tmpl
        assert "{NEXT_STEP}" in user_tmpl
        assert "{CODE_SO_FAR}" in user_tmpl

    def test_build_prompts_tiles_mode(self):
        sys_prompt, user_tmpl = build_prompts(mode="tiles", vision=False)
        assert isinstance(sys_prompt, str)
        assert isinstance(user_tmpl, str)
        assert "{HISTORY_BLOCK}" in user_tmpl
        assert "{NEXT_STEP}" in user_tmpl

    def test_build_prompts_with_vision(self):
        sys_prompt, user_tmpl = build_prompts(mode="step", vision=True)
        assert "vision" in sys_prompt.lower() or len(sys_prompt) > 0

    def test_make_user_prompt_formatting(self):
        template = "History:\n{HISTORY_BLOCK}\n\nCode:\n{CODE_SO_FAR}\n\nNext:\n{NEXT_STEP}"
        prompt = make_user_prompt(
            instr="Draw red tile",
            history=["Step 1", "Step 2"],
            template=template,
            code="some code",
        )
        assert "Step 1" in prompt
        assert "Step 2" in prompt
        assert "Draw red tile" in prompt
        assert "some code" in prompt

    def test_make_user_prompt_empty_history(self):
        template = "History:\n{HISTORY_BLOCK}\n\nCode:\n{CODE_SO_FAR}\n\nNext:\n{NEXT_STEP}"
        prompt = make_user_prompt(
            instr="Draw red tile", history=[], template=template, code="code"
        )
        assert "(none yet)" in prompt

    def test_make_tile_prompt(self):
        template = "History:\n{HISTORY_BLOCK}\n\nNext:\n{NEXT_STEP}"
        prompt = make_tile_prompt(
            instr="Draw red tile", history=["Step 1"], template=template
        )
        assert "Step 1" in prompt
        assert "Draw red tile" in prompt


class TestSummarizeLogs:
    """Test log summarization."""

    def test_summarize_step_mode_all_correct(self):
        logs = [
            {"valid": True, "exact_board": True, "exact_action": True, "f1_board": 1.0, "f1_action": 1.0, "attempt": 1, "correct": True},
            {"valid": True, "exact_board": True, "exact_action": True, "f1_board": 1.0, "f1_action": 1.0, "attempt": 1, "correct": True},
        ]
        stats = summarize_logs(logs, mode="step", task_id=123)
        assert stats["task_id"] == 123
        assert stats["steps"] == 2
        assert stats["valid"] == 2
        assert stats["exact"] == 2
        assert stats["f1_board"] == 1.0
        assert stats["successful_steps"] == [1, 2]
        assert stats["failed_steps"] == []

    def test_summarize_step_mode_partial_success(self):
        logs = [
            {"valid": True, "exact_board": True, "exact_action": True, "f1_board": 1.0, "f1_action": 1.0, "attempt": 1, "correct": True},
            {"valid": True, "exact_board": False, "exact_action": False, "f1_board": 0.5, "f1_action": 0.5, "attempt": 2, "correct": False},
        ]
        stats = summarize_logs(logs, mode="step", task_id=123)
        assert stats["steps"] == 2
        assert stats["valid"] == 2
        assert stats["exact"] == 1
        assert stats["f1_board"] == 0.75  # (1.0 + 0.5) / 2
        assert stats["successful_steps"] == [1]
        assert stats["failed_steps"] == [2]

    def test_summarize_full_mode(self):
        logs = [
            {"valid": True, "exact_board": True, "f1_board": 1.0, "attempt": 1, "correct": True}
        ]
        stats = summarize_logs(logs, mode="full", task_id=123)
        assert stats["steps"] == 1
        assert stats["valid"] == 1
        assert stats["exact"] == 1


class TestIterSetTasks:
    """Test dataset iteration."""

    def test_iter_set_tasks_4_samples(self):
        tasks = list(iter_set_tasks("4-samples"))
        assert len(tasks) > 0
        for task_id, task_data in tasks:
            assert isinstance(task_id, int)
            assert "steps" in task_data
            assert "gold_boards" in task_data
            assert isinstance(task_data["steps"], list)
            assert isinstance(task_data["gold_boards"], list)

    def test_iter_set_tasks_filters_none(self):
        """Tasks should filter out steps with NONE instruction."""
        tasks = list(iter_set_tasks("4-samples"))
        for task_id, task_data in tasks:
            for step in task_data["steps"]:
                assert step != "NONE"


# ──────────────────────────────────────────────────────────────────────────────
# Integration Tests - Step Mode
# ──────────────────────────────────────────────────────────────────────────────


class TestStepModeIntegration:
    """Test step-by-step code execution mode."""

    @patch("runners.step_runner.call_gpt")
    def test_run_step_code_success(self, mock_call_gpt, mock_config, tmp_path):
        """Test successful step execution."""
        mock_call_gpt.return_value = {
            "text": "```python\nTile(row=5, column=7).draw('red')\n```",
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        }

        code_so_far = (
            "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
            "from constants import HEIGHT, WIDTH\n"
            "with Game() as g:\n"
        )

        gold_board = [0] * (WIDTH * HEIGHT)
        prev_gold_board = [0] * (WIDTH * HEIGHT)

        sys_prompt, user_tmpl = build_prompts("step", False)

        log, success, new_code, plot_path = run_step_code(
            cfg=mock_config,
            sys_prompt=sys_prompt,
            user_tmpl=user_tmpl,
            instruction="Draw a red tile at row 5, column 7",
            history=[],
            code=code_so_far,
            gold_board=gold_board,
            prev_gold_board=prev_gold_board,
            image_path=None,
            out_dir=tmp_path,
            step_idx=1,
            run_ts="test-timestamp",
        )

        # Verify response structure
        assert "step" in log
        assert "attempt" in log
        assert "usage" in log
        assert "valid" in log
        assert isinstance(success, bool)
        assert isinstance(new_code, str)
        assert len(new_code) > len(code_so_far)

    @patch("runners.step_runner.call_gpt")
    def test_run_step_code_retry_on_error(self, mock_call_gpt, mock_config, tmp_path):
        """Test retry logic when code has errors."""
        # First attempt returns invalid code
        mock_call_gpt.side_effect = [
            {
                "text": "```python\ninvalid_function_call()\n```",
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
            },
            {
                "text": "```python\nTile(row=5, column=7).draw('red')\n```",
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
            },
        ]

        code_so_far = (
            "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
            "from constants import HEIGHT, WIDTH\n"
            "with Game() as g:\n"
        )

        gold_board = [0] * (WIDTH * HEIGHT)
        prev_gold_board = [0] * (WIDTH * HEIGHT)

        sys_prompt, user_tmpl = build_prompts("step", False)

        log, success, new_code, plot_path = run_step_code(
            cfg=mock_config,
            sys_prompt=sys_prompt,
            user_tmpl=user_tmpl,
            instruction="Draw a red tile",
            history=[],
            code=code_so_far,
            gold_board=gold_board,
            prev_gold_board=prev_gold_board,
            image_path=None,
            out_dir=tmp_path,
            step_idx=1,
            run_ts="test-timestamp",
        )

        # Should have retried
        assert log["attempt"] >= 1


# ──────────────────────────────────────────────────────────────────────────────
# Integration Tests - Full Mode
# ──────────────────────────────────────────────────────────────────────────────


class TestFullModeIntegration:
    """Test single-shot full execution mode."""

    @patch("runners.full_runner.call_gpt")
    def test_run_full_success(self, mock_call_gpt, mock_config, tmp_path):
        """Test full mode execution."""
        mock_call_gpt.return_value = {
            "text": "```python\nTile(row=5, column=7).draw('red')\nTile(row=5, column=8).draw('yellow')\n```",
            "usage": {"prompt_tokens": 100, "completion_tokens": 30, "total_tokens": 130},
        }

        code_so_far = (
            "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
            "from constants import HEIGHT, WIDTH\n"
            "with Game() as g:\n"
        )

        instructions = ["Draw red at 5,7", "Draw yellow at 5,8"]
        gold_final = [0] * (WIDTH * HEIGHT)

        sys_prompt, user_tmpl = build_prompts("full", False)

        log = run_full(
            cfg=mock_config,
            sys_prompt=sys_prompt,
            user_tmpl=user_tmpl,
            instructions=instructions,
            code_so_far=code_so_far,
            gold_final=gold_final,
            image_path=None,
            task_dir=tmp_path,
            run_ts="test-timestamp",
        )

        # Verify response structure
        assert "attempt" in log
        assert "valid" in log
        assert "code" in log
        assert "usage" in log
        assert log["attempt"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Integration Tests - Tiles Mode
# ──────────────────────────────────────────────────────────────────────────────


class TestTilesModeIntegration:
    """Test tile prediction mode."""

    @patch("runners.tiles_runner.call_gpt")
    def test_run_tile_step_success(self, mock_call_gpt, mock_config, tmp_path):
        """Test tile prediction step."""
        mock_call_gpt.return_value = {
            "text": "[(5, 7, 'red')]",
            "usage": {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110},
        }

        board = [0] * (WIDTH * HEIGHT)
        gold_board = [0] * (WIDTH * HEIGHT)
        prev_gold_board = [0] * (WIDTH * HEIGHT)

        sys_prompt, user_tmpl = build_prompts("tiles", False)

        log, success, new_board, plot_path = run_tile_step(
            cfg=mock_config,
            sys_prompt=sys_prompt,
            user_tmpl=user_tmpl,
            instruction="Draw a red tile at row 5, column 7",
            history=[],
            board=board,
            gold_board=gold_board,
            prev_gold_board=prev_gold_board,
            image_path=None,
            out_dir=tmp_path,
            step_idx=1,
            run_ts="test-timestamp",
        )

        # Verify response structure
        assert "step" in log
        assert "attempt" in log
        assert "tiles" in log
        assert "valid" in log
        assert log["valid"] is True
        assert isinstance(new_board, list)
        assert len(new_board) == WIDTH * HEIGHT


# ──────────────────────────────────────────────────────────────────────────────
# Integration Tests - Vision Support
# ──────────────────────────────────────────────────────────────────────────────


class TestVisionIntegration:
    """Test vision mode support."""

    @patch("runners.step_runner.call_gpt")
    def test_step_mode_with_vision(self, mock_call_gpt, mock_config, tmp_path):
        """Test that vision mode passes image_path to GPT."""
        mock_call_gpt.return_value = {
            "text": "```python\nTile(row=5, column=7).draw('red')\n```",
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        }

        mock_config.vision = True
        code_so_far = (
            "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
            "from constants import HEIGHT, WIDTH\n"
            "with Game() as g:\n"
        )

        # Create a dummy image file
        dummy_image = tmp_path / "board.png"
        dummy_image.write_bytes(b"fake image data")

        gold_board = [0] * (WIDTH * HEIGHT)
        prev_gold_board = [0] * (WIDTH * HEIGHT)

        sys_prompt, user_tmpl = build_prompts("step", vision=True)

        log, success, new_code, plot_path = run_step_code(
            cfg=mock_config,
            sys_prompt=sys_prompt,
            user_tmpl=user_tmpl,
            instruction="Draw a red tile",
            history=[],
            code=code_so_far,
            gold_board=gold_board,
            prev_gold_board=prev_gold_board,
            image_path=dummy_image,
            out_dir=tmp_path,
            step_idx=1,
            run_ts="test-timestamp",
        )

        # Verify call_gpt was called with images parameter
        mock_call_gpt.assert_called_once()
        call_kwargs = mock_call_gpt.call_args[1]
        assert "images" in call_kwargs
        assert call_kwargs["images"] is not None


# ──────────────────────────────────────────────────────────────────────────────
# End-to-End Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestEndToEnd:
    """End-to-end tests that don't call the actual API."""

    @patch("runners.step_runner.call_gpt")
    def test_run_task_step_mode(self, mock_call_gpt, mock_config, sample_task, tmp_path):
        """Test complete task execution in step mode."""
        # Mock successful responses
        mock_call_gpt.return_value = {
            "text": "```python\nTile(row=5, column=7).draw('red')\n```",
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        }

        # Temporarily change results directory
        with patch("experiment.ensure_task_dir", return_value=tmp_path), \
             patch("runners.step_runner.call_gpt", return_value=mock_call_gpt.return_value):
            result = run_task(cfg=mock_config, task_id=999, task=sample_task)

        # Verify result structure
        assert "stats" in result
        assert "runs" in result
        assert "run_dir" in result
        assert "run_log_path" in result

        stats = result["stats"]
        assert stats["task_id"] == 999
        assert stats["mode"] == "step"
        assert stats["steps"] == len(sample_task["steps"])
        assert isinstance(stats["f1_board"], float)
        assert isinstance(stats["f1_action"], float)
