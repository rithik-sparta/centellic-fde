import os

from dotenv import load_dotenv

load_dotenv()

try:

    MODEL : str = os.environ["ANTHROPIC_MODEL"]

    ANTHROPIC_API_KEY : str = os.environ["ANTHROPIC_API_KEY"]

    VOYAGE_EMBED_MODEL : str = os.environ["VOYAGE_EMBED_MODEL"]

    VOYAGE_API_KEY : str = os.environ["VOYAGE_API_KEY"]
    
    RELEVANCE_FLOOR : float = float(os.environ["RELEVANCE_FLOOR"])
    
    MAX_ITERATIONS : int = 15
    
except ValueError as exc:
    raise RuntimeError(f"Server misconfiguration: Value for relevance floor ({os.environ["RELEVANCE_FLOOR"]}) must be castable to float") from exc
except RuntimeError as exc:
    raise RuntimeError("Missing an environment variable:") from exc


