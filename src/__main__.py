import argparse
import sys
import os

from src.parsing import (
    get_functions_definition,
    get_prompts,
    FunctionsDefinitionError,
    PromptError
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call Me Maybe")
    parser.add_argument("--input", type=str, default="data/input")
    parser.add_argument("--output", type=str,
                        default="data/output/function_calling_results.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("Hello from 42-call-me-maybe!")
    print("Starting Program...")
    print(f"Output Path: {args.output}")
    try:
        functions_path = os.path.join(args.input, "function_definitions.json")
        prompts_path = os.path.join(args.input, "function_calling_tests.json")

        print(f"Validating files in: {args.input}")
        functions = get_functions_definition(functions_path)
        prompts = get_prompts(prompts_path)
        print(f"Loaded {len(functions)} functions & {len(prompts)} prompts.")
    except (FunctionsDefinitionError, PromptError) as e:
        print(f"Critic error on input files:\n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
