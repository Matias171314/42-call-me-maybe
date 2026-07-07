import json
from typing import List
from pydantic import BaseModel, ValidationError


class PromptError(Exception):
    pass


class Prompt(BaseModel):
    call: str


def get_prompts(file_path: str) -> List[Prompt]:
    try:
        with open(file_path, 'r') as f:
            data_prompts = json.load(f)
    except FileNotFoundError:
        raise PromptError(f"Prompts file was not found at '{file_path}'.")
    except json.JSONDecodeError as e:
        raise PromptError(f"File '{file_path}' is not a valid JSON:\n{e}")
    except PermissionError:
        raise PromptError(f"No read permission for the file '{file_path}'.")
    except Exception as e:
        raise PromptError(f"Unexpected error reading the prompts file:\n{e}")

    if not isinstance(data_prompts, list):
        raise PromptError(
            "The prompts JSON file must contain a list of prompts."
            )

    validated_prompts: List[Prompt] = []

    for index, item in enumerate(data_prompts):
        try:
            valid_prompt = Prompt(call=item)
            validated_prompts.append(valid_prompt)
        except ValidationError as e:
            raise PromptError(f"Structure error in prompt #{index + 1}:\n{e}")
    return validated_prompts
