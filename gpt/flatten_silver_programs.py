"""Post-process silver/gold programs from get_tiles()-wrapper style into flat, wrapper-free
scripts: hoist the function body to top-level statements and replace its final `return <expr>`
with `tiles = sorted(<expr>)`.

Why this exists: HexaGen's own execution harness (extract_and_execute_python, python-full mode,
etc.) is built around every generated program defining `def get_tiles(): ... return tiles` — that
contract stays as-is here, this script only transforms a COPY of the data for external consumers
that don't share it (e.g. REGAL's library-learning pipeline, which expects a flat script ending
in an assignment, and which — being provider-agnostic about the source of its "python" task
data — has no special-casing for the fact every HexaGen program shares that one function name).
Left un-flattened, REGAL's helper-usage bookkeeping cross-references function-call names against
its shared codebank with no concept of "this name is the required per-task entry point, not a
reusable helper," so an unrelated program's identically-named `get_tiles` call gets credited as
reusing whichever one example's function first got copied into the shared codebank under that
name. Flattening removes the function definition (and its name) entirely, making the collision
structurally impossible.

Validated on all 373 sample_idx==0 records of silver_programs_seq5.jsonl: every flattened
program produces byte-identical output to calling the original get_tiles() (0 mismatches).

Usage:
    python -m gpt.flatten_silver_programs --input silver_programs_seq5.jsonl \
        --output silver_programs_seq5_flat.jsonl
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def strip_markdown_fences(code: str) -> str:
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
    return code.strip()


def inline_entry_point(program: str) -> str:
    """Hoist the entry-point function's body to module level, replacing its final
    `return <expr>` with `tiles = sorted(<expr>)`. Any other top-level function defs (helpers)
    are kept, in their original relative order. Raises ValueError if the program doesn't match
    the expected shape (a `get_tiles`-named function, or exactly one top-level function, ending
    in a `return <expr>` statement).
    """
    tree = ast.parse(strip_markdown_fences(program))

    func_defs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    named = [n for n in func_defs if n.name == "get_tiles"]
    if named:
        func_def = named[-1]
    elif len(func_defs) == 1:
        func_def = func_defs[0]
    else:
        raise ValueError(
            f"no function named get_tiles and not exactly one top-level function def "
            f"(found {len(func_defs)}: {[f.name for f in func_defs]})"
        )

    body = list(func_def.body)
    if not body or not isinstance(body[-1], ast.Return) or body[-1].value is None:
        raise ValueError("function does not end in a `return <expr>` statement")

    return_stmt = body.pop()
    assign = ast.Assign(
        targets=[ast.Name(id="tiles", ctx=ast.Store())],
        value=ast.Call(func=ast.Name(id="sorted", ctx=ast.Load()), args=[return_stmt.value], keywords=[]),
    )

    preamble = [n for n in tree.body if n is not func_def]
    new_module = ast.Module(body=preamble + body + [assign], type_ignores=[])
    ast.fix_missing_locations(new_module)
    return ast.unparse(new_module)


def flatten_file(records: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[tuple]]:
    out, skipped = [], []
    for r in records:
        try:
            flat_code = inline_entry_point(r["program"])
            # ast.parse alone won't catch this: a nested helper inside the original get_tiles()
            # that used `nonlocal` to mutate a variable in get_tiles's local scope becomes
            # invalid once that body is hoisted to module level (nonlocal needs an enclosing
            # function frame, which no longer exists) — only a full compile() surfaces it.
            compile(flat_code, "<flattened>", "exec")
            flat = dict(r)
            flat["program"] = flat_code
            out.append(flat)
        except (SyntaxError, ValueError) as e:
            skipped.append((r.get("image_id"), r.get("index"), str(e)))
    return out, skipped


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    records = [json.loads(line) for line in args.input.open()]
    out, skipped = flatten_file(records)

    with args.output.open("w") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Flattened {len(out)}/{len(records)} record(s) to {args.output}")
    if skipped:
        print(f"Skipped {len(skipped)} record(s) that didn't fit the expected shape:")
        for image_id, index, err in skipped[:10]:
            print(f"  {image_id} (index={index}): {err}")


if __name__ == "__main__":
    main()
