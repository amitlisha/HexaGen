import inspect
import sys
from pathlib import Path

# Add project root and larc directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "larc"))

try:
    import larc.dsl as dsl
except ImportError as e:
    print(f"Error importing larc.dsl: {e}")
    sys.path.append(str(project_root / "larc"))
    try:
        import dsl
    except ImportError as e2:
        print(f"Error importing dsl directly: {e2}")
        sys.exit(1)

def generate_api_spec():
    functions = []
    for name, obj in inspect.getmembers(dsl):
        if inspect.isfunction(obj) and obj.__module__ == dsl.__name__:
            functions.append(obj)
        elif inspect.isfunction(obj) and obj.__module__ == 'dsl': # If imported as 'dsl'
             functions.append(obj)

    # Sort by line number (definition order)
    functions.sort(key=lambda x: x.__code__.co_firstlineno)

    output = []
    output.append("# LARC DSL API Specification")
    output.append("# Use these functions to solve the task.")
    output.append("")

    for func in functions:
        sig = inspect.signature(func)
        doc = inspect.getdoc(func)
        
        # Clean up type hints in signature if they are too verbose (optional, but good for LLM)
        # For now, we'll keep the full signature including type hints
        
        output.append(f"def {func.__name__}{sig}:")
        if doc:
            output.append(f'    """ {doc} """')
        output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    spec = generate_api_spec()
    output_path = project_root / "data" / "larc_api_spec.txt"
    output_path.write_text(spec)
    print(f"LARC API spec written to {output_path}")
