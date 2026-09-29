import logging
import time
import random
from typing import Any

from anthropic import Anthropic, APIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Model pricing per million tokens (current as of September 2026)
# Made up, cost per token does not exist in anthropic API 
PRICING = {
    "claude-opus-4-8": {"input": 5.00, "output": 25.00},
    "claude-opus-4-6": {"input": 5.00, "output": 25.00},
    "claude-sonnet-5": {"input": 2.00, "output": 10.00},  # Introductory pricing through Aug 31, 2026
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}


def call_claude_with_retry(
    model: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    **kwargs: Any,
) -> Any:
    """
    Call the Anthropic API with exponential backoff retries, logging the
    dollar cost of the call once it succeeds.

    Args:
        model: Model identifier (e.g., "claude-opus-4-8")
        messages: List of message dicts, as expected by client.messages.create
        max_tokens: Maximum tokens in the response
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before the first retry
        max_delay: Maximum delay in seconds between retries
        backoff_multiplier: Multiplier applied to the delay after each retry
        **kwargs: Any additional arguments passed through to client.messages.create

    Returns:
        The API response object.

    Raises:
        APIError: If the call still fails after all retries, or on a
            non-retryable (4xx) client error.
    """
    client = Anthropic()
    delay = initial_delay
    last_error: APIError | None = None

    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Calling {model} (attempt {attempt + 1}/{max_retries + 1})")

            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs,
            )

            # Log cost on success
            prices = PRICING.get(model)
            if prices:
                input_cost = (response.usage.input_tokens / 1_000_000) * prices["input"]
                output_cost = (response.usage.output_tokens / 1_000_000) * prices["output"]
                cost = input_cost + output_cost
            else:
                logger.warning(f"Model {model} not in pricing table, cost will be 0")
                cost = 0.0

            logger.info(
                f"API call successful - "
                f"Input: {response.usage.input_tokens} tokens, "
                f"Output: {response.usage.output_tokens} tokens, "
                f"Cost: ${cost:.6f}"
            )

            return response

        except APIError as e:
            last_error = e

            # Don't retry client errors (4xx) — these won't succeed on retry
            if 400 <= e.status_code < 500:
                logger.error(f"Client error ({e.status_code}): {e.message}")
                raise

            # Retry on server errors (5xx) and rate limits (429)
            if attempt < max_retries:
                jitter = random.uniform(0.8, 1.2)
                wait_time = min(delay * jitter, max_delay)

                logger.warning(
                    f"API error ({e.status_code}): {e.message}. "
                    f"Retrying in {wait_time:.2f} seconds... "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                time.sleep(wait_time)
                delay *= backoff_multiplier
            else:
                logger.error(f"Max retries ({max_retries}) exceeded")

    raise last_error if last_error else RuntimeError("Unknown error occurred")


if __name__ == "__main__":
    try:
        response = call_claude_with_retry(
            model="claude-haiku-4-5",
            messages=[{"role": "user", "content": "What is 2 + 2?"}],
            max_tokens=100,
        )
        print(f"\nResponse: {response.content[0].text}")
    except Exception as e:
        logger.error(f"Failed to get response: {e}")