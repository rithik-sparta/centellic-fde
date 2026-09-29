
# 1. Set up Fake Building blocks
# 2. Create a Fake Model (that keeps going)
# 3. Sub in our fakes from step 1
# 4. hit our endpoint
# 5. check it stopped
# pretend the model never stops... check your code stops it anyway


from fastapi.testclient import TestClient

import agent
from main import app

client = TestClient(app)


class FakeToolUseBlock:
    type = "tool_use",
    id = "tools_01",
    name = "search_knowledge_base",
    
    def __init__(self, input_):
        self.input = input_
        
class FakeUsage:
    def __init__(self, input_token, output_token):
        self.input_tokens, self.output_tokens = input_token, output_token

class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content, self.stop_reason, self.usage = content, stop_reason, usage

def test_agent_stops_at_max_iterations_instead_of_looping_forever(monkeypatch):

    def fake_create(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query" : "anything"})], "tool_use", FakeUsage(100,15)
        )

    monkeypatch.setattr(agent.client.messages, "create", fake_create)
    monkeypatch.setattr(
        agent.knowledge, "search",
        lambda question="1", tok_k=3: [{"id" : "doc-001", "title" : "t", "text" : "x", "score" : 0.5}]
    )
    
    response = client.post("/agent/ask", json={"question":"never resolves"})
    body = response.json()
    
    # assert - completed
    assert body.get("completed", None) == None
    
    
    # assert - stop_reason
    assert body.get("stop_reason", None) == None
    
    
    # assert - tool_calls_made
    assert body.get("tool_calls_made", -1) == -1