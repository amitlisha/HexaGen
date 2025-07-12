from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from runner_utils import DATA_DIR


def build_prompts(mode: str) -> Tuple[str, str]:
    """Load system and user templates for the selected mode."""
    shared_sys_p = DATA_DIR / "shared_system_prompt.txt"

    if mode == "tiles":
        sys_p = DATA_DIR / "tiles_system_prompt.txt"
        user_p = DATA_DIR / "tiles_user_message.txt"
    else:
        sys_p = DATA_DIR / "code_system_prompt.txt"
        user_p = DATA_DIR / "code_user_message.txt"

    system_tmpl = f"{shared_sys_p.read_text()}\n\n{sys_p.read_text()}"
    user_tmpl = user_p.read_text()

    tags = ["{HISTORY_BLOCK}", "{NEXT_STEP}"]
    if mode != "tiles":
        tags.append("{CODE_SO_FAR}")
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
