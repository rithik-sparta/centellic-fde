from dotenv import load_dotenv
import os
load_dotenv()


MODEL = os.environ["ANTHROPIC_MODEL"]

RELEVANCE_FLOOR = os.environ["RELEVANCE_FLOOR"]

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]

