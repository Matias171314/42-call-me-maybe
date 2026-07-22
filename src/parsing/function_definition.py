import json
from typing import List, Dict
from pydantic import BaseModel, ValidationError


class FunctionDefinitionError(Exception):
    """Custom exception for errors during function definitions parsing."""
    pass


class ParameterInfo(BaseModel):
    """
    Model representing the type information of a parameter or return value.

    Attributes:
        type (str): The expected data type (e.g., 'string', 'number').
    """
    type: str


class FunctionDefinition(BaseModel):
    """
    Model representing the complete definition of a function.

    Attributes:
        name (str): The name of the function.
        description (str): A brief description of what the function does.
        parameters (Dict[str, ParameterInfo]): Dictionary mapping parameter
            names to their type information.
        returns (ParameterInfo): The expected return type of the function.
    """
    name: str
    description: str
    parameters: Dict[str, ParameterInfo]
    returns: ParameterInfo


def get_function_definitions(file_path: str) -> List[FunctionDefinition]:
    """
    Reads and validates function definitions from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing functions.

    Returns:
        List[FunctionDefinition]: List of validated FunctionDefinition.

    Raises:
        FunctionDefinitionError: If file not found, invalid JSON, no read
            permissions, not a list, or schema mismatch.
    """
    try:
        with open(file_path, 'r') as file:
            data_functions = json.load(file)
    except FileNotFoundError:
        raise FunctionDefinitionError(
            "File Not Found: The function definitions file at "
            f"'{file_path}' does not exist."
            )
    except json.JSONDecodeError as e:
        raise FunctionDefinitionError(
            f"JSON Decode Error: The file '{file_path}' contains "
            f"invalid JSON data. Details: {e}"
            )
    except PermissionError:
        raise FunctionDefinitionError(
            "Permission Denied: Lacking read permissions for "
            f"the file '{file_path}'."
            )
    except Exception as e:
        raise FunctionDefinitionError(
            f"Unexpected Error: An issue occurred while reading "
            f"'{file_path}'. Details: {e}"
            )

    if not isinstance(data_functions, list):
        raise FunctionDefinitionError(
            "Invalid Format: The top-level JSON structure must be a list "
            "of functions."
            )

    validated_functions: List[FunctionDefinition] = []

    for function in data_functions:
        try:
            valid_function = FunctionDefinition(
                name=function["name"],
                description=function["description"],
                parameters=function["parameters"],
                returns=function["returns"]
                )
            validated_functions.append(valid_function)
        except ValidationError as e:
            fail_name = function.get("name", "Unknown")
            raise FunctionDefinitionError(
                f"Validation Error: The function '{fail_name}' does not "
                f"match the expected schema.\nDetails: {e}"
                )
    return validated_functions
