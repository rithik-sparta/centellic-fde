import anthropic, inspect
c = anthropic.Anthropic(api_key="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")

# Does the method it called actually exist?
print([m for m in dir(c.messages) if not m.startswith("_")])

# Does every parameter it used actually exist?
print(list(inspect.signature(c.messages.create).parameters))

# Does every field it reads off the response actually exist?
from anthropic.types import Message
print(list(Message.model_fields))