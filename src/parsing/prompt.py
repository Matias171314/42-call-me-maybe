import json
from typing import List
from pydantic import BaseModel, ValidationError


class PromptError(Exception):
    """Custom exception for errors during prompts parsing."""
    pass


class Prompt(BaseModel):
    """
    Model representing a prompt entry.

    Attributes:
        prompt (str): The natural language query or instruction.
    """
    prompt: str


def get_prompts(file_path: str) -> List[Prompt]:
    """
    Reads and validates prompt instructions from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing prompts.

    Returns:
        List[Prompt]: List of validated Prompt.

    Raises:
        PromptError: If the file is not found, contains invalid JSON,
            lacks read permissions, is not a list, or schema fails.
    """
    try:
        with open(file_path, 'r') as f:
            data_prompts = json.load(f)
    except FileNotFoundError:
        raise PromptError(
            f"File Not Found: The prompts file at '{file_path}' "
            "does not exist."
            )
    except json.JSONDecodeError as e:
        raise PromptError(
            f"JSON Decode Error: The file '{file_path}' contains "
            f"invalid JSON data. Details: {e}"
            )
    except PermissionError:
        raise PromptError(
            "Permission Denied: Lacking read permissions for "
            f"the file '{file_path}'."
            )
    except Exception as e:
        raise PromptError(
            f"Unexpected Error: An issue occurred while reading "
            f"'{file_path}'. Details: {e}"
            )

    if not isinstance(data_prompts, list):
        raise PromptError(
            "Invalid Format: The top-level JSON structure must be a list "
            "of prompts."
            )

    validated_prompts: List[Prompt] = []

    for item in data_prompts:
        try:
            valid_prompt = Prompt(prompt=item["prompt"])
            validated_prompts.append(valid_prompt)
        except ValidationError as e:
            fail_prompt = item.get("prompt")
            raise PromptError(
                f"Validation Error: The prompt '{fail_prompt}' does not "
                f"match the expected schema.\nDetails: {e}"
                )
    return validated_prompts
