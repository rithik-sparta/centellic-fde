
# 1. Set up Fake Building blocks
# 2. Create a Fake Model (that keeps going)
# 3. Sub in our fakes from step 1
# 4. hit our endpoint
# 5. check it stopped
# pretend the model never stops... check your code stops it anyway


from fastapi.testclient import TestClient
import agent.tools as tools
import agent.model as mdl
import agent.summarise_borrower as sb
import retrieval.document_store as ds
import anthropic

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
        
def test_health():
    assert True

def test_ask_agent_stops_at_max_iterations_instead_of_looping_forever(monkeypatch):

    def fake_create(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query" : "anything"})], "tool_use", FakeUsage(100,15)
        )

    monkeypatch.setattr(mdl.client.messages, "create", fake_create)
    monkeypatch.setattr(
        tools.DocumentSearchTool, "get_context",
        lambda question="1", tok_k=3: [{"id" : "doc-001", "title" : "t1", "text" : "x", "score" : 0.5},
                                       {"id" : "doc-003", "title" : "t2", "text" : "y", "score" : 0.4},
                                       {"id" : "doc-005", "title" : "t3", "text" : "z", "score" : 0.3}]
    )
    
    monkeypatch.setattr(
        tools.RecordSearchTool, "get_records",
        lambda entity_name="borrowers", borrower_id="b-02", filter_condition=None : [{"id" : "b-02", "name" : "test", "sector" : "Renewables", "score" : 0.5}]
    )
    
    monkeypatch.setattr(
        tools.CalculationTool, "run",
        lambda name="net_debt", arguments={"total_debt":300.0,"cash":100.0} : 3.0
    )
    
    response = client.post("/borrowers/ask", json={"question":"never resolves"})
    body = response.json()
    
    # assert - completed
    assert body.get("completed", None) == False
    
    
    # assert - stop_reason
    assert body.get("stop_reason", None) == "tool_use"
    
    
    # assert - tool_calls_made
    assert body.get("tool_calls_made", -1) == 0
    
def test_credit_assessment_agent_stops_at_max_iterations_instead_of_looping_forever(monkeypatch):
    def fake_create(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query" : "anything"})], "tool_use", FakeUsage(100,15)
        )

    monkeypatch.setattr(mdl.client.messages, "parse", fake_create)
    monkeypatch.setattr(
        tools.DocumentSearchTool, "get_context",
        lambda question="1", tok_k=3: [{"id" : "doc-001", "title" : "t1", "text" : "x", "score" : 0.5},
                                       {"id" : "doc-003", "title" : "t2", "text" : "y", "score" : 0.4},
                                       {"id" : "doc-005", "title" : "t3", "text" : "z", "score" : 0.3}]
    )
    
    monkeypatch.setattr(
        tools.RecordSearchTool, "get_records",
        lambda entity_name="borrowers", borrower_id="b-02", filter_condition=None : [{"id" : "b-02", "name" : "test", "sector" : "Renewables", "score" : 0.5}]
    )
    
    monkeypatch.setattr(
        tools.CalculationTool, "run",
        lambda name="net_debt", arguments={"total_debt":300.0,"cash":100.0} : 3.0
    )
    
    response = client.post("/borrowers/b-02/credit_assessment")
    body = response.json()
    
    # assert - completed
    assert body.get("completed", None) == False
    
    
    # assert - stop_reason
    assert body.get("stop_reason", None) == "tool_use"
    
    
    # assert - tool_calls_made
    assert body.get("tool_calls_made", -1) == 0
    
FAKE_SUMMARY = [
    {"borrower": "b-01", "name": "Northbridge Components", "sector": "Manufacturing", "summary": "A manufacturing company",
         "input_tokens": 120, "output_tokens":95, "stop_reason": "end_turn"},
]

#tests
#what paths could the call take?

def test_summary_returns_text_and_usage(monkeypatch):
    monkeypatch.setattr(sb, "summarise_borrower", lambda borrower: FAKE_SUMMARY)
    response = client.post("/borrowers/b-01/summary")
    #assrt what it should do
    assert response.status_code == 200
    assert response.json()[0]["input_tokens"] == 120
    
def test_provider_timeout_becomes_504(monkeypatch):
    def boom(borrower):
        raise anthropic.APITimeoutError(request= None) # type: ignore
    monkeypatch.setattr(sb, "summarise_borrower", boom)
    response = client.post("/borrowers/b-01/summary")
    assert response.status_code == 504
    assert response.json()["detail"] == "Summary provider timed out"
    

# Check that our estimate does not call the model
def test_estimate_does_not_call_the_model(monkeypatch):
    # Monkeypatch is a test kit to set attriutes that are mocked
    monkeypatch.setattr(mdl,"estimate_input_tokens",lambda borrower, model, system, prompt: 137)
    response = client.get("/borrowers/b-01/summary/estimate")
    json = response.json()
    
    assert response.status_code == 200
    assert json["estimated_input_tokens"] == 137
    
def test_stream_yields_chunks(monkeypatch):
    monkeypatch.setattr(sb,"stream_borrower_summary", lambda borrower: iter(["Nort", "hbri", "dge", " Com", "pon","ents"]))
    
    with client.stream("POST","/borrowers/b-01/stream_summary") as response:
        assert response.status_code==200
        body = "".join(response.iter_text())
    assert body == "Northbridge Components"
    

STRONG_HIT = {"id": "doc-008", "title": "Benchmarking Methodology",
              "text": "Revenue per lawyer is calculated as...", "score": 0.81}
WEAK_HIT = {"id": "doc-003", "title": "Okonkwo Bell Strategy Briefing",
            "text": "Okonkwo Bell is a boutique...", "score": 0.12}
FAKE_ANSWER = {"answer": "Revenue divided by fee-earners [doc-008].",
               "input_tokens": 400, "output_tokens": 30, "stop_reason": "end_turn"}


def test_search_returns_ranked_hits(monkeypatch):
    monkeypatch.setattr(ds, "search", lambda q, k=3: [STRONG_HIT])

    response = client.post("/borrowers/search", json={"question": "how is PEP worked out"})
    assert response.status_code == 200
    assert response.json()["results"][0]["id"] == "doc-008"


def test_search_before_indexing_is_409(monkeypatch):
    def not_built(q, k=3):
        raise RuntimeError("Index is empty, call build_index() first")

    monkeypatch.setattr(ds, "search", not_built)

    response = client.post("/borrowers/search", json={"question": "anything at all"})
    assert response.status_code == 409


def test_ask_answers_and_cites_sources(monkeypatch):
    monkeypatch.setattr(ds, "search", lambda q, k=3: [STRONG_HIT])
    monkeypatch.setattr(mdl, "answer_from_context", lambda q, c: FAKE_ANSWER)

    body = client.post("/borrowers/context", json={"question": "how is PEP worked out"}).json()
    assert body["refused"] is False
    assert body["sources"][0]["id"] == "doc-008"
    assert body["input_tokens"] == 400


def test_ask_refuses_without_calling_the_model(monkeypatch):
    monkeypatch.setattr(ds, "search", lambda q, k=3: [WEAK_HIT])

    def must_not_be_called(q, c):
        raise AssertionError("The model was called despite no relevant context")

    monkeypatch.setattr(mdl, "answer_from_context", must_not_be_called)

    body = client.post("/borrowers/context", json={"question": "what is the capital of France"}).json()
    assert body["refused"] is True
    assert body["answer"] is None
    assert body["sources"] == []


def test_short_question_is_rejected_before_any_work():
    assert client.post("/borrowers/ask", json={"question": "hi"}).status_code == 422


def test_top_k_is_bounded():
    response = client.post("/borrowers/context", json={"question": "valid question", "top_k": 99})
    assert response.status_code == 422
    