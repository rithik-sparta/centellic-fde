import inspect
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
c = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Does the method it called actually exist?
print([m for m in dir(c.messages) if not m.startswith("_")])

# Does every parameter it used actually exist?
print(list(inspect.signature(c.messages.create).parameters))

# Does every field it reads off the response actually exist?
from anthropic.types import Message
print(list(Message.model_fields))