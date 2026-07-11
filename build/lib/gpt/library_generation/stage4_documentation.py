"""Stage 4: DSL API Specification Generation.

This stage generates a formal API specification for the generated library that can be
integrated into experiment prompts. The API spec follows the same format as the
existing Hexagen API documentation.

Per-class generation: each class gets its own LLM call for focused, high-quality specs.
Supports sequential, parallel (ThreadPoolExecutor), and Batch API execution modes.

DOMAIN-AGNOSTIC: Works with any generated library.
"""

from __future__ import annotations

import ast
import json
import re
import argparse
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple


def load_implementation(impl_file: Path) -> str:
    """Load generated implementation from Stage 3."""
    if not impl_file.exists():
        raise FileNotFoundError(f"Implementation not found: {impl_file}")
    return impl_file.read_text(encoding="utf-8")


def load_sample_instructions(data_path: str, num_samples: int = 10, seed: int = 42) -> List[str]:
    """Load sample instructions for documentation examples.

    Args:
        data_path: Path to standardized JSONL file
        num_samples: Number of instructions to sample
        seed: Random seed for reproducibility

    Returns:
        List of sampled instruction strings
    """
    import random
    random.seed(seed)

    all_instructions = []
    data_file = Path(data_path)

    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            for step in obj["steps"]:
                all_instructions.append(step["instruction"])

    # Sample without replacement
    sample_size = min(num_samples, len(all_instructions))
    return random.sample(all_instructions, sample_size)


# ---------------------------------------------------------------------------
# AST-based class extraction
# ---------------------------------------------------------------------------

def _extract_class_ranges_regex(lines: List[str]) -> List[Tuple[str, int, int]]:
    """Regex fallback for extracting class ranges when ast.parse fails."""
    class_ranges: List[Tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        match = re.match(r'^class\s+(\w+)', lines[i])
        if match:
            class_name = match.group(1)
            start = i + 1  # 1-indexed
            # Find end: next top-level definition or EOF
            end = len(lines)
            for j in range(i + 1, len(lines)):
                # A line at column 0 that starts a new class/function/variable
                if lines[j] and not lines[j][0].isspace() and not lines[j].startswith('#'):
                    if re.match(r'^(class |def |[A-Z_]+ =)', lines[j]):
                        end = j  # 0-indexed, exclusive
                        break
            class_ranges.append((class_name, start, end))
            i = end
        else:
            i += 1
    return class_ranges


def parse_classes_from_implementation(implementation: str) -> Tuple[str, Dict[str, str]]:
    """Parse implementation code to extract per-class source and module header.

    Uses AST to find class definitions and extracts their source text from
    the original code (preserving formatting).

    Args:
        implementation: Full library source code

    Returns:
        Tuple of (header_source, class_sources) where:
        - header_source: module-level code (imports, constants, helpers)
        - class_sources: dict mapping class_name -> class source code
    """
    lines = implementation.split('\n')

    try:
        tree = ast.parse(implementation)
        # Find all top-level class definitions with their line ranges
        class_ranges: List[Tuple[str, int, int]] = []  # (name, start_line, end_line)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_ranges.append((node.name, node.lineno, node.end_lineno))
    except SyntaxError:
        # Fallback: regex-based extraction for LLM-generated code with syntax errors
        print("WARNING: ast.parse failed (syntax error in generated code), using regex fallback")
        class_ranges = _extract_class_ranges_regex(lines)

    # Sort by start line
    class_ranges.sort(key=lambda x: x[1])

    # Extract header: everything before the first class
    if class_ranges:
        header_end = class_ranges[0][1] - 1  # 1-indexed to 0-indexed
        header_source = '\n'.join(lines[:header_end]).strip()
    else:
        header_source = implementation.strip()

    # Extract each class's source code
    class_sources: Dict[str, str] = {}
    for name, start, end in class_ranges:
        # AST lines are 1-indexed
        class_source = '\n'.join(lines[start - 1:end])
        class_sources[name] = class_source

    return header_source, class_sources


def extract_module_constants(implementation: str) -> List[Tuple[str, str]]:
    """Extract module-level constant assignments for the spec header.

    Returns list of (name, value_repr) tuples for top-level assignments
    to UPPER_CASE names.
    """
    try:
        tree = ast.parse(implementation)
    except SyntaxError:
        # Fallback: regex-based extraction for UPPER_CASE = ... assignments
        constants = []
        for match in re.finditer(r'^([A-Z_]+)\s*=\s*(.+)', implementation, re.MULTILINE):
            constants.append((match.group(1), match.group(2).strip()))
        return constants

    constants = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    # Get the source text for the value
                    lines = implementation.split('\n')
                    value_lines = lines[node.value.lineno - 1:node.value.end_lineno]
                    if value_lines:
                        # Get from column offset to end
                        value_lines[0] = value_lines[0][node.value.col_offset:]
                        value_text = '\n'.join(value_lines).strip()
                    else:
                        value_text = "..."
                    constants.append((target.id, value_text))

    return constants


def extract_public_classes(implementation: str) -> List[str]:
    """Extract names of public classes (not starting with _) in definition order."""
    try:
        tree = ast.parse(implementation)
    except SyntaxError:
        # Fallback: regex-based extraction
        return [m.group(1) for m in re.finditer(r'^class\s+(\w+)', implementation, re.MULTILINE)
                if not m.group(1).startswith('_')]

    classes = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
            classes.append(node.name)
    return classes


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

STAGE4_SYSTEM_PROMPT = """\
You are a technical writer creating concise API reference documentation.
Your output will be used by LLMs as their ONLY reference when writing code with this library.
Brevity and precision are critical — every extra word wastes context tokens.
Accuracy is paramount — if the LLM calls a method that doesn't exist or passes wrong arguments, the code will fail."""


def _build_class_api_spec_prompt(
    class_name: str,
    class_source: str,
    full_implementation: str,
    sample_instructions: List[str],
    domain_description: str,
) -> str:
    """Build prompt for generating the API spec of a single class."""
    instructions_text = "\n".join(f"- {instr}" for instr in sample_instructions)
    domain_context = f" (domain: {domain_description})" if domain_description else ""

    return f"""Write the API spec section for class `{class_name}`{domain_context}.

CLASS SOURCE CODE:
```python
{class_source}
```

FULL LIBRARY (for context on types, constants, and other classes):
```python
{full_implementation}
```

EXAMPLE INSTRUCTIONS this library handles:
{instructions_text}

OUTPUT FORMAT — produce ONLY a Class section like this:

Class: ClassName                              # optional brief role comment
  # ── Category Name ──────────────────────── # group related methods
  Method: method_name(param1:type, param2:type) -> ReturnType    # brief inline note
    Param options: param1 ∈ {{'val1','val2'}} ∪ SOME_CONSTANT
    Notes: One sentence max. Only when inline comment isn't enough.
    # CRITICAL: warning about non-obvious constraint or common mistake
  Method: another(p:type) -> Type             # auto-paints / mutates board
  Static: class_method(args) -> Type
  Property: name:type                         # brief note if needed

RULES:
1. Document ONLY public methods (no _ prefix). Skip __repr__, __str__, __hash__, __eq__.
2. Be CONCISE: prefer inline `#` comments over multi-line Notes. Use Notes only when truly needed, and keep to ONE sentence.
3. GROUP methods by function (e.g. "Drawing/painting", "Navigation", "Geometric queries", "Set operations", "Construction"). Use `# ──` section headers.
4. Mark methods that modify state (draw on board, mutate object) with `# auto-paints` or `# mutates` inline.
5. Note what methods return: self (for chaining), new object, list of affected items, etc.
6. Add `# CRITICAL:` warnings for methods that are easy to misuse, have non-obvious constraints, or where passing wrong arguments is a common mistake.
7. Use compact set notation for param options: `param ∈ {{'a','b'}} ∪ CONSTANT` instead of listing all values.
8. Show inheritance with "(inherits BaseClass)" if applicable.
9. Do NOT include snippets, examples, or import statements — those are generated separately.
10. Do NOT wrap output in markdown code blocks."""


def _build_snippets_prompt(
    per_class_specs: Dict[str, str],
    sample_instructions: List[str],
    domain_description: str,
) -> str:
    """Build prompt for generating usage snippets and closing notes."""
    all_specs = "\n\n".join(
        f"# ---\n{spec}" for spec in per_class_specs.values()
    )
    instructions_text = "\n".join(f"- {instr}" for instr in sample_instructions)
    domain_context = f" for {domain_description}" if domain_description else ""

    return f"""Given this API specification{domain_context}, write 3-5 usage snippets and important notes.

API SPEC:
{all_specs}

EXAMPLE INSTRUCTIONS the library handles:
{instructions_text}

OUTPUT FORMAT:

Snippet: [descriptive title of what this snippet demonstrates]
  [2-6 lines of Python code showing a realistic usage pattern]

Note: [important usage note — one sentence]

RULES:
1. Each snippet should demonstrate a REALISTIC task pattern from the example instructions, not trivial operations.
2. Show how classes work TOGETHER (e.g., create objects then transform/combine them).
3. Include the most common workflow: object creation → manipulation → output.
4. Add Notes for important conventions: coordinate systems, context managers, return value behavior, common gotchas.
5. Do NOT repeat method signatures — snippets complement the spec, not duplicate it.
6. Do NOT wrap output in markdown code blocks.
7. Keep snippets SHORT (2-6 lines of code each). No comments in the code unless truly clarifying."""


# ---------------------------------------------------------------------------
# Per-class generation
# ---------------------------------------------------------------------------

def generate_class_api_spec(
    class_name: str,
    class_source: str,
    full_implementation: str,
    sample_instructions: List[str],
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
    request_timeout: int = 300,
) -> str:
    """Generate API spec for a single class."""
    from gpt.llm_wrapper import call_llm

    prompt = _build_class_api_spec_prompt(
        class_name, class_source, full_implementation,
        sample_instructions, domain_description,
    )

    print(f"  Generating API spec for class {class_name}...")

    response = call_llm(
        prompt=prompt,
        system_prompt=STAGE4_SYSTEM_PROMPT,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
        request_timeout=request_timeout,
    )

    return response["text"]


def generate_snippets(
    per_class_specs: Dict[str, str],
    sample_instructions: List[str],
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
    request_timeout: int = 300,
) -> str:
    """Generate usage snippets and notes section."""
    from gpt.llm_wrapper import call_llm

    prompt = _build_snippets_prompt(
        per_class_specs, sample_instructions, domain_description,
    )

    print(f"  Generating usage snippets...")

    response = call_llm(
        prompt=prompt,
        system_prompt=STAGE4_SYSTEM_PROMPT,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
        request_timeout=request_timeout,
    )

    return response["text"]


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def build_spec_header(
    implementation: str,
    public_classes: List[str],
    domain_description: str,
) -> str:
    """Build the deterministic header section (imports, constants) — no LLM needed."""
    constants = extract_module_constants(implementation)

    # Build import line
    classes_str = ", ".join(public_classes)
    # Try to detect module name from the implementation (look for common patterns)
    # Default to "hexagen" as the package name
    import_names = list(public_classes)
    for name, _ in constants:
        import_names.append(name)

    lines = []
    lines.append(f"# ================================  API SPEC  ===============================")
    lines.append(f"# One entity per line; two-space indentation shows containment.")
    lines.append(f"# Inline '#' comments clarify hidden behaviour.")
    lines.append(f"# '# CRITICAL:' marks common pitfalls.")
    lines.append("")

    # Import line
    lines.append(f"Import: from hexagen import {', '.join(import_names)}")
    lines.append("")

    # Constants
    for name, value in constants:
        lines.append(f"Constant: {name} = {value}")

    return "\n".join(lines)


def assemble_api_spec(
    header: str,
    per_class_specs: Dict[str, str],
    snippets: str,
) -> str:
    """Combine header, per-class specs, and snippets into final API spec."""
    parts = [header, ""]

    separator = "# -------------------------------------------------------------------------------------"

    for class_name, spec in per_class_specs.items():
        parts.append(separator)
        # Clean up any markdown code block wrappers the LLM might have added
        cleaned = spec.strip()
        if cleaned.startswith("```"):
            # Remove opening ```...
            first_nl = cleaned.index('\n') if '\n' in cleaned else len(cleaned)
            cleaned = cleaned[first_nl + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].rstrip()
        parts.append(cleaned)

    parts.append("")
    parts.append(separator)

    # Clean snippets similarly
    cleaned_snippets = snippets.strip()
    if cleaned_snippets.startswith("```"):
        first_nl = cleaned_snippets.index('\n') if '\n' in cleaned_snippets else len(cleaned_snippets)
        cleaned_snippets = cleaned_snippets[first_nl + 1:]
    if cleaned_snippets.endswith("```"):
        cleaned_snippets = cleaned_snippets[:-3].rstrip()
    parts.append(cleaned_snippets)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Legacy monolithic generation (kept as fallback)
# ---------------------------------------------------------------------------

STAGE4_SYSTEM_PROMPT_MONOLITHIC = "You are a technical writer creating formal API specifications for LLM consumption."


def _build_api_spec_prompt_monolithic(
    implementation: str,
    sample_instructions: List[str],
    domain_description: str,
) -> str:
    """Build the monolithic prompt for API spec generation (legacy fallback)."""
    instructions_text = "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(sample_instructions))
    domain_context = f" for {domain_description}" if domain_description else ""

    return f"""Create a formal API specification for this Python library{domain_context}.

LIBRARY CODE:
```python
{implementation}
```

EXAMPLE INSTRUCTIONS (what the library handles):
{instructions_text}

OUTPUT FORMAT (based on Hexagen API style):

# ================================  [LIBRARY NAME] API SPEC  ===============================
# One entity per line; two-space indentation shows containment.
# Extra "Notes:" lines clarify hidden behaviour.

Import: [import statement]

Constant: [NAME] = [value or type]

# -------------------------------------------------------------------------------------
Class: [ClassName]
  Method: __init__([parameters with types])
    Notes: [optional clarifications]
  Method: [method_name]([parameters with types]) -> [return_type]
    Param options: [if method accepts specific values, list them]
    Notes: [optional clarifications]
  Property: [property_name]:[type]

# -------------------------------------------------------------------------------------
Class: [AnotherClass] (inherits [BaseClass])
  Method: [method_name]([parameters]) -> [return_type]
  Static: [static_method]([parameters]) -> [return_type]

# -------------------------------------------------------------------------------------
Snippet: [common usage pattern]
Note: [important usage note]

REQUIREMENTS:
- Document ONLY public API (no methods starting with _)
- Clear parameter and return type annotations
- List specific accepted values under "Param options:" when applicable
- Two-space indentation for class members
- Separate sections with dashed lines
- Include important constants
- Show inheritance with "(inherits ClassName)"
- Mark static/class methods with "Static:"
- End with usage snippets and notes

This spec will be used by LLMs to write code - prioritize completeness and precision."""


def generate_api_spec_monolithic(
    implementation: str,
    sample_instructions: List[str],
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
) -> str:
    """Generate API spec in a single monolithic LLM call (legacy fallback)."""
    from gpt.llm_wrapper import call_llm

    prompt = _build_api_spec_prompt_monolithic(implementation, sample_instructions, domain_description)

    print(f"Generating API specification (monolithic)...")

    response = call_llm(
        prompt=prompt,
        system_prompt=STAGE4_SYSTEM_PROMPT_MONOLITHIC,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
    )

    return response["text"]


# Keep old names as aliases for backward compatibility
generate_api_spec = generate_api_spec_monolithic
_build_api_spec_prompt = _build_api_spec_prompt_monolithic


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


# ---------------------------------------------------------------------------
# Main stage runner
# ---------------------------------------------------------------------------

def run_stage4(cfg: argparse.Namespace, output_dir: Path, stage3_result: Dict) -> Dict:
    """Run Stage 4: DSL API Specification Generation.

    Generates per-class API specs in parallel, then assembles them with a
    deterministic header and LLM-generated usage snippets.

    Supports three execution modes:
    - Sequential (workers <= 1, no --batch): one class at a time
    - ThreadPoolExecutor (workers > 1): parallel sync calls across classes
    - Batch API (--batch): submit all class requests as a batch job

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage3_result: Results from Stage 3

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 4: DSL API SPECIFICATION GENERATION")
    print(f"{'='*70}\n")

    # Load Stage 3 implementation
    stage3_impl_file = Path(stage3_result["outputs"]["implementation"])
    print(f"Loading implementation from {stage3_impl_file}...")
    implementation = load_implementation(stage3_impl_file)
    print(f"✓ Loaded implementation ({len(implementation)} characters)\n")

    # Load sample instructions for examples
    print(f"Loading sample instructions from {cfg.train_data}...")
    sample_instructions = load_sample_instructions(
        cfg.train_data,
        num_samples=10,
        seed=cfg.seed
    )
    print(f"✓ Loaded {len(sample_instructions)} sample instructions\n")

    # Step 1: Parse implementation into per-class sections
    print("Step 1: Parsing implementation by class...")
    print("-" * 70)

    header_source, class_sources = parse_classes_from_implementation(implementation)
    public_classes = extract_public_classes(implementation)

    # Filter to only public classes
    class_sources = {name: src for name, src in class_sources.items() if name in public_classes}

    print(f"✓ Found {len(class_sources)} public classes: {', '.join(class_sources.keys())}\n")

    # Step 2: Build deterministic header
    print("Step 2: Building spec header...")
    print("-" * 70)

    spec_header = build_spec_header(implementation, public_classes, cfg.domain_description)
    print(f"✓ Header built ({len(spec_header)} chars)\n")

    # Step 3: Generate per-class API specs
    print("Step 3: Generating per-class API specs...")
    print("-" * 70)

    # Each entry: (class_name, spec_text)
    class_spec_responses: List[Tuple[str, str]] = []

    if getattr(cfg, "batch", False) or getattr(cfg, "batch_resume", None):
        # --- Batch API mode ---
        print("Using LLM Batch API for per-class spec generation...")
        import sys

        gpt_dir = Path(__file__).parent.parent
        if str(gpt_dir) not in sys.path:
            sys.path.insert(0, str(gpt_dir))

        from llm_wrapper import (
            _is_gemini_model,
            build_openai_messages,
            build_openai_request_body,
            build_gemini_batch_request,
            submit_openai_batch,
            poll_openai_batch,
            parse_batch_results,
            submit_gemini_batch,
            poll_gemini_batch,
            parse_gemini_batch_results,
        )

        is_gemini = _is_gemini_model(cfg.model)
        class_names = list(class_sources.keys())

        if is_gemini:
            gemini_requests = []
            for class_name in class_names:
                prompt = _build_class_api_spec_prompt(
                    class_name, class_sources[class_name], implementation,
                    sample_instructions, cfg.domain_description,
                )
                request = build_gemini_batch_request(
                    prompt=prompt,
                    system_prompt=STAGE4_SYSTEM_PROMPT,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    thinking_level=getattr(cfg, "thinking_level", None),
                )
                gemini_requests.append(request)

            # Add snippets request at the end
            # (will be generated after per-class specs are assembled)

            if getattr(cfg, "batch_resume", None):
                print(f"Resuming Gemini batch: {cfg.batch_resume}")
                batch_job = poll_gemini_batch(
                    cfg.batch_resume,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )
            else:
                display_name = f"{cfg.experiment_name}-stage4-{cfg.model}"
                job_name = submit_gemini_batch(gemini_requests, cfg.model, display_name)
                print(f"Created Gemini batch: {job_name}")
                batch_job = poll_gemini_batch(
                    job_name,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )

            batch_results = parse_gemini_batch_results(batch_job, gemini_requests)

            for i, class_name in enumerate(class_names):
                result = batch_results.get(i)
                if result and not result.get("error"):
                    class_spec_responses.append((class_name, result["text"]))
                else:
                    err = (result or {}).get("error", "unknown error")
                    print(f"  ✗ {class_name}: {err}")

        else:
            # OpenAI Batch API
            jsonl_lines = []
            for class_name in class_names:
                prompt = _build_class_api_spec_prompt(
                    class_name, class_sources[class_name], implementation,
                    sample_instructions, cfg.domain_description,
                )
                messages = build_openai_messages(prompt=prompt, system_prompt=STAGE4_SYSTEM_PROMPT)
                body = build_openai_request_body(
                    messages=messages,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    reasoning_effort=getattr(cfg, "thinking_effort", None),
                )
                jsonl_lines.append(json.dumps({
                    "custom_id": f"stage4_class_{class_name}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": body,
                }))

            if getattr(cfg, "batch_resume", None):
                print(f"Resuming OpenAI batch: {cfg.batch_resume}")
                batch_obj = poll_openai_batch(
                    cfg.batch_resume,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )
            else:
                batch_id = submit_openai_batch(jsonl_lines)
                print(f"Created OpenAI batch: {batch_id}")
                batch_obj = poll_openai_batch(
                    batch_id,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )

            batch_results = {}
            if batch_obj.output_file_id:
                batch_results.update(parse_batch_results(batch_obj.output_file_id))
            if batch_obj.error_file_id:
                batch_results.update(parse_batch_results(batch_obj.error_file_id))

            for class_name in class_names:
                custom_id = f"stage4_class_{class_name}"
                result = batch_results.get(custom_id)
                if result and not result.get("error"):
                    class_spec_responses.append((class_name, result["text"]))
                else:
                    err = (result or {}).get("error", "unknown error")
                    print(f"  ✗ {class_name}: {err}")

    elif getattr(cfg, "workers", 1) <= 1:
        # --- Sequential mode ---
        for class_name, class_source in class_sources.items():
            spec_text = generate_class_api_spec(
                class_name=class_name,
                class_source=class_source,
                full_implementation=implementation,
                sample_instructions=sample_instructions,
                domain_description=cfg.domain_description,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                thinking_effort=getattr(cfg, "thinking_effort", None),
                thinking_level=getattr(cfg, "thinking_level", None),
                request_timeout=getattr(cfg, "request_timeout", 300),
            )
            class_spec_responses.append((class_name, spec_text))

    else:
        # --- ThreadPoolExecutor mode ---
        print(f"Using {cfg.workers} parallel workers...")
        with ThreadPoolExecutor(max_workers=cfg.workers) as executor:
            futures = {
                executor.submit(
                    generate_class_api_spec,
                    class_name=class_name,
                    class_source=class_source,
                    full_implementation=implementation,
                    sample_instructions=sample_instructions,
                    domain_description=cfg.domain_description,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    thinking_effort=getattr(cfg, "thinking_effort", None),
                    thinking_level=getattr(cfg, "thinking_level", None),
                    request_timeout=getattr(cfg, "request_timeout", 300),
                ): class_name
                for class_name, class_source in class_sources.items()
            }

            for future in as_completed(futures):
                class_name = futures[future]
                try:
                    spec_text = future.result()
                    class_spec_responses.append((class_name, spec_text))
                except Exception as exc:
                    print(f"  ✗ {class_name} failed: {exc}")

    print(f"\n✓ Generated specs for {len(class_spec_responses)} classes\n")

    # Save per-class raw specs
    per_class_dir = output_dir / "per_class"
    per_class_dir.mkdir(parents=True, exist_ok=True)

    # Preserve class ordering from source code
    per_class_specs: Dict[str, str] = {}
    response_map = {name: text for name, text in class_spec_responses}
    for class_name in public_classes:
        if class_name in response_map:
            per_class_specs[class_name] = response_map[class_name]
            # Save individual spec
            spec_file = per_class_dir / f"{class_name}_spec.txt"
            spec_file.write_text(response_map[class_name], encoding='utf-8')

    # Step 4: Generate usage snippets
    print("Step 4: Generating usage snippets...")
    print("-" * 70)

    if getattr(cfg, "batch", False) or getattr(cfg, "batch_resume", None):
        # For batch mode, generate snippets synchronously (it's just one call)
        snippets = generate_snippets(
            per_class_specs=per_class_specs,
            sample_instructions=sample_instructions,
            domain_description=cfg.domain_description,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            thinking_effort=getattr(cfg, "thinking_effort", None),
            thinking_level=getattr(cfg, "thinking_level", None),
            request_timeout=getattr(cfg, "request_timeout", 300),
        )
    else:
        snippets = generate_snippets(
            per_class_specs=per_class_specs,
            sample_instructions=sample_instructions,
            domain_description=cfg.domain_description,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            thinking_effort=getattr(cfg, "thinking_effort", None),
            thinking_level=getattr(cfg, "thinking_level", None),
            request_timeout=getattr(cfg, "request_timeout", 300),
        )

    print(f"✓ Generated snippets ({len(snippets)} chars)\n")

    # Step 5: Assemble final API spec
    print("Step 5: Assembling final API spec...")
    print("-" * 70)

    api_spec = assemble_api_spec(spec_header, per_class_specs, snippets)

    # Save API spec
    api_spec_file = output_dir / "api_spec.txt"
    api_spec_file.write_text(api_spec, encoding='utf-8')
    print(f"✓ Saved API specification to {api_spec_file}\n")

    # Create summary
    result = {
        "stage": 4,
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "model": cfg.model,
        },
        "outputs": {
            "api_spec": str(api_spec_file),
            "api_spec_length": len(api_spec),
            "classes_documented": list(per_class_specs.keys()),
            "num_classes": len(per_class_specs),
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage4_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 4 COMPLETE")
    print(f"{'='*70}\n")
    print(f"API specification: {api_spec_file} ({len(api_spec)} chars)")
    print(f"Classes documented: {', '.join(per_class_specs.keys())}")
    print(f"\nTo use this in experiments, copy the API spec into your user message template:")
    print(f"  cp {api_spec_file} data/generated_api_spec.txt")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args
    import sys

    cfg = parse_args()

    # Load Stage 3 results
    stage3_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage3"
    stage3_summary = stage3_dir / "stage3_summary.json"

    if not stage3_summary.exists():
        print(f"Error: Stage 3 results not found at {stage3_summary}")
        print("Please run Stage 3 first!")
        sys.exit(1)

    with open(stage3_summary) as f:
        stage3_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage4"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage4(cfg, output_dir, stage3_result)
