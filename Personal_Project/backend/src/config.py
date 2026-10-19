import os

from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

try:

    MODEL : str = os.environ["ANTHROPIC_MODEL"]

    ANTHROPIC_API_KEY : str = os.environ["ANTHROPIC_API_KEY"]

    VOYAGE_EMBED_MODEL : str = os.environ["VOYAGE_EMBED_MODEL"]

    VOYAGE_API_KEY : str = os.environ["VOYAGE_API_KEY"]
    
    RELEVANCE_FLOOR : float = float(os.environ["RELEVANCE_FLOOR"])
    
    MAX_ITERATIONS : int = 15
    
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Server misconfiguration: Value for relevance floor ({os.environ["RELEVANCE_FLOOR"]}) must be castable to float")

