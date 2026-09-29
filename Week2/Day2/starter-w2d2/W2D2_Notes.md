Why FastAPI

* Starlette (FastAPI built on top of Starlette):
  * Handles HTTP plumbing
  * Recieving requests, Sending responses
* Pydantic
  * Data validation
  * Check what arrives is what you expected
* FastAPI reads your python type hints and wires the two automatically.
* One annotation, three jobs:
  * pulls value, converts to correct type
  * Rejects malformed requests, handled by pydantic
  * Documentation is generated automatically.
* Why it is default?
  * Validation - Malformed input is rejected before your code runs.
  * Documentation - Generated from code. Can not drift out of date.
  * Concurrency - Async Native. Built for waiting or slow things efficiently. Suitable for AI workflows as LLM requests are mostly spent waiting.
*
