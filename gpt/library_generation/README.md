# Library Generation System

A multi-stage system for generating a Python library from training samples using LLMs.

## Overview

Instead of testing how well LLMs use an existing library (hexagen), this system uses training samples to **generate a new library from scratch**. The library starts from a minimal foundation and lets the LLM discover and implement higher-level abstractions.

## Philosophy

1. **Minimal Foundation**: Provide only the bare essentials (Game, Tile, Shape with basic draw operations)
2. **LLM-Driven Discovery**: Let the LLM analyze ALL training samples to discover needed abstractions
3. **Bottom-Up Growth**: Build complex operations on top of primitives
4. **Dataset-Agnostic**: No assumptions about categories or structure
5. **Full Coverage**: Analyze entire training set, not just samples

## Hierarchical Analysis Method

The key insight is **hierarchical summarization** - process all samples by repeatedly summarizing batches:

```
3,278 instructions
    ↓ split into batches of ~100
33 batch summaries ("what patterns in these 100 instructions?")
    ↓ group into batches of ~10
4 meta-summaries ("what patterns across these 10 summaries?")
    ↓ final synthesis
1 unified API proposal
```

This ensures:
- **Full coverage**: Every instruction analyzed at least once
- **Scalability**: Can handle any dataset size
- **Natural prioritization**: Frequent patterns bubble up automatically
- **Simplicity**: Easy to understand and implement

## Stage Pipeline

### Stage 0: Minimal Foundation Library
Extract bare minimum from hexagen:
- Game (context manager, board state, plotting)
- Tile (row, col, draw, properties)
- Shape (collection of tiles, draw)
- Internal coordinate system (_Vec, _Hexagon)
- Constants (WIDTH, HEIGHT, COLORS, DIRECTIONS)

**Output**: `minimal_lib/` with stripped-down implementation

### Stage 1: API Discovery
Hierarchically analyze all training instructions:

1. **Level 1**: Split instructions into batches (~100 each)
   - Each batch analyzed by LLM: "what patterns do you see?"
   - Output: 33 batch summaries

2. **Level 2**: Group batch summaries (~10 each)
   - Each group synthesized by LLM: "what's common across these?"
   - Output: 4 meta-summaries

3. **Level 3**: Final synthesis
   - LLM designs API from meta-summaries
   - Output: `api_proposal_v1.md`

**Output**: Initial API design based on ALL training data

### Stage 2: API Refinement
Iteratively improve the API:
- Test with different sample subsets
- Identify gaps, redundancies
- Refine design through multiple iterations
- Generate `api_proposal_v2.md`, `api_proposal_v3.md`, `api_proposal_final.md`

**Output**: Refined, validated API design

### Stage 3: Implementation Generation
Generate code for the designed API:
- LLM implements each class/method
- Builds on top of minimal foundation
- Generates modular library structure

**Output**: `generated_lib/` with full implementation

### Stage 4: DSL Documentation
Generate comprehensive API documentation:
- User message template (like `code_user_message.txt`)
- System prompt (like `code_system_prompt.txt`)
- Full API reference with examples

**Output**: `generated_dsl_docs.txt`, `generated_system_prompt.txt`

### Stage 5: Validation
Test the generated library:
- Run on validation set (train/dev/test)
- Measure correctness (F1, exact match)
- Measure usability (LOC, complexity)
- Identify failing patterns

**Output**: Validation report with metrics and failures

### Stage 6: Error-Driven Extension
Improve library based on failures:
- Analyze failure patterns
- Propose API extensions
- Re-implement and re-validate
- Iterate until convergence

**Output**: Extended library with improved coverage

## Usage

### Basic Usage

```bash
# Run full pipeline
python gpt/library_generation/orchestrator.py \
  --experiment-name my_experiment \
  --stage all \
  --train-set train \
  --validation-set dev \
  --model gpt-4o

# Run specific stage
python gpt/library_generation/orchestrator.py \
  --experiment-name my_experiment \
  --stage 1 \
  --train-set train \
  --model gpt-4o
```

### Configuration Options

```
--stage: Which stage to run (0-6 or "all")
--train-set: Training data for API discovery (train/dev/test/4-samples)
--validation-set: Data to validate on (train/dev/test/4-samples)
--batch-size: Instructions per batch for hierarchical analysis (default: 100)
--meta-batch-size: Summaries per meta-batch (default: 10)
--model: LLM model (default: gpt-4o)
--temperature: LLM temperature (default: 0.7)
--max-tokens: Max tokens per response (default: 2000)
--vision: Include board images in prompts
--refinement-iterations: Refinement rounds in stage 2 (default: 3)
--max-extension-cycles: Max cycles in stage 6 (default: 3)
--experiment-name: Name for this experiment (required)
--output-dir: Base output directory (default: generated_libs)
--workers: Parallel workers for batch processing (default: 1)
--seed: Random seed (default: 42)
```

### Examples

```bash
# Quick test with 4-samples dataset
python gpt/library_generation/orchestrator.py \
  --experiment-name test_run \
  --stage 1 \
  --train-set 4-samples \
  --model gpt-4o \
  --batch-size 2

# Full experiment with parallel processing
python gpt/library_generation/orchestrator.py \
  --experiment-name full_experiment \
  --stage all \
  --train-set train \
  --validation-set dev \
  --model gpt-4o \
  --workers 4 \
  --batch-size 100

# Just Stage 1 with vision
python gpt/library_generation/orchestrator.py \
  --experiment-name vision_test \
  --stage 1 \
  --train-set train \
  --vision \
  --model gpt-4o
```

## Output Structure

```
generated_libs/
└── my_experiment/
    ├── stage0_minimal/
    │   └── minimal_lib/
    │       ├── __init__.py
    │       ├── game.py
    │       ├── tile.py
    │       ├── shape.py
    │       ├── primitives.py
    │       └── constants.py
    ├── stage1/
    │   ├── batch_001_summary.txt
    │   ├── batch_002_summary.txt
    │   ├── ...
    │   ├── meta_001_summary.txt
    │   ├── meta_002_summary.txt
    │   ├── api_proposal_v1.md
    │   └── stage1_summary.json
    ├── stage2/
    │   ├── api_proposal_v2.md
    │   ├── api_proposal_v3.md
    │   ├── api_proposal_final.md
    │   └── stage2_summary.json
    ├── stage3/
    │   ├── generated_lib/
    │   │   ├── __init__.py
    │   │   ├── shapes.py
    │   │   ├── operations.py
    │   │   └── queries.py
    │   └── stage3_summary.json
    ├── stage4/
    │   ├── generated_dsl_docs.txt
    │   ├── generated_system_prompt.txt
    │   └── stage4_summary.json
    ├── stage5/
    │   ├── validation_report.json
    │   ├── usability_metrics.json
    │   ├── failed_samples/
    │   └── stage5_summary.json
    └── stage6/
        ├── extended_lib/
        ├── extension_report.json
        └── stage6_summary.json
```

## Key Design Decisions

### Why Hierarchical Summarization?

1. **Full Coverage**: Every instruction is analyzed (vs. sampling which might miss patterns)
2. **Scalable**: Works with any dataset size (just add more levels)
3. **Natural Prioritization**: Patterns appearing in many batches automatically emphasized
4. **Dataset-Agnostic**: No assumptions about categories or structure
5. **Simple**: Easy to understand and debug

### Why Minimal Foundation?

1. **Solid Base**: LLM doesn't reinvent coordinate math
2. **True Creativity**: LLM designs abstractions independently
3. **Practical Constraints**: Must work with real hexagonal coordinates
4. **Fair Comparison**: Same foundation for all experiments

### Batch Size Selection

- **Batch size (100)**:
  - Small enough for LLM to read all instructions
  - Large enough to see patterns
  - Balances detail vs. coverage

- **Meta-batch size (10)**:
  - Manageable number of summaries to synthesize
  - Allows LLM to identify cross-cutting patterns
  - Prevents information overload

## Cost Estimation

For the full training set (3,278 instructions):

| Stage | LLM Calls | Est. Input Tokens | Est. Output Tokens | Est. Cost |
|-------|-----------|-------------------|-------------------|-----------|
| Stage 1 | ~33 batches + 4 meta + 1 final | ~1.5M | ~300K | ~$6.75 |
| Stage 2 | ~3 iterations × ~5 calls | ~100K | ~20K | ~$0.45 |
| Stage 3 | ~20 methods | ~200K | ~100K | ~$1.50 |
| Stage 4 | ~2 docs | ~50K | ~20K | ~$0.33 |
| Stage 5 | ~100 validations | ~500K | ~200K | ~$3.25 |
| Stage 6 | ~3 cycles × ~10 calls | ~150K | ~50K | ~$0.88 |
| **Total** | | | | **~$13.16** |

*Estimates based on GPT-4o pricing (~$2.50/1M input, ~$10/1M output tokens)*

With parallel processing (`--workers 4`), total time: ~30-45 minutes

## Next Steps

1. **Implement Stage 0**: Extract minimal foundation from hexagen
2. **Test Stage 1**: Run on 4-samples dataset first
3. **Implement Stages 2-6**: Complete the pipeline
4. **Evaluate**: Compare generated library vs. hexagen baseline
5. **Iterate**: Refine based on results

## Contributing

When adding new stages:
1. Create `stageN_name.py` with `run_stageN(cfg, output_dir, prev_result)` function
2. Update `orchestrator.py` to call the new stage
3. Update this README with stage description
4. Add tests in `tests/`
