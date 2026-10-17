"""Core runner tests with FakeClient: tool loop, approval gating, max turns, errors."""

import json

import pytest

from core import AgentRunner, FakeClient, Solution, fake_text, fake_tool_call, fake_tool_calls
from core.clients import FakeResponse, make_client


def _solution(handlers=None, approval=()):
    calls = []

    def lookup(order_id: str):
        calls.append(order_id)
        return {"order_id": order_id, "status": "shipped", "email": "a.person@example.com"}

    def refund(order_id: str, amount: float):
        return {"refunded": amount}

    def boom(x: str):
        raise RuntimeError("upstream 500")

    tools = [
        {"name": "lookup", "description": "d", "input_schema": {
            "type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"],
            "additionalProperties": False}},
        {"name": "refund", "description": "d", "input_schema": {
            "type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
            "required": ["order_id", "amount"]}},
        {"name": "boom", "description": "d", "input_schema": {
            "type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]}},
    ]
    sol = Solution(name="test", system_prompt="You are a test agent.", tools=tools,
                   handlers=handlers or {"lookup": lookup, "refund": refund, "boom": boom},
                   requires_approval=set(approval))
    return sol, calls


def test_tool_loop_executes_and_returns_final_text():
    sol, calls = _solution()
    client = FakeClient([fake_tool_call("lookup", {"order_id": "1001"}), fake_text("Your order has shipped.")])
    result = AgentRunner(sol, client).run("where is 1001")
    assert result.final_text == "Your order has shipped."
    assert result.stop_reason == "end_turn"
    assert calls == ["1001"]
    # second request carries the tool_result for the first tool_use
    second = client.calls[1]["messages"]
    tool_result = second[-1]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert json.loads(tool_result["content"])["status"] == "shipped"
    assert client.calls[0]["tools"] == sol.tools
    assert client.calls[0]["system"].startswith("You are a test agent.")


def test_parallel_tool_calls_return_in_one_user_message():
    sol, calls = _solution()
    client = FakeClient([fake_tool_calls([("lookup", {"order_id": "1"}), ("lookup", {"order_id": "2"})]),
                         fake_text("done")])
    result = AgentRunner(sol, client).run("two orders")
    assert calls == ["1", "2"]
    user_msg = client.calls[1]["messages"][-1]
    assert user_msg["role"] == "user" and len(user_msg["content"]) == 2
    assert len(result.tool_calls) == 2


def test_approval_required_tool_is_not_executed():
    executed = []
    sol, _ = _solution(handlers={
        "lookup": lambda order_id: {}, "boom": lambda x: {},
        "refund": lambda order_id, amount: executed.append((order_id, amount)) or {"refunded": amount},
    }, approval={"refund"})
    client = FakeClient([fake_tool_call("refund", {"order_id": "1", "amount": 20.0}),
                         fake_text("Refund requested, pending approval.")])
    runner = AgentRunner(sol, client)
    result = runner.run("refund me")
    assert executed == []
    assert len(result.pending_approvals) == 1
    pending = result.pending_approvals[0]
    assert pending["status"] == "pending_approval" and pending["tool"] == "refund"
    sent = json.loads(client.calls[1]["messages"][-1]["content"][0]["content"])
    assert sent["status"] == "pending_approval"
    # a human approves later: now it runs
    out = runner.approve(pending["approval_id"])
    assert out == {"refunded": 20.0} and executed == [("1", 20.0)]
    with pytest.raises(KeyError):
        runner.approve(pending["approval_id"])


def test_approver_callback_and_auto_approve():
    executed = []
    sol, _ = _solution(handlers={
        "lookup": lambda order_id: {}, "boom": lambda x: {},
        "refund": lambda order_id, amount: executed.append(order_id) or {"ok": True}}, approval={"refund"})
    client = FakeClient([fake_tool_call("refund", {"order_id": "A", "amount": 1.0}), fake_text("ok")])
    AgentRunner(sol, client, approver=lambda name, inp: True).run("x")
    client = FakeClient([fake_tool_call("refund", {"order_id": "B", "amount": 1.0}), fake_text("ok")])
    AgentRunner(sol, client, auto_approve={"refund"}).run("x")
    assert executed == ["A", "B"]


def test_max_turns_stops_the_loop():
    sol, calls = _solution()
    client = FakeClient([fake_tool_call("lookup", {"order_id": "1"})], repeat_last=True)
    result = AgentRunner(sol, client, max_turns=3).run("loop forever")
    assert result.stop_reason == "max_turns"
    assert len(client.calls) == 3
    assert len(calls) == 3
    assert any(e["type"] == "guardrail" for e in result.transcript["events"])


def test_unknown_tool_invalid_input_and_handler_error_become_is_error_results():
    sol, _ = _solution()
    client = FakeClient([
        fake_tool_calls([("nope", {}), ("lookup", {}), ("lookup", {"order_id": 5}), ("boom", {"x": "y"})]),
        fake_text("sorry"),
    ])
    result = AgentRunner(sol, client).run("x")
    results = client.calls[1]["messages"][-1]["content"]
    assert all(r.get("is_error") for r in results)
    texts = [json.loads(r["content"]) for r in results]
    assert "unknown tool" in texts[0]["error"]
    assert "missing required field 'order_id'" in texts[1]["details"]
    assert "should be string" in texts[2]["details"][0]
    assert texts[3]["error"] == "RuntimeError"
    assert [c["status"] for c in result.tool_calls] == ["error"] * 4


def test_refusal_stops_without_tools():
    sol, calls = _solution()
    client = FakeClient([FakeResponse(content=[], stop_reason="refusal")])
    result = AgentRunner(sol, client).run("x")
    assert result.stop_reason == "refusal" and calls == []


def test_transcript_written_and_redacted(tmp_path):
    sol, _ = _solution()
    client = FakeClient([fake_tool_call("lookup", {"order_id": "1"}),
                         fake_text("Emailed a.person@example.com and texted +61 412 345 678.")])
    result = AgentRunner(sol, client, transcript_dir=tmp_path).run("hi, I am a.person@example.com")
    data = json.loads(open(result.transcript_path).read())
    blob = json.dumps(data)
    assert "a.person@example.com" not in blob
    assert "412 345 678" not in blob
    assert "[REDACTED" in blob
    assert data["solution"] == "test" and data["stop_reason"] == "end_turn"
    # the model-facing conversation is NOT redacted
    assert "a.person@example.com" in json.dumps(result.messages)


def test_server_fallbacks_use_beta_channel_but_not_for_haiku():
    sol, _ = _solution()
    client = FakeClient([fake_text("hi")])
    AgentRunner(sol, client, use_server_fallbacks=True).run("x")
    assert client.calls[0]["channel"] == "beta"
    assert client.calls[0]["fallbacks"] == "default"
    assert client.calls[0]["model"] == "claude-sonnet-5-5"
    client = FakeClient([fake_text("hi")])
    AgentRunner(sol, client, model="claude-haiku-5-5", use_server_fallbacks=True).run("x")
    assert client.calls[0]["channel"] == "standard" and "fallbacks" not in client.calls[0]


def test_context_appended_to_system_prompt():
    sol, _ = _solution()
    client = FakeClient([fake_text("hi")])
    AgentRunner(sol, client).run("x", context={"business_id": "b1"})
    assert '"business_id": "b1"' in client.calls[0]["system"]


def test_make_client_requires_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        make_client()


def test_sdk_style_blocks_are_normalised():
    """Blocks with model_dump (like SDK objects) are converted to dicts."""

    class Block:
        def __init__(self, **kw):
            self.__dict__.update(kw)

        def model_dump(self, mode="json", exclude_none=True):
            return {k: v for k, v in self.__dict__.items() if v is not None}

    class Resp:
        def __init__(self, content, stop_reason):
            self.content, self.stop_reason, self.usage = content, stop_reason, None

    sol, calls = _solution()
    client = FakeClient([])
    responses = [Resp([Block(type="thinking", thinking="", signature="sig"),
                       Block(type="tool_use", id="t1", name="lookup", input={"order_id": "9"})], "tool_use"),
                 Resp([Block(type="text", text="ok", citations=None)], "end_turn")]
    client._next = lambda channel, kwargs: (client.calls.append(kwargs), responses.pop(0))[1]
    result = AgentRunner(sol, client).run("x")
    assert result.final_text == "ok" and calls == ["9"]
    # thinking block is passed back unchanged in history
    assert result.messages[1]["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}
