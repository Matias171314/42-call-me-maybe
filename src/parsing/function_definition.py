import json
from typing import List, Dict
from pydantic import BaseModel, ValidationError


class FunctionDefinitionError(Exception):
    pass


class ParameterInfo(BaseModel):
    type: str


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ParameterInfo]
    returns: ParameterInfo


def get_function_definitions(file_path: str) -> List[FunctionDefinition]:
    try:
        with open(file_path, 'r') as file:
            data_functions = json.load(file)
    except FileNotFoundError:
        raise FunctionDefinitionError(
            f"Functions definition file was not found at '{file_path}'."
            )
    except json.JSONDecodeError as e:
        raise FunctionDefinitionError(
            f"File '{file_path}' is not a valid JSON:\n{e}"
            )
    except PermissionError:
        raise FunctionDefinitionError("Non read permission in the file.")
    except Exception as e:
        raise FunctionDefinitionError(
            f"Unexpected error reading the file:\n{e}"
            )

    if not isinstance(data_functions, list):
        raise FunctionDefinitionError(
            "The JSON file must contain a list of functions."
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
                f"Structure error in function '{fail_name}':\n{e}"
                )
    return validated_functions
