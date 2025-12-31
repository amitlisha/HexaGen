"""Stage 3: Implementation Generation from refined API.

This stage takes the refined API proposal from Stage 2 and generates
actual Python code that implements the proposed methods.

Approach:
1. Generate ONLY new methods (not full library) from API proposal
2. Parse generated methods and group by class
3. Programmatically merge methods into base library using AST
4. Validate that base library is preserved and new methods added

This ensures the base library code is never modified by the LLM,
isolating the DSL generation capability for cleaner research evaluation.

DOMAIN-AGNOSTIC: Works with any API design in standard format.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import Dict


def load_api_proposal(api_file: Path) -> str:
    """Load refined API proposal from Stage 2."""
    if not api_file.exists():
        raise FileNotFoundError(f"API proposal not found: {api_file}")
    return api_file.read_text(encoding="utf-8")


def load_base_library(base_lib_path: str) -> str:
    """Load the base library code."""
    lib_file = Path(base_lib_path)
    if not lib_file.exists():
        raise FileNotFoundError(f"Base library not found: {base_lib_path}")
    return lib_file.read_text(encoding="utf-8")


def generate_new_methods(
    api_proposal: str,
    base_lib_code: str,
    base_lib_docs: str,
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Generate ONLY new methods from API proposal (not full library).

    Args:
        api_proposal: Refined API proposal from Stage 2
        base_lib_code: Current base library code
        base_lib_docs: Base library documentation
        domain_description: Brief description of domain
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Python code containing ONLY the new methods
    """
    from gpt.llm_wrapper import call_llm

    domain_context = f" for {domain_description}" if domain_description else ""

    system_prompt = "You are an expert Python developer implementing methods from an API specification."

    prompt = f"""Implement the NEW methods from this API proposal{domain_context}.

API PROPOSAL:
{api_proposal}

BASE LIBRARY (reference):
```python
{base_lib_code}
```

BASE LIBRARY DOCUMENTATION:
{base_lib_docs}

OUTPUT FORMAT - Use this exact structure:
```python
# CLASS: ClassName
def method_name(self, param1: type1, param2: type2) -> ReturnType:
    \"\"\"Brief description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description
    \"\"\"
    # Implementation
    pass
```

REQUIREMENTS:
- Complete implementations with docstrings
- Handle edge cases (None, empty, out-of-bounds)
- Match base library coding style
- Use `# CLASS: ClassName` marker before each method

DO NOT:
- Include existing base library code
- Include class definitions
- Add explanations outside code

Provide ONLY the new method implementations."""

    print(f"Generating new methods from refined API proposal...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response (handles markdown code blocks)."""
    # If response contains markdown code blocks, extract them
    if "```python" in response:
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + len("```")
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()

    # Otherwise return as-is
    return response.strip()


def parse_methods_by_class(methods_code: str) -> Dict[str, list]:
    """Parse generated methods and group them by class.

    Args:
        methods_code: Code containing methods with # CLASS: ClassName markers

    Returns:
        Dictionary mapping class names to lists of method code strings
    """
    import re

    methods_by_class = {}
    current_class = None
    current_method_lines = []

    lines = methods_code.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for class marker
        class_match = re.match(r'^\s*#\s*CLASS:\s*(\w+)', line)
        if class_match:
            # Save previous method if exists
            if current_class and current_method_lines:
                method_code = '\n'.join(current_method_lines).strip()
                if method_code:
                    if current_class not in methods_by_class:
                        methods_by_class[current_class] = []
                    methods_by_class[current_class].append(method_code)
                current_method_lines = []

            current_class = class_match.group(1)
            i += 1
            continue

        # Check for method definition
        if current_class and re.match(r'^\s*def\s+\w+', line):
            # Save previous method if exists
            if current_method_lines:
                method_code = '\n'.join(current_method_lines).strip()
                if method_code:
                    if current_class not in methods_by_class:
                        methods_by_class[current_class] = []
                    methods_by_class[current_class].append(method_code)
                current_method_lines = []

            # Start collecting new method
            current_method_lines.append(line)
            i += 1

            # Collect method body (indented lines)
            base_indent = len(line) - len(line.lstrip())
            while i < len(lines):
                next_line = lines[i]
                # Stop if we hit another def at same or lower indent, or a CLASS marker
                if next_line.strip() and not next_line.startswith(' ' * (base_indent + 1)):
                    if re.match(r'^\s*def\s+\w+', next_line) or re.match(r'^\s*#\s*CLASS:', next_line):
                        break
                current_method_lines.append(next_line)
                i += 1
        else:
            i += 1

    # Save last method
    if current_class and current_method_lines:
        method_code = '\n'.join(current_method_lines).strip()
        if method_code:
            if current_class not in methods_by_class:
                methods_by_class[current_class] = []
            methods_by_class[current_class].append(method_code)

    return methods_by_class


def merge_methods_into_library(base_lib_code: str, methods_by_class: Dict[str, list]) -> str:
    """Merge new methods into base library code using AST manipulation.

    Args:
        base_lib_code: Original base library code
        methods_by_class: Dictionary of class names to method code lists

    Returns:
        Updated library code with new methods added
    """
    import ast
    import textwrap

    # Parse the base library
    try:
        tree = ast.parse(base_lib_code)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse base library: {e}")

    # Find all class definitions
    class_nodes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_nodes[node.name] = node

    # Build the output by inserting methods at appropriate locations
    lines = base_lib_code.split('\n')
    insertions = []  # List of (line_number, indent, method_code) tuples

    for class_name, methods in methods_by_class.items():
        if class_name not in class_nodes:
            print(f"⚠ Warning: Class '{class_name}' not found in base library")
            continue

        class_node = class_nodes[class_name]

        # Find the last line of the class (end of last method/statement)
        if class_node.body:
            last_stmt = class_node.body[-1]
            insert_line = last_stmt.end_lineno

            # Determine class indentation
            class_line = lines[class_node.lineno - 1]
            class_indent = len(class_line) - len(class_line.lstrip())
            method_indent = class_indent + 4  # Standard 4-space indent for methods

            for method_code in methods:
                # Indent the method code properly
                method_lines = method_code.split('\n')

                # Find the base indentation of the method code
                first_line_indent = 0
                for line in method_lines:
                    if line.strip():  # Find first non-empty line
                        first_line_indent = len(line) - len(line.lstrip())
                        break

                # Re-indent all lines relative to the base indentation
                indented_method = []
                for line in method_lines:
                    if line.strip():  # Non-empty line
                        # Remove original indentation and add class method indentation
                        relative_indent = len(line) - len(line.lstrip()) - first_line_indent
                        new_line = ' ' * (method_indent + relative_indent) + line.lstrip()
                        indented_method.append(new_line)
                    else:
                        indented_method.append('')

                insertions.append((insert_line, '\n\n' + '\n'.join(indented_method)))

    # Sort insertions by line number (descending) to maintain line numbers
    insertions.sort(key=lambda x: x[0], reverse=True)

    # Apply insertions
    result_lines = lines[:]
    for insert_line, code_to_insert in insertions:
        result_lines.insert(insert_line, code_to_insert)

    return '\n'.join(result_lines)


def validate_merged_library(
    merged_code: str,
    base_lib_code: str,
    methods_by_class: Dict[str, list]
) -> tuple[bool, list[str]]:
    """Validate that merged library preserves base code and adds new methods.

    Args:
        merged_code: Final merged library code
        base_lib_code: Original base library code
        methods_by_class: Dictionary of new methods added

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check that code is not empty
    if not merged_code or len(merged_code) < len(base_lib_code):
        issues.append("Merged code is shorter than base library")
        return False, issues

    # Try to compile the code
    try:
        compile(merged_code, "<string>", "exec")
    except SyntaxError as e:
        issues.append(f"Syntax error in merged code: {e}")
        return False, issues

    # Parse both to check structure
    try:
        import ast
        base_tree = ast.parse(base_lib_code)
        merged_tree = ast.parse(merged_code)
    except SyntaxError as e:
        issues.append(f"Failed to parse code for validation: {e}")
        return False, issues

    # Extract class and method names from base library
    base_classes = {}
    for node in ast.walk(base_tree):
        if isinstance(node, ast.ClassDef):
            base_classes[node.name] = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    base_classes[node.name].add(item.name)

    # Extract from merged library
    merged_classes = {}
    for node in ast.walk(merged_tree):
        if isinstance(node, ast.ClassDef):
            merged_classes[node.name] = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    merged_classes[node.name].add(item.name)

    # Check that all base classes exist in merged
    for class_name in base_classes:
        if class_name not in merged_classes:
            issues.append(f"Base class '{class_name}' missing from merged code")

    # Check that all base methods still exist
    for class_name, methods in base_classes.items():
        if class_name not in merged_classes:
            continue
        for method in methods:
            if method not in merged_classes[class_name]:
                issues.append(f"Base method '{class_name}.{method}' missing from merged code")

    # Check that new methods were added
    new_methods_found = 0
    for class_name, method_codes in methods_by_class.items():
        if class_name not in merged_classes:
            issues.append(f"Class '{class_name}' not found in merged code")
            continue

        # Extract method names from method code
        for method_code in method_codes:
            import re
            match = re.search(r'def\s+(\w+)\s*\(', method_code)
            if match:
                method_name = match.group(1)
                if method_name in merged_classes[class_name]:
                    new_methods_found += 1
                else:
                    issues.append(f"New method '{class_name}.{method_name}' not found in merged code")

    if new_methods_found == 0:
        issues.append("No new methods were successfully added")

    if issues:
        return False, issues

    print(f"✓ Validation passed: {new_methods_found} new methods added")
    return True, []


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage3(cfg: argparse.Namespace, output_dir: Path, stage2_result: Dict) -> Dict:
    """Run Stage 3: Implementation Generation.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage2_result: Results from Stage 2

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 3: IMPLEMENTATION GENERATION")
    print(f"{'='*70}\n")

    # Load Stage 2 API proposal
    stage2_api_file = Path(stage2_result["outputs"]["final_api"])
    print(f"Loading refined API proposal from {stage2_api_file}...")
    api_proposal = load_api_proposal(stage2_api_file)
    print(f"✓ Loaded API proposal\n")

    # Load base library code
    print(f"Loading base library code from {cfg.base_lib}...")
    base_lib_code = load_base_library(cfg.base_lib)
    print(f"✓ Loaded {len(base_lib_code)} characters of code\n")

    # Load base library docs
    print(f"Loading base library docs from {cfg.base_lib_docs}...")
    base_lib_docs = Path(cfg.base_lib_docs).read_text(encoding="utf-8")
    print(f"✓ Loaded base library docs\n")

    # Step 1: Generate new methods only
    print("Step 1: Generating new methods...")
    print("-" * 70)

    new_methods_response = generate_new_methods(
        api_proposal=api_proposal,
        base_lib_code=base_lib_code,
        base_lib_docs=base_lib_docs,
        domain_description=cfg.domain_description,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens * 3  # Give more tokens for code generation
    )

    # Save raw response
    raw_file = output_dir / "new_methods_raw.txt"
    raw_file.write_text(new_methods_response, encoding='utf-8')
    print(f"✓ Saved raw response to {raw_file}\n")

    # Extract code from response (handle markdown blocks)
    methods_code = extract_code_from_response(new_methods_response)

    # Save extracted methods
    methods_file = output_dir / "new_methods.py"
    methods_file.write_text(methods_code, encoding='utf-8')
    print(f"✓ Saved extracted methods to {methods_file}\n")

    # Step 2: Parse methods by class
    print("Step 2: Parsing methods by class...")
    print("-" * 70)

    try:
        methods_by_class = parse_methods_by_class(methods_code)
        print(f"✓ Parsed {sum(len(m) for m in methods_by_class.values())} methods across {len(methods_by_class)} classes")
        for class_name, methods in methods_by_class.items():
            print(f"  - {class_name}: {len(methods)} methods")
        print()
    except Exception as e:
        print(f"✗ Failed to parse methods: {e}\n")
        methods_by_class = {}

    # Save parsed methods
    parsed_file = output_dir / "methods_by_class.json"
    save_json({cls: [f"method_{i}" for i in range(len(methods))]
               for cls, methods in methods_by_class.items()}, parsed_file)

    # Step 3: Merge methods into base library
    print("Step 3: Merging methods into base library...")
    print("-" * 70)

    try:
        merged_code = merge_methods_into_library(base_lib_code, methods_by_class)
        print(f"✓ Merged successfully")
        print(f"  Base library: {len(base_lib_code)} chars")
        print(f"  Merged library: {len(merged_code)} chars")
        print(f"  Added: {len(merged_code) - len(base_lib_code)} chars\n")
    except Exception as e:
        print(f"✗ Failed to merge methods: {e}\n")
        merged_code = base_lib_code

    # Save merged library
    impl_file = output_dir / "generated_library.py"
    impl_file.write_text(merged_code, encoding='utf-8')
    print(f"✓ Saved merged library to {impl_file}\n")

    # Step 4: Validate merged library
    print("Step 4: Validating merged library...")
    print("-" * 70)

    is_valid, issues = validate_merged_library(merged_code, base_lib_code, methods_by_class)

    if not is_valid:
        print("✗ Validation failed with issues:")
        for issue in issues:
            print(f"  - {issue}")
    print()

    # Create summary
    result = {
        "stage": 3,
        "timestamp": timestamp(),
        "config": {
            "base_lib": cfg.base_lib,
            "base_lib_docs": cfg.base_lib_docs,
            "model": cfg.model,
        },
        "outputs": {
            "new_methods_raw": str(raw_file),
            "new_methods": str(methods_file),
            "methods_by_class": str(parsed_file),
            "implementation": str(impl_file),
            "validation_passed": is_valid,
            "validation_issues": issues if not is_valid else [],
            "base_lib_size": len(base_lib_code),
            "merged_lib_size": len(merged_code),
            "classes_extended": list(methods_by_class.keys()),
            "num_methods_added": sum(len(m) for m in methods_by_class.values()),
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage3_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 3 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Implementation: {impl_file}")
    print(f"Methods added: {sum(len(m) for m in methods_by_class.values())}")
    print(f"Classes extended: {', '.join(methods_by_class.keys())}")
    print(f"Validation: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if not is_valid and issues:
        print(f"Issues: {len(issues)}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args
    import sys

    cfg = parse_args()

    # Load Stage 2 results
    stage2_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage2"
    stage2_summary = stage2_dir / "stage2_summary.json"

    if not stage2_summary.exists():
        print(f"Error: Stage 2 results not found at {stage2_summary}")
        print("Please run Stage 2 first!")
        sys.exit(1)

    with open(stage2_summary) as f:
        stage2_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage3"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage3(cfg, output_dir, stage2_result)
