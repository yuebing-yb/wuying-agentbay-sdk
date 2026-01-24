import pytest


class _FakeLogger:
    def __init__(self):
        self.messages = []

    def opt(self, depth=0):
        return self

    def info(self, msg):
        self.messages.append(("info", msg))

    def debug(self, msg):
        self.messages.append(("debug", msg))

    def error(self, msg):
        self.messages.append(("error", msg))


@pytest.mark.unit
def test_log_api_response_with_details_failure_includes_key_fields_and_masks_response(monkeypatch):
    from agentbay._common import logger as ab_logger

    fake = _FakeLogger()
    monkeypatch.setattr(ab_logger, "log", fake)
    monkeypatch.setenv("AGENTBAY_LOG_FORMAT", "pretty")

    ab_logger._log_api_response_with_details(
        api_name="CallMcpTool(LinkUrl) Response",
        request_id="link-1",
        success=False,
        key_fields={"http_status": 502, "tool_name": "long_screenshot"},
        full_response='{"code":"BadGateway","message":"upstream","token":"tok_123456"}',
    )

    joined = "\n".join([m for _lvl, m in fake.messages])
    assert "❌ API Response Failed" in joined
    assert "CallMcpTool(LinkUrl) Response" in joined
    assert "RequestId=link-1" in joined
    assert "http_status=502" in joined
    assert "tool_name=long_screenshot" in joined
    assert "📥 Response:" in joined
    assert "tok_123456" not in joined
    assert "to****56" in joined

