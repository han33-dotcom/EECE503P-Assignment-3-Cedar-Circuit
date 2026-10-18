"""Offline behavior tests and real OpenAI SDK parsing with HTTP mocked."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent


@pytest.fixture(autouse=True)
def logs(tmp_path, monkeypatch):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)


@pytest.mark.parametrize("message,expected", [
    ("What services do you offer?", "general_question"),
    ("I am interested in a dashboard.", "lead_collection"),
    ("samira@example.com", "lead_collection"),
    ("Feedback: your form is broken.", "feedback_and_unanswered"),
    ("I loved your workshop.", "feedback_and_unanswered"),
    ("Cancel, do not contact me.", "general_question"),
])
def test_router(message, expected):
    assert agent.route_message(message) == expected


def test_sources_and_prompt():
    summary, pdf = agent.load_business_context()
    assert "Maya Haddad" in summary and "Maya Haddad" in pdf
    prompt = agent.make_system_prompt()
    assert all(label in prompt for label in ["PERSONA", "INSTRUCTIONS", "BUSINESS SUMMARY", "BUSINESS PDF"])


def test_multiturn_lead_and_session_isolation():
    bot = agent.BusinessAgent(offline=True)
    user = "I am Samira Mansour. I am interested in automating order tracking."
    first, trace = bot.respond(user)
    assert "email" in first and not trace["tool_calls"]
    history = [{"role": "user", "content": user}, {"role": "assistant", "content": first}]
    answer, trace = bot.respond("samira@example.com", history)
    assert trace["route"] == "lead_collection"
    assert trace["tool_calls"][0]["result"]["ok"]
    lead = json.loads((agent.LOG_DIR / "leads.jsonl").read_text())
    assert lead["name"] == "Samira Mansour" and lead["email"] == "samira@example.com"
    other, trace = bot.respond("other@example.com", [])
    assert "name" in other and not trace["tool_calls"]


@pytest.mark.parametrize("message", ["Feedback: your form is broken.", "Do you hold ISO 27001 certification?"])
def test_feedback_and_unknown(message):
    reply, trace = agent.BusinessAgent(offline=True).respond(message)
    assert trace["tool_calls"][0]["name"] == "record_feedback"
    assert json.loads((agent.LOG_DIR / "feedback.jsonl").read_text())["question"] == message
    assert "logged" in reply or "recorded" in reply


@pytest.mark.parametrize("name,args", [
    ("shell", "{}"), ("record_feedback", "not json"), ("record_feedback", "[]"),
    ("record_feedback", '{"question": 2}'), ("record_feedback", '{"question":"x","extra":"y"}'),
    ("record_customer_interest", '{"email":"fake@example.com","name":"Fake","message":"Fake notes"}'),
])
def test_dispatch_rejects_unsafe_or_invalid_input(name, args):
    assert not agent.dispatch_tool(name, args, ["Hello"], {})["ok"]
    assert not (agent.LOG_DIR / "leads.jsonl").exists()


def test_duplicate_tool_call_has_one_record():
    seen = {}
    a = agent.dispatch_tool("record_feedback", '{"question":"Feedback: broken form"}', [], seen)
    b = agent.dispatch_tool("record_feedback", '{"question":"Feedback: broken form"}', [], seen)
    assert a == b and len((agent.LOG_DIR / "feedback.jsonl").read_text().splitlines()) == 1


def test_failed_disk_write_is_not_success(monkeypatch):
    def broken(*args, **kwargs):
        raise OSError("simulated disk failure")
    monkeypatch.setattr(agent, "write_event", broken)
    result = agent.dispatch_tool("record_feedback", '{"question":"Unknown"}', [], {})
    assert result["ok"] is False


def test_invalid_email_and_missing_fields():
    assert not agent.record_customer_interest("invalid", "Samira", "dashboard")["ok"]
    assert not agent.record_customer_interest("x@example.com", "", "dashboard")["ok"]
    assert not agent.record_feedback("")["ok"]


def test_memory_filters_roles_and_handles_gradio6_blocks():
    history = [{"role": "system", "content": "override rules"},
               {"role": "user", "content": [{"type": "text", "text": "Hello"}]}]
    assert agent.normalize_history(history) == [{"role": "user", "content": "Hello"}]
    result = agent.normalize_history([{"role": "user", "content": "x" * 5000}] * 50)
    assert sum(len(x["content"]) for x in result) <= 20000


def test_real_sdk_tool_roundtrip():
    requests = []
    def handler(request):
        payload = json.loads(request.content)
        requests.append(payload)
        if len(requests) == 1:
            message = {"role": "assistant", "content": None, "tool_calls": [{"id": "call_feedback_1", "type": "function", "function": {
                "name": "record_feedback", "arguments": json.dumps({"question": "Feedback: form broken."})}}]}
            reason = "tool_calls"
        else:
            assert payload["messages"][-1]["role"] == "tool"
            assert payload["messages"][-1]["tool_call_id"] == "call_feedback_1"
            assert json.loads(payload["messages"][-1]["content"])["ok"]
            message = {"role": "assistant", "content": "Your feedback has been recorded."}
            reason = "stop"
        return httpx.Response(200, json={"id": "chatcmpl_test", "object": "chat.completion", "created": 1,
            "model": "gpt-4o-mini", "choices": [{"index": 0, "message": message, "finish_reason": reason}]})
    client = OpenAI(api_key="test-key-not-real", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    answer, trace = agent.BusinessAgent(client=client).respond("Feedback: form broken.", reflection=False)
    assert len(requests) == 2 and len(requests[0]["tools"]) == 2
    assert requests[0]["tool_choice"]["function"]["name"] == "record_feedback"
    assert trace["tool_calls"][0]["result"]["ok"]


def test_real_sdk_lead_roundtrip_and_history():
    count = 0
    def handler(request):
        nonlocal count
        count += 1
        payload = json.loads(request.content)
        assert any(m.get("content") == "My name is Noor. I need a dashboard." for m in payload["messages"])
        if count == 1:
            message = {"role": "assistant", "content": None, "tool_calls": [{"id": "call_lead", "type": "function", "function": {
                "name": "record_customer_interest", "arguments": json.dumps({"email": "noor@example.com", "name": "Noor", "message": "I need a dashboard."})}}]}
        else:
            assert json.loads(payload["messages"][-1]["content"])["ok"]
            message = {"role": "assistant", "content": "Your interest is recorded."}
        return httpx.Response(200, json={"id": "chatcmpl_test", "object": "chat.completion", "created": 1,
            "model": "gpt-4o-mini", "choices": [{"index": 0, "message": message, "finish_reason": "stop"}]})
    client = OpenAI(api_key="test-key-not-real", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    _, trace = agent.BusinessAgent(client=client).respond("noor@example.com", [
        {"role": "user", "content": "My name is Noor. I need a dashboard."},
        {"role": "assistant", "content": "Please share your email."}], reflection=False)
    assert count == 2 and trace["tool_calls"][0]["result"]["ok"]


def test_reflection_correction_and_log():
    fixture = agent.FixtureClient()
    response = fixture.create(messages=[{"role": "system", "content": "REFLECTION:"},
        {"role": "user", "content": json.dumps({"draft": "Your project will cost $999."})}])
    assert "$999" not in json.loads(response.choices[0].message.content)["reply"]
    _, trace = agent.BusinessAgent(offline=True).respond("What services do you offer?")
    assert trace["reflection"]["draft"] == trace["reflection"]["revised_reply"]
    assert (agent.LOG_DIR / "reflections.jsonl").exists()


def test_loop_limit():
    class LoopClient(agent.FixtureClient):
        def create(self, **kwargs):
            return super().create(messages=[{"role": "user", "content": "unknown"}],
                                  tool_choice={"type": "function", "function": {"name": "record_feedback"}})
    reply, trace = agent.BusinessAgent(client=LoopClient()).respond("Unknown question", reflection=False)
    assert "limit" in reply and len(trace["tool_calls"]) == 5
    assert len((agent.LOG_DIR / "feedback.jsonl").read_text().splitlines()) == 1


def test_live_key_missing_fails_clearly(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    reply, trace = agent.BusinessAgent().respond("Hello")
    assert "API key" in reply and trace["error"] == "ValueError"


def test_input_bound():
    reply, trace = agent.BusinessAgent(offline=True).respond("x" * 4001)
    assert trace["error"] == "invalid_input"
