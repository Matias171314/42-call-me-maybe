from typing import Generator
from src import Small_LLM_Model


class Model(Small_LLM_Model):
    """
    Wrapper for the Small_LLM_Model SDK providing text generation methods.

    This class handles the tokenization, prompt formatting, and logit
    processing required to interact with the underlying neural network.
    """
    def _build_prompt(self, message: str, previous: str) -> str:
        """Helper to construct the prompt with chat templates."""
        return (
            f"<|im_start|>user\n{message}<|im_end|>\n"
            f"<|im_start|>assistant\n<think>\n\n</think>\n\n{previous}"
        )

    def predict_token(
        self,
        prompt_message: str,
        previous_tokens: str = '',
        skip: int = 0
    ) -> str:
        """
        Gets the next most probable token for a given sequence.

        Args:
            prompt_message (str): The natural language query.
            previous_tokens (str, optional): Tokens already generated.
                Defaults to ''.
            skip (int, optional): The rank of the token to return (0 for the
                best, 1 for the second best, etc.). Defaults to 0.

        Returns:
            str: The decoded text of the selected token.
        """
        prompt = self._build_prompt(prompt_message, previous_tokens)
        tensors = self.encode(prompt)

        probabilities = self.get_logits_from_input_ids(tensors.tolist()[0])

        sorted_tokens = sorted(probabilities, reverse=True)

        token_id = probabilities.index(sorted_tokens[skip])

        return self.decode(token_id)

    def predict_multiple_tokens(
        self,
        prompt_message: str,
        previous_tokens: str = '',
        skip: int = 0
    ) -> Generator[str, None, None]:
        """
        Yields alternative token predictions for a single position.

        Useful for constrained decoding (e.g., rejecting invalid tokens
        and requesting the next most probable one).

        Args:
            prompt_message (str): The natural language query.
            previous_tokens (str, optional): Tokens already generated.
                Defaults to ''.
            skip (int, optional): The starting rank of the token to yield.
                Defaults to 0.

        Yields:
            Generator[str, None, None]: A generator that infinitely yields
                the next best token string.
        """
        prompt = self._build_prompt(prompt_message, previous_tokens)
        tensors = self.encode(prompt)

        probabilities = self.get_logits_from_input_ids(tensors.tolist()[0])
        sorted_tokens = sorted(probabilities, reverse=True)

        while True:
            token_id = probabilities.index(sorted_tokens[skip])
            yield self.decode(token_id)
            skip += 1
