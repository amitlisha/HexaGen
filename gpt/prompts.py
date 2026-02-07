from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional

from gpt.runner_utils import DATA_DIR


def build_prompts(mode: str, vision: bool = False, api_spec_file: Optional[str] = None, dataset: str = "hexagons") -> Tuple[str, str]:
    """Load system and user templates for the selected mode.

    Args:
        mode: Experiment mode ('code-step', 'code-full', 'code-step-full', 'tiles-step', 'tiles-full', 'tiles-step-full', 'python-full')
        vision: Whether to use vision-enabled system prompt
        api_spec_file: Optional path to custom API spec file (for generated libraries)
                      If None, uses default hexagen_api_spec.txt
        dataset: Dataset name ('hexagons' or 'larc')

    Returns:
        Tuple of (system_prompt, user_template)
    """
    # Select shared prompt based on dataset
    if dataset == "larc":
        shared_sys_p = DATA_DIR / "larc_shared_system_prompt.txt"
    else:
        shared_sys_p = DATA_DIR / "shared_system_prompt.txt"

    if mode in ("tiles-step", "tiles-full", "tiles-step-full"):
        if dataset == "larc":
            # LARC uses its own prompts (no vision variant yet)
            sys_p = DATA_DIR / "larc_tiles_system_prompt.txt"
            user_p = DATA_DIR / "larc_tiles_user_message.txt"
        else:
            # Hexagons tiles prompts
            if vision:
                sys_p = DATA_DIR / "tiles_with_vision_system_prompt.txt"
            else:
                sys_p = DATA_DIR / "tiles_system_prompt.txt"
            if mode == "tiles-step-full":
                user_p = DATA_DIR / "tiles_step_full_user_message.txt"
            else:
                user_p = DATA_DIR / "tiles_user_message.txt"
    elif mode == "python-full":
        if dataset == "larc":
            # LARC uses its own python prompts
            sys_p = DATA_DIR / "larc_python_system_prompt.txt"
            user_p = DATA_DIR / "larc_python_user_message.txt"
        else:
            # Hexagons python prompts
            sys_p = DATA_DIR / "python_system_prompt.txt"
            user_p = DATA_DIR / "python_user_message.txt"
    else:
        if dataset == "larc":
            sys_p = DATA_DIR / "larc_code_full_system_prompt.txt"
            user_p = DATA_DIR / "larc_code_full_user_message.txt"
        else:
            if vision:
                sys_p = DATA_DIR / "code_with_vision_system_prompt.txt"
            else:
                sys_p = DATA_DIR / "code_system_prompt.txt"
            # Use template file for code mode (supports dynamic API spec)
            if mode == "code-step-full":
                user_p = DATA_DIR / "code_step_full_user_message_template.txt"
            else:
                user_p = DATA_DIR / "code_user_message_template.txt"

    system_tmpl = f"{shared_sys_p.read_text()}\n\n{sys_p.read_text()}"
    user_tmpl = user_p.read_text()

    # Inject API spec if we're in code mode (but not python-full)
    if mode not in ("tiles-step", "tiles-full", "tiles-step-full", "python-full"):
        # Load API spec (either custom or default)
        if api_spec_file:
            api_spec_path = Path(api_spec_file)
        else:
            if dataset == "larc":
                api_spec_path = DATA_DIR / "larc_api_spec.txt"
            else:
                api_spec_path = DATA_DIR / "hexagen_api_spec.txt"

        if not api_spec_path.exists():
            raise FileNotFoundError(f"API spec file not found: {api_spec_path}")

        api_spec = api_spec_path.read_text()
        user_tmpl = user_tmpl.replace("{API_SPEC}", api_spec)

    # Validate required placeholders
    if dataset == "larc" and mode == "code-full":
        tags = ["{INPUT_GRID}", "{NEXT_STEP}"]
    else:
        tags = ["{HISTORY_BLOCK}", "{NEXT_STEP}"]
        if mode not in ("tiles-step", "tiles-full", "tiles-step-full", "python-full"):
            tags.append("{CODE_SO_FAR}")
        if mode in ("code-step-full", "tiles-step-full"):
            tags.append("{ALL_INSTRUCTIONS}")
    
    for tag in tags:
        if tag not in user_tmpl:
            raise ValueError(f"{user_p.name} missing placeholder {tag}")
    return system_tmpl, user_tmpl


def make_user_prompt(instr: str, history: List[str], template: str, code: str) -> str:
    """Format a prompt for code generation mode."""
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    return (
        template.replace("{HISTORY_BLOCK}", hist_block)
        .replace("{CODE_SO_FAR}", code.rstrip())
        .replace("{NEXT_STEP}", f"    # TODO: {instr.strip()}")
    )


def make_tile_prompt(instr: str, history: List[str], template: str) -> str:
    """Format prompt for tile prediction mode."""
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    return template.replace("{HISTORY_BLOCK}", hist_block).replace(
        "{NEXT_STEP}", instr.strip()
    )


def make_code_step_full_prompt(instr: str, history: List[str], all_instructions: List[str], template: str, code: str) -> str:
    """Format a prompt for code-step-full mode (all instructions visible, solve one at a time)."""
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    all_instr_block = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(all_instructions))
    current_step_num = len(history) + 1
    return (
        template.replace("{HISTORY_BLOCK}", hist_block)
        .replace("{ALL_INSTRUCTIONS}", all_instr_block)
        .replace("{CODE_SO_FAR}", code.rstrip())
        .replace("{NEXT_STEP}", f"    # TODO (step {current_step_num}): {instr.strip()}")
    )


def make_tiles_step_full_prompt(instr: str, history: List[str], all_instructions: List[str], template: str) -> str:
    """Format prompt for tiles-step-full mode (all instructions visible, predict tiles one at a time)."""
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    all_instr_block = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(all_instructions))
    current_step_num = len(history) + 1
    return (
        template.replace("{HISTORY_BLOCK}", hist_block)
        .replace("{ALL_INSTRUCTIONS}", all_instr_block)
        .replace("{NEXT_STEP}", f"{current_step_num}. {instr.strip()}")
    )


def format_grid_as_tuples(board_2d: List[List[int]]) -> str:
    """Format a 2D grid as tuples: [(height, width), (r, c, color), ...] (1-indexed)."""
    height = len(board_2d)
    width = len(board_2d[0]) if board_2d else 0
    tuples = [f"({height}, {width})"]
    for r, row in enumerate(board_2d, 1):
        for c, color in enumerate(row, 1):
            tuples.append(f"({r}, {c}, {color})")
    return "[" + ", ".join(tuples) + "]"


def make_larc_tile_prompt(instr: str, input_board_2d: List[List[int]], template: str) -> str:
    """Format prompt for LARC tile prediction.

    Args:
        instr: Task description (combined see + grid_size + do)
        input_board_2d: Input grid as 2D list (list of rows)
        template: User message template
    """
    grid_str = format_grid_as_tuples(input_board_2d)
    return (
        template.replace("{INPUT_GRID}", grid_str)
        .replace("{HISTORY_BLOCK}", "(none)")
        .replace("{NEXT_STEP}", instr.strip())
    )
