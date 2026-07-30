import sys
import json
import argparse
from pathlib import Path

from src import (
    FunctionDefinitionError,
    Model,
    PromptError,
    PromptProcessor,
    get_function_definitions,
    get_prompts,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Call Me Maybe")
    parser.add_argument(
        "--input",
        type=str,
        default="data/input",
        help="Directory containing the input JSON files."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output/function_calling_results.json",
        help="Path to save the generated JSON results."
    )
    return parser.parse_args()


def main() -> None:
    """Main execution flow for the prompt processor."""
    args: argparse.Namespace = parse_args()

    print("[INFO] Hello from 42-call-me-maybe!")
    print("[INFO] Starting Program...")

    input_dir = Path(args.input)
    output_file = Path(args.output)

    print(f"[INFO] Validating files in: {input_dir}")
    print(f"[INFO] Output Path: {output_file}")

    functions_path: str = str(input_dir / "functions_definition.json")
    prompts_path: str = str(input_dir / "function_calling_tests.json")

    try:
        functions = get_function_definitions(functions_path)
        prompts = get_prompts(prompts_path)
        print(
            f"[SUCCESS] Loaded {len(functions)} functions & "
            f"{len(prompts)} prompts."
        )
    except (FunctionDefinitionError, PromptError) as e:
        print(
            f"\033[0;31m[CRITICAL] Error on input files:\n{e}\033[0m",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        print("[INFO] Loading LLM Engine...")
        llm = Model()
    except Exception as e:
        print(
            f"\033[0;31m[CRITICAL] Error loading model. Details: {e}\033[0m",
            file=sys.stderr
        )
        sys.exit(1)

    print("[INFO] Processing prompts. This might take a while...")
    processor = PromptProcessor(prompts, functions, llm)
    output = processor.process()

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"[SUCCESS] Results saved successfully in: {output_file}")
        sys.exit(0)
    except OSError as e:
        print(
            f"\033[0;31m[ERROR] Could not write to output. "
            f"Details: {e}\033[0m",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
