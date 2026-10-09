import os

from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

try:

    MODEL : str = os.environ["ANTHROPIC_MODEL"]

    RELEVANCE_FLOOR : float = float(os.environ["RELEVANCE_FLOOR"])

    ANTHROPIC_API_KEY : str = os.environ["ANTHROPIC_API_KEY"]

    VOYAGE_API_KEY : str = os.environ["VOYAGE_API_KEY"]
    
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Server misconfiguration: Value for relevance floor ({os.environ["RELEVANCE_FLOOR"]}) must be castable to float")

