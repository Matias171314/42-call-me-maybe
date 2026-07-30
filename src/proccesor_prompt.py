from typing import Any, Dict, List
from src import Prompt, FunctionDefinition, Model


class PromptProcessor():
    """
    Object specialized in process natural language prompts into function calls.
    """
    def __init__(
        self,
        prompts: List[Prompt],
        functions_definition: List[FunctionDefinition],
        llm: Model
    ):
        self.__prompts = prompts
        self.__functions_definition = functions_definition
        self.__llm = llm
        self.nb_prompts = len(prompts)

    def process(self) -> List[Dict[str, Any]]:
        """
        Processes the entire list of prompts sequentially.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the
                prompt, the inferred function name, and its parsed arguments.
        """
        output = []

        for prompt in self.__prompts:
            prompt_output: Dict[str, Any] = {}
            prompt_output["prompt"] = prompt.prompt

            fn_name = self.generate_fn_name(prompt)
            prompt_output["fn_name"] = fn_name

            params = self.generate_parameters(prompt, fn_name)
            prompt_output["args"] = params

            output.append(prompt_output)
            print(prompt_output)
        return output

    def get_available_functions(self) -> List[Dict[str, str]]:
        """
        Extracts the names and descriptions of all loaded functions.

        Returns:
            List[Dict[str, str]]: A list of simplified function metadata.
        """
        available_functions = []
        for function in self.__functions_definition:
            available_functions.append({
                "name": function.name,
                "description": function.description
            })
        return available_functions

    def generate_fn_name(self, prompt: Prompt) -> str:
        """
        Infers the target function name using constrained prefix matching.

        Args:
            prompt (Prompt): The prompt object.

        Returns:
            str: The exact name of the matched function.
        """
        available_functions = self.get_available_functions()
        function_progress = ""
        prompt_message = (
            "Task: Select the most appropriate function to solve the "
            "user's request.\n"
            f"Available Functions: {available_functions}\n"
            f"User Request: '{prompt.prompt}'\n"
            "Rules: Output ONLY the exact name of the chosen function. "
            "Do not add quotes, spaces, or explanations.\n"
            "Selected Function:"
        )

        while True:
            for generation in self.__llm.predict_multiple_tokens(
                prompt_message=prompt_message,
                previous_tokens=function_progress
            ):
                remaining_functions = []
                for function in available_functions:
                    if function["name"].startswith(
                        function_progress + generation
                    ):
                        remaining_functions.append(function)
                if (len(remaining_functions) == 1):
                    return remaining_functions[0]["name"]
                elif len(remaining_functions) > 1 and generation != "":
                    function_progress = function_progress + generation
                    available_functions = remaining_functions
                    break

    def generate_parameters(
        self, prompt: Prompt, function_name: str
    ) -> Dict[str, Any]:
        """
        Iterates over the required parameters of a function and generates them.

        Args:
            prompt(Prompt): The original prompt.
            function_name (str): The resolved name of the target function.

        Returns:
            Dict[str, Any]: A dictionary mapping parameter names to values.
        """
        for function_def in self.__functions_definition:
            if (function_def.name == function_name):
                definition = function_def

        output: Dict[str, Any] = {}
        for param in definition.parameters:
            previous_gen = ""
            for arg in output.keys():
                previous_gen = previous_gen + arg +\
                    "=" + str(output[arg]) + "\n"
            previous_gen = previous_gen + param + "="
            if definition.parameters[param].type == "string":
                output[param] = self.generate_str_parameter(
                    prompt, definition, previous_gen)
            elif definition.parameters[param].type == "number":
                output[param] = self.generate_int_parameter(
                    prompt, definition, previous_gen)
        return output

    def generate_int_parameter(
        self,
        prompt: Prompt,
        function: FunctionDefinition,
        previous_gen: str
    ) -> float:
        """
        Generates a numeric parameter using strict regex filtering.

        Args:
            prompt (Prompt): The original prompt.
            function (FunctionDefinition): The function being executed.
            previous_gen (str): The accumulated history of parameters.

        Returns:
            float: The validated numeric value.
        """
        prompt_message = (
            "Task: Extract exact numeric value for the requested parameter.\n"
            f"Original Prompt: '{prompt.prompt}'\n"
            "Rules:\n"
            "- Output ONLY the raw number (integer or float).\n"
            "- Do NOT add quotes, spaces, or words.\n"
            "- Stop at the end of the number.\n\n"
            f"Context: {function.model_dump_json()}\n"
        )
        argument_progress = ""
        while True:
            for generation in self.__llm.predict_multiple_tokens(
                prompt_message, previous_gen + argument_progress
            ):
                if not generation:
                    try:
                        return float(argument_progress)
                    except ValueError:
                        argument_progress = ''

                valid_chars = "-0123456789.\n"
                stop = False
                for character in generation:
                    if character not in valid_chars:
                        stop = True
                if stop:
                    continue

                current_attempt = argument_progress + generation
                if (current_attempt).count(".") > 1:
                    continue
                if (current_attempt).count("-") > 1:
                    continue
                if (current_attempt).count("-") == 1\
                        and (current_attempt)[0] != "-":
                    continue

                argument_progress = current_attempt
                if '\n' in argument_progress:
                    clean_number = argument_progress.split("\n")[0]
                    if not clean_number:
                        continue
                    try:
                        return float(clean_number)
                    except ValueError:
                        argument_progress = ""
                        break
                break

    def generate_str_parameter(
        self,
        prompt: Prompt,
        function: FunctionDefinition,
        previous_gen: str
    ) -> str:
        """
        Generates a string parameter, stopping at a newline character.

        Args:
            prompt (Prompt): The original prompt.
            function (FunctionDefinition): The function being executed.
            previous_gen (str): The accumulated history of parameters.

        Returns:
            str: The generated string parameter.
        """
        prompt_message = (
            f"Task: Extract the exact string value for the parameter.\n"
            f"Prompt: '{prompt.prompt}'\n"
            f"Rules:\n"
            f"- Output ONLY the raw string value.\n"
            f"- NO quotes around the text.\n"
            f"- NO trailing spaces.\n"
            f"- Do NOT add next parameters (stop at the end of the value).\n\n"
            f"Context: {function.model_dump_json()}\n"
        )
        argument_progress = ''
        while True:
            generation = self.__llm.predict_token(
                prompt_message, previous_gen + argument_progress
                )
            if not generation:
                break
            if '\n' in generation:
                argument_progress += generation.split('\n')[0]
                break
            if generation.startswith(','):
                break
            argument_progress += generation
        clean_result = argument_progress.strip(' "\'')
        return clean_result
