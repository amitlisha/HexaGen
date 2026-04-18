"""Stage 2: Implementation Generation from API proposal.

This stage takes the API proposal from Stage 1 and generates
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
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List


def load_api_proposal(api_file: Path) -> str:
    """Load API proposal from Stage 1."""
    if not api_file.exists():
        raise FileNotFoundError(f"API proposal not found: {api_file}")
    return api_file.read_text(encoding="utf-8")


def load_base_library(base_lib_path: str) -> str:
    """Load the base library code."""
    lib_file = Path(base_lib_path)
    if not lib_file.exists():
        raise FileNotFoundError(f"Base library not found: {base_lib_path}")
    return lib_file.read_text(encoding="utf-8")


def parse_classes_from_proposal(api_proposal: str) -> Dict[str, str]:
    """Parse API proposal to extract per-class sections.

    Looks for 'Class: ClassName' lines and groups all content (including
    indented Method: entries) under each class until the next Class: line
    or section separator.

    Args:
        api_proposal: Full API proposal text (markdown format)

    Returns:
        Dictionary mapping class names to their proposal section text
    """
    classes: Dict[str, List[str]] = {}  # class_name -> list of section texts
    current_class = None
    current_lines: List[str] = []

    def _flush():
        nonlocal current_class, current_lines
        if current_class and current_lines:
            section = '\n'.join(current_lines)
            if current_class not in classes:
                classes[current_class] = []
            classes[current_class].append(section)
        current_class = None
        current_lines = []

    for line in api_proposal.split('\n'):
        class_match = re.match(r'^(?:```text\s*)?Class:\s*(\w+)', line.strip())
        if class_match:
            _flush()
            current_class = class_match.group(1)
            current_lines = [line]
        elif current_class is not None:
            # Batch/section separators end the current class section
            if re.match(r'^#\s+Batch\s+\d+', line.strip()):
                _flush()
            else:
                current_lines.append(line)

    _flush()

    # Merge multiple sections per class into a single text
    return {name: '\n\n'.join(sections) for name, sections in classes.items()}


def generate_methods_for_class(
    class_name: str,
    class_proposal: str,
    base_lib_code: str,
    base_lib_docs: str,
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
    is_new_class: bool = False,
    request_timeout: int = 300,
) -> str:
    """Generate new methods for a single class from its API proposal section.

    Args:
        class_name: Name of the class to generate methods for
        class_proposal: API proposal section for this class
        base_lib_code: Current base library code
        base_lib_docs: Base library documentation
        domain_description: Brief description of domain
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response
        thinking_effort: OpenAI reasoning effort
        thinking_level: Gemini thinking level
        is_new_class: If True, generate full class definition instead of bare methods
        request_timeout: Timeout in seconds for the API request

    Returns:
        Raw LLM response text containing method implementations
    """
    from gpt.llm_wrapper import call_llm

    domain_context = f" for {domain_description}" if domain_description else ""

    system_prompt = "You are an expert Python developer implementing methods from an API specification."

    prompt = _build_class_generation_prompt(
        class_name, class_proposal, base_lib_code, base_lib_docs, domain_context,
        is_new_class=is_new_class,
    )

    print(f"  Generating methods for class {class_name}...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
        request_timeout=request_timeout,
    )

    return response["text"]


def generate_new_methods(
    api_proposal: str,
    base_lib_code: str,
    base_lib_docs: str,
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
) -> str:
    """Generate ONLY new methods from API proposal (not full library).

    Args:
        api_proposal: API proposal from Stage 1
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

    Examples:
        >>> obj = ClassName(...)
        >>> obj.method_name(arg1, arg2)
        expected_result
    \"\"\"
    # Implementation
    pass
```

REQUIREMENTS:
- Complete implementations with docstrings
- Each method MUST include at least one doctest example in its docstring (in the Examples section)
- Doctest examples must be correct and runnable — they will be executed to validate the implementation
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
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
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


def _remove_broken_methods(
    base_lib_code: str,
    methods_by_class: Dict[str, list],
    new_class_definitions: Dict[str, str] | None = None,
) -> str:
    """Re-merge methods one-by-one, skipping any that cause SyntaxError.

    Called as a fallback when the full merge produces invalid Python.
    """
    import re

    if not base_lib_code.startswith("from __future__"):
        base_lib_code = "from __future__ import annotations\n\n" + base_lib_code

    # Start from clean base
    good_methods: Dict[str, list] = {cls: [] for cls in methods_by_class}
    removed: list[str] = []

    for class_name, methods in methods_by_class.items():
        for method_code in methods:
            # Extract method name for reporting
            name_match = re.search(r'def\s+(\w+)', method_code)
            method_name = name_match.group(1) if name_match else "<unknown>"

            # Try adding this one method
            trial = dict(good_methods)
            trial[class_name] = good_methods[class_name] + [method_code]

            trial_code = _merge_without_validation(
                base_lib_code, trial, None,
            )
            try:
                compile(trial_code, "<trial>", "exec")
                good_methods[class_name] = trial[class_name]
            except SyntaxError as e:
                removed.append(f"{class_name}.{method_name}")
                print(f"  ⚠ Removing {class_name}.{method_name} (syntax error: {e})")

    # Also validate new class definitions
    good_new_classes: Dict[str, str] | None = None
    if new_class_definitions:
        good_new_classes = {}
        for class_name, class_code in new_class_definitions.items():
            trial_code = _merge_without_validation(
                base_lib_code, good_methods, {**good_new_classes, class_name: class_code},
            )
            try:
                compile(trial_code, "<trial>", "exec")
                good_new_classes[class_name] = class_code
            except SyntaxError as e:
                removed.append(class_name)
                print(f"  ⚠ Removing new class {class_name} (syntax error: {e})")

    if removed:
        print(f"  Removed {len(removed)} broken method(s): {', '.join(removed)}")
        # Update methods_by_class in-place so callers see the cleaned version
        for cls in methods_by_class:
            methods_by_class[cls] = good_methods[cls]
        if new_class_definitions is not None:
            new_class_definitions.clear()
            if good_new_classes:
                new_class_definitions.update(good_new_classes)

    return _merge_without_validation(base_lib_code, good_methods, good_new_classes)


def _merge_without_validation(
    base_lib_code: str,
    methods_by_class: Dict[str, list],
    new_class_definitions: Dict[str, str] | None = None,
) -> str:
    """Core merge logic without syntax validation (used by _remove_broken_methods)."""
    import ast

    tree = ast.parse(base_lib_code)

    class_nodes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_nodes[node.name] = node

    lines = base_lib_code.split('\n')
    insertions = []

    for class_name, methods in methods_by_class.items():
        if class_name not in class_nodes:
            continue

        class_node = class_nodes[class_name]

        if class_node.body:
            last_stmt = class_node.body[-1]
            insert_line = last_stmt.end_lineno

            class_line = lines[class_node.lineno - 1]
            class_indent = len(class_line) - len(class_line.lstrip())
            method_indent = class_indent + 4

            for method_code in methods:
                method_lines = method_code.split('\n')

                first_line_indent = 0
                for line in method_lines:
                    if line.strip():
                        first_line_indent = len(line) - len(line.lstrip())
                        break

                indented_method = []
                for line in method_lines:
                    if line.strip():
                        relative_indent = len(line) - len(line.lstrip()) - first_line_indent
                        new_line = ' ' * (method_indent + relative_indent) + line.lstrip()
                        indented_method.append(new_line)
                    else:
                        indented_method.append('')

                insertions.append((insert_line, '\n\n' + '\n'.join(indented_method)))

    insertions.sort(key=lambda x: x[0], reverse=True)

    result_lines = lines[:]
    for insert_line, code_to_insert in insertions:
        result_lines.insert(insert_line, code_to_insert)

    if new_class_definitions:
        for class_name, class_code in new_class_definitions.items():
            result_lines.append(f'\n\n{class_code}')

    return '\n'.join(result_lines)


def merge_methods_into_library(
    base_lib_code: str,
    methods_by_class: Dict[str, list],
    new_class_definitions: Dict[str, str] | None = None,
) -> str:
    """Merge new methods into base library code using AST manipulation.

    Args:
        base_lib_code: Original base library code
        methods_by_class: Dictionary of class names to method code lists
            (for classes that already exist in the base library)
        new_class_definitions: Dictionary of class names to full class
            definition code (for entirely new classes)

    Returns:
        Updated library code with new methods added
    """
    import ast
    import textwrap

    # Prepend future annotations to avoid forward reference errors
    # (e.g. Game methods referencing Tile before Tile is defined)
    if not base_lib_code.startswith("from __future__"):
        base_lib_code = "from __future__ import annotations\n\n" + base_lib_code

    # Parse the base library (after prepending, so AST line numbers match)
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
            print(f"  ⚠ Warning: Class '{class_name}' not found in base library, skipping")
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

    # Append new class definitions at the end of the file
    if new_class_definitions:
        for class_name, class_code in new_class_definitions.items():
            print(f"  Appending new class '{class_name}'")
            result_lines.append(f'\n\n{class_code}')

    merged = '\n'.join(result_lines)

    # Validate syntax — remove methods that introduce errors
    try:
        compile(merged, "<merged>", "exec")
    except SyntaxError:
        merged = _remove_broken_methods(
            base_lib_code, methods_by_class, new_class_definitions,
        )

    return merged


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


def _make_lenient_checker():
    """Build a doctest OutputChecker resilient to common LLM doctest mistakes.

    Handles:
    - ``# doctest: +ELLIPSIS`` placed on expected-output lines (strips it)
    - Extra output lines from un-suppressed return values (e.g. bare
      ``.draw()`` calls that return ``self``)
    """
    import doctest
    import re

    _DIRECTIVE_RE = re.compile(r'\s*#\s*doctest\s*:.*$', re.MULTILINE)

    class _LenientChecker(doctest.OutputChecker):
        def check_output(self, want: str, got: str, optionflags: int) -> bool:
            # Always enable ELLIPSIS
            optionflags |= doctest.ELLIPSIS

            # Strip ``# doctest:`` directives from expected output
            want_clean = _DIRECTIVE_RE.sub('', want).rstrip()
            if want_clean != want.rstrip():
                # Re-add trailing newline so the base checker is happy
                want_clean += '\n'
                if super().check_output(want_clean, got, optionflags):
                    return True

            # Standard check
            if super().check_output(want, got, optionflags):
                return True

            # Tolerate extra leading lines in got (e.g. un-suppressed
            # return values from .draw()) — check whether the *expected*
            # output appears as a suffix of *got*.
            if want.strip():
                got_lines = got.rstrip('\n').split('\n')
                want_lines = want.rstrip('\n').split('\n')
                if len(got_lines) > len(want_lines):
                    got_suffix = '\n'.join(got_lines[-len(want_lines):]) + '\n'
                    if super().check_output(want, got_suffix, optionflags):
                        return True

            return False

    return _LenientChecker()


def run_doctests_on_merged(
    merged_code: str, per_test_timeout: int = 30,
) -> tuple[int, int, list[str]]:
    """Run doctests on the entire merged library.

    Each individual doctest is run in a daemon thread with a timeout to
    prevent LLM-generated infinite loops from hanging the process.

    Args:
        merged_code: Complete merged library code
        per_test_timeout: Max seconds to allow each doctest to run

    Returns:
        Tuple of (num_passed, num_failed, failure_details)
    """
    import doctest
    import io
    import threading
    import types

    import sys

    # Create a temporary module whose name matches what the LLM expects
    # in its doctest output (e.g. <hexagen.Game object at ...>).
    # Register it in sys.modules so ``from hexagen import ...`` inside
    # doctests resolves to the generated library, not the real package.
    mod = types.ModuleType("hexagen")
    old_hexagen = sys.modules.get("hexagen")
    sys.modules["hexagen"] = mod
    try:
        exec(compile(merged_code, "<generated_library>", "exec"), mod.__dict__)
    except Exception as e:
        # Restore original module on failure
        if old_hexagen is not None:
            sys.modules["hexagen"] = old_hexagen
        else:
            sys.modules.pop("hexagen", None)
        return 0, 0, [f"Library exec failed: {e}"]

    # Auto-patch classes that define __str__ but not __repr__, so doctests
    # that print return values get the human-readable form instead of
    # <module.ClassName object at 0x...>.
    for _name, obj in list(mod.__dict__.items()):
        if isinstance(obj, type) and "__str__" in obj.__dict__ and "__repr__" not in obj.__dict__:
            obj.__repr__ = obj.__str__

    checker = _make_lenient_checker()
    flags = doctest.ELLIPSIS

    # Run all doctests with lenient checker
    finder = doctest.DocTestFinder()
    all_tests = finder.find(mod, "hexagen", globs=mod.__dict__)
    total_passed = 0
    total_failed = 0
    failure_details = []

    try:
        for test in all_tests:
            if not test.examples:
                continue
            out = io.StringIO()
            runner = doctest.DocTestRunner(
                checker=checker, verbose=False, optionflags=flags,
            )

            # Run each test in a daemon thread with a timeout to avoid
            # hanging on LLM-generated infinite loops.
            result_holder = [None, None]  # [summary, exception]

            def _run_test(r=runner, t=test, o=out, rh=result_holder):
                try:
                    r.run(t, out=o.write)
                    # Suppress summarize() stdout by redirecting it
                    old_out = sys.stdout
                    sys.stdout = io.StringIO()
                    try:
                        rh[0] = r.summarize(verbose=False)
                    finally:
                        sys.stdout = old_out
                except Exception as exc:
                    rh[1] = exc

            t = threading.Thread(target=_run_test, daemon=True)
            t.start()
            t.join(timeout=per_test_timeout)

            if t.is_alive():
                total_failed += len(test.examples)
                failure_details.append(
                    f"{test.name}: TIMED OUT after {per_test_timeout}s "
                    f"(possible infinite loop)"
                )
            elif result_holder[1] is not None:
                total_failed += len(test.examples)
                failure_details.append(
                    f"{test.name}: ERROR: {result_holder[1]}"
                )
            else:
                summary = result_holder[0]
                total_passed += summary.attempted - summary.failed
                total_failed += summary.failed
                if summary.failed > 0:
                    failure_details.append(f"{test.name}:\n{out.getvalue()}")
    finally:
        # Restore original hexagen module
        if old_hexagen is not None:
            sys.modules["hexagen"] = old_hexagen
        else:
            sys.modules.pop("hexagen", None)

    return total_passed, total_failed, failure_details


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def _build_class_generation_prompt(
    class_name: str,
    class_proposal: str,
    base_lib_code: str,
    base_lib_docs: str,
    domain_context: str,
    is_new_class: bool = False,
) -> str:
    """Build the prompt for generating methods for a single class.

    Used by both the sync generate_methods_for_class() and the Batch API path.

    When is_new_class is True, the LLM is asked to produce a complete class
    definition instead of bare methods with # CLASS: markers.
    """
    if is_new_class:
        return f"""Implement the class `{class_name}` from this API proposal{domain_context}.

API PROPOSAL FOR {class_name}:
{class_proposal}

BASE LIBRARY (reference — the new class will be appended after this code):
```python
{base_lib_code}
```

BASE LIBRARY DOCUMENTATION:
{base_lib_docs}

OUTPUT FORMAT — provide the FULL class definition:
```python
class {class_name}:
    \"\"\"Brief class description.\"\"\"

    def __init__(self, ...):
        ...

    def method_name(self, param1: type1, param2: type2) -> ReturnType:
        \"\"\"Brief description.

        Examples:
            >>> obj = {class_name}(...)
            >>> obj.method_name(arg1, arg2)
            expected_result
        \"\"\"
        ...
```

REQUIREMENTS:
- Provide the complete class with `__init__` and all proposed methods
- Each method MUST include at least one doctest example that is correct and runnable
- Handle edge cases (None, empty, out-of-bounds)
- Raise meaningful exceptions (ValueError, TypeError, etc.) with descriptive error messages that explain what went wrong and how to fix it — this library will be used by an LLM, so clear error messages are critical for self-correction
- Match base library coding style
- The class can reference base library classes (Game, Tile) and constants (WIDTH, HEIGHT, COLORS, DIRECTIONS)

DO NOT:
- Include existing base library code
- Add explanations outside code

Provide ONLY the `{class_name}` class definition."""

    return f"""Implement the NEW methods for class `{class_name}` from this API proposal{domain_context}.

API PROPOSAL FOR {class_name}:
{class_proposal}

BASE LIBRARY (reference):
```python
{base_lib_code}
```

BASE LIBRARY DOCUMENTATION:
{base_lib_docs}

OUTPUT FORMAT - Use this exact structure:
```python
# CLASS: {class_name}
def method_name(self, param1: type1, param2: type2) -> ReturnType:
    \"\"\"Brief description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description

    Examples:
        >>> obj = {class_name}(...)
        >>> obj.method_name(arg1, arg2)
        expected_result
    \"\"\"
    # Implementation
    pass
```

REQUIREMENTS:
- Complete implementations with docstrings
- Each method MUST include at least one doctest example in its docstring (in the Examples section)
- Doctest examples must be correct and runnable — they will be executed to validate the implementation
- Handle edge cases (None, empty, out-of-bounds)
- Raise meaningful exceptions (ValueError, TypeError, etc.) with descriptive error messages that explain what went wrong and how to fix it — this library will be used by an LLM, so clear error messages are critical for self-correction
- Match base library coding style
- ALL methods must use `# CLASS: {class_name}` marker

DO NOT:
- Include existing base library code
- Include class definitions
- Add explanations outside code
- Include methods for other classes

Provide ONLY the new method implementations for {class_name}."""


def run_stage2(cfg: argparse.Namespace, output_dir: Path, stage2_result: Dict) -> Dict:
    """Run Stage 3: Implementation Generation.

    Supports three execution modes:
    - Sequential (workers <= 1, no --batch): one class at a time
    - ThreadPoolExecutor (workers > 1): parallel sync calls across classes
    - Batch API (--batch): submit all class requests as a batch job

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage2_result: Results from Stage 2

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 2: IMPLEMENTATION GENERATION")
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

    # Step 1: Parse API proposal into per-class sections
    print("Step 1: Parsing API proposal by class...")
    print("-" * 70)

    class_proposals = parse_classes_from_proposal(api_proposal)
    print(f"✓ Found {len(class_proposals)} classes: {', '.join(class_proposals.keys())}\n")

    # Detect which proposed classes already exist in the base library
    import ast as _ast
    _base_tree = _ast.parse(base_lib_code)
    _base_class_names = {
        node.name for node in _ast.walk(_base_tree) if isinstance(node, _ast.ClassDef)
    }
    new_classes = {name for name in class_proposals if name not in _base_class_names}
    if new_classes:
        print(f"  New classes (not in base library): {', '.join(sorted(new_classes))}")

    # Step 2: Generate methods per class (3 execution modes)
    print("Step 2: Generating methods per class...")
    print("-" * 70)

    # Each entry: (class_name, raw_response_text)
    class_responses: List[tuple[str, str]] = []

    if getattr(cfg, "batch", False) or getattr(cfg, "batch_resume", None):
        # --- Batch API mode ---
        print("Using LLM Batch API for per-class generation...")
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

        system_prompt = "You are an expert Python developer implementing methods from an API specification."
        is_gemini = _is_gemini_model(cfg.model)
        class_names = list(class_proposals.keys())

        if is_gemini:
            gemini_requests = []
            for class_name in class_names:
                domain_context = f" for {cfg.domain_description}" if cfg.domain_description else ""
                prompt = _build_class_generation_prompt(
                    class_name, class_proposals[class_name],
                    base_lib_code, base_lib_docs, domain_context,
                    is_new_class=class_name in new_classes,
                )
                request = build_gemini_batch_request(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    thinking_level=getattr(cfg, "thinking_level", None),
                )
                gemini_requests.append(request)

            if getattr(cfg, "batch_resume", None):
                print(f"Resuming Gemini batch: {cfg.batch_resume}")
                batch_job = poll_gemini_batch(
                    cfg.batch_resume,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )
            else:
                display_name = f"{cfg.experiment_name}-stage3-{cfg.model}"
                job_name = submit_gemini_batch(gemini_requests, cfg.model, display_name)
                print(f"Created Gemini batch: {job_name}")
                batch_job = poll_gemini_batch(
                    job_name,
                    getattr(cfg, "batch_poll_interval", 60),
                    getattr(cfg, "batch_timeout", 86400),
                )

            print(f"Parsing Gemini batch results...")
            batch_results = parse_gemini_batch_results(batch_job, gemini_requests)

            for i, class_name in enumerate(class_names):
                result = batch_results.get(i)
                if result and not result.get("error"):
                    class_responses.append((class_name, result["text"]))
                else:
                    err = (result or {}).get("error", "unknown error")
                    print(f"  ✗ {class_name}: {err}")

        else:
            # OpenAI Batch API
            jsonl_lines = []
            for i, class_name in enumerate(class_names):
                custom_id = f"class_{class_name}"
                domain_context = f" for {cfg.domain_description}" if cfg.domain_description else ""
                prompt = _build_class_generation_prompt(
                    class_name, class_proposals[class_name],
                    base_lib_code, base_lib_docs, domain_context,
                    is_new_class=class_name in new_classes,
                )
                messages = build_openai_messages(prompt=prompt, system_prompt=system_prompt)
                body = build_openai_request_body(
                    messages=messages,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    reasoning_effort=getattr(cfg, "thinking_effort", None),
                )
                jsonl_lines.append(json.dumps({
                    "custom_id": custom_id,
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
                custom_id = f"class_{class_name}"
                result = batch_results.get(custom_id)
                if result and not result.get("error"):
                    class_responses.append((class_name, result["text"]))
                else:
                    err = (result or {}).get("error", "unknown error")
                    print(f"  ✗ {class_name}: {err}")

    elif cfg.workers <= 1:
        # --- Sequential mode ---
        for class_name, class_proposal in class_proposals.items():
            response = generate_methods_for_class(
                class_name=class_name,
                class_proposal=class_proposal,
                base_lib_code=base_lib_code,
                base_lib_docs=base_lib_docs,
                domain_description=cfg.domain_description,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                thinking_effort=getattr(cfg, "thinking_effort", None),
                thinking_level=getattr(cfg, "thinking_level", None),
                is_new_class=class_name in new_classes,
                request_timeout=getattr(cfg, "request_timeout", 300),
            )
            class_responses.append((class_name, response))

    else:
        # --- ThreadPoolExecutor mode ---
        print(f"Using {cfg.workers} parallel workers...")
        with ThreadPoolExecutor(max_workers=cfg.workers) as executor:
            futures = {
                executor.submit(
                    generate_methods_for_class,
                    class_name=class_name,
                    class_proposal=class_proposal,
                    base_lib_code=base_lib_code,
                    base_lib_docs=base_lib_docs,
                    domain_description=cfg.domain_description,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    thinking_effort=getattr(cfg, "thinking_effort", None),
                    thinking_level=getattr(cfg, "thinking_level", None),
                    is_new_class=class_name in new_classes,
                    request_timeout=getattr(cfg, "request_timeout", 300),
                ): class_name
                for class_name, class_proposal in class_proposals.items()
            }

            for future in as_completed(futures):
                class_name = futures[future]
                try:
                    response = future.result()
                    class_responses.append((class_name, response))
                except Exception as exc:
                    print(f"  ✗ {class_name} failed: {exc}")

    print(f"\n✓ Generated responses for {len(class_responses)} classes\n")

    # Save per-class raw responses and combine into methods_by_class
    per_class_dir = output_dir / "per_class"
    per_class_dir.mkdir(parents=True, exist_ok=True)

    all_methods_code_parts = []
    methods_by_class: Dict[str, list] = {}
    new_class_definitions: Dict[str, str] = {}  # class_name -> full class code

    for class_name, raw_response in class_responses:
        # Save raw response
        raw_file = per_class_dir / f"{class_name}_raw.txt"
        raw_file.write_text(raw_response, encoding='utf-8')

        # Extract code
        methods_code = extract_code_from_response(raw_response)
        all_methods_code_parts.append(methods_code)

        if class_name in new_classes:
            # New class: store the full class definition as-is
            new_class_definitions[class_name] = methods_code
            print(f"  {class_name}: new class definition extracted")
        else:
            # Existing class: parse individual methods
            try:
                class_methods = parse_methods_by_class(methods_code)
                for cls, methods in class_methods.items():
                    if cls not in methods_by_class:
                        methods_by_class[cls] = []
                    methods_by_class[cls].extend(methods)
                    print(f"  {cls}: {len(methods)} methods parsed")
            except Exception as e:
                print(f"  ✗ Failed to parse methods for {class_name}: {e}")

    # Save combined raw response and extracted methods
    combined_raw = "\n\n" + "=" * 70 + "\n\n".join(
        f"# CLASS: {cn}\n{resp}" for cn, resp in class_responses
    )
    raw_file = output_dir / "new_methods_raw.txt"
    raw_file.write_text(combined_raw, encoding='utf-8')

    combined_methods = "\n\n".join(all_methods_code_parts)
    methods_file = output_dir / "new_methods.py"
    methods_file.write_text(combined_methods, encoding='utf-8')

    print(f"\n✓ Total: {sum(len(m) for m in methods_by_class.values())} methods across {len(methods_by_class)} classes\n")

    # Save parsed methods
    parsed_file = output_dir / "methods_by_class.json"
    save_json({cls: [f"method_{i}" for i in range(len(methods))]
               for cls, methods in methods_by_class.items()}, parsed_file)

    # Step 3: Merge methods into base library
    print("Step 3: Merging methods into base library...")
    print("-" * 70)

    try:
        merged_code = merge_methods_into_library(
            base_lib_code, methods_by_class, new_class_definitions,
        )
        print(f"✓ Merged successfully")
        print(f"  Base library: {len(base_lib_code)} chars")
        print(f"  Merged library: {len(merged_code)} chars")
        print(f"  Added: {len(merged_code) - len(base_lib_code)} chars\n")
    except Exception as e:
        print(f"✗ Failed to merge methods: {e}\n")
        merged_code = base_lib_code

    # Step 4: Run doctests on merged library
    print("Step 4: Running doctests...")
    print("-" * 70)

    num_passed, num_failed, doctest_failures = run_doctests_on_merged(merged_code)
    doctest_total = num_passed + num_failed

    print(f"  Doctests: {num_passed}/{doctest_total} passed")
    if num_failed > 0:
        for detail in doctest_failures:
            name = detail.split(":")[0] if ":" in detail else detail
            print(f"    - {name}")
    elif doctest_total == 0 and doctest_failures:
        print(f"  ✗ Library failed to compile/exec:")
        for detail in doctest_failures:
            print(f"    - {detail}")
    elif doctest_total == 0:
        print(f"  ⚠ No doctests found")
    else:
        print(f"  ✓ All doctests passed")
    print()

    # Save merged library
    impl_file = output_dir / "generated_library.py"
    impl_file.write_text(merged_code, encoding='utf-8')
    print(f"✓ Saved merged library to {impl_file}\n")

    # Step 5: Validate merged library
    print("Step 5: Validating merged library...")
    print("-" * 70)

    is_valid, issues = validate_merged_library(merged_code, base_lib_code, methods_by_class)

    if not is_valid:
        print("✗ Validation failed with issues:")
        for issue in issues:
            print(f"  - {issue}")
    print()

    # Create summary
    all_classes = list(methods_by_class.keys()) + list(new_class_definitions.keys())
    total_methods = sum(len(m) for m in methods_by_class.values())

    result = {
        "stage": 2,
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
            "new_classes": list(new_class_definitions.keys()),
            "num_methods_added": total_methods,
            "doctest_total": doctest_total,
            "doctest_passed": num_passed,
            "doctest_failed": num_failed,
            "doctest_failure_details": doctest_failures,
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage2_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 2 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Implementation: {impl_file}")
    print(f"Methods added: {total_methods}")
    print(f"New classes: {', '.join(new_class_definitions.keys()) if new_class_definitions else 'none'}")
    print(f"Doctests: {num_passed}/{doctest_total} passed")
    print(f"Classes extended: {', '.join(methods_by_class.keys()) if methods_by_class else 'none'}")
    print(f"Validation: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    if not is_valid and issues:
        print(f"Issues: {len(issues)}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args
    import sys

    cfg = parse_args()

    # Load Stage 1 results
    stage1_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage1"
    stage1_summary = stage1_dir / "stage1_summary.json"

    if not stage1_summary.exists():
        print(f"Error: Stage 1 results not found at {stage1_summary}")
        print("Please run Stage 1 first!")
        sys.exit(1)

    with open(stage1_summary) as f:
        stage1_result = json.load(f)

    # Create stage1_result in the format expected by run_stage2
    stage1_input = {
        "stage": 1,
        "outputs": {"final_api": stage1_result["outputs"]["api_proposal"]},
    }

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage2"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage2(cfg, output_dir, stage1_input)
