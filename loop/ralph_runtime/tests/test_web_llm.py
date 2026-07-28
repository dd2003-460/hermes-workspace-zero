import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ralph_runtime import cli
from ralph_runtime.web_llm import WebLLMConfigurationError, run_web_llm_cross_check


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def _providers():
    return json.dumps([
        {
            "id": "reviewer-a",
            "endpoint": "https://reviewer-a.example/v1/chat/completions",
            "model": "reviewer-a-model",
            "api_key_env": "RALPH_TEST_KEY_A",
        },
        {
            "id": "reviewer-b",
            "endpoint": "https://reviewer-b.example/v1/chat/completions",
            "model": "reviewer-b-model",
            "api_key_env": "RALPH_TEST_KEY_B",
        },
    ])


def test_web_llm_cross_check_persists_two_provider_receipt(tmp_path: Path, monkeypatch):
    project = tmp_path / "web-llm-project"
    cli.prepare_project(project, task="验证一个写作主张")
    stage_dir = project / "loop-artifacts" / "stages" / "01" / "r1"
    request = stage_dir / "cross-check.json"
    request.write_text(
        json.dumps({"claim": "清楚区分隐喻和因果主张会提高科普可核验性。", "context": "写作审计"}, ensure_ascii=False),
        encoding="utf-8",
    )
    monkeypatch.setenv("RALPH_WEB_LLM_PROVIDERS_JSON", _providers())
    monkeypatch.setenv("RALPH_TEST_KEY_A", "test-a")
    monkeypatch.setenv("RALPH_TEST_KEY_B", "test-b")

    def fake_urlopen(request_obj, timeout):
        assert timeout > 0
        assert request_obj.get_header("Authorization") in {"Bearer test-a", "Bearer test-b"}
        return _Response({"choices": [{"message": {"content": "uncertain: need authoritative sources"}}]})

    monkeypatch.setattr("ralph_runtime.web_llm.urlopen", fake_urlopen)
    report = run_web_llm_cross_check(project, request.relative_to(project))

    assert report["ok"] is True
    assert report["successful_provider_ids"] == ["reviewer-a", "reviewer-b"]
    receipt = json.loads((project / report["receipt"]).read_text(encoding="utf-8"))
    assert receipt["note"].startswith("LLM replies are adversarial")
    assert {item["endpoint_host"] for item in receipt["responses"]} == {
        "reviewer-a.example",
        "reviewer-b.example",
    }


def test_web_llm_cross_check_refuses_unconfigured_or_single_provider(tmp_path: Path, monkeypatch):
    project = tmp_path / "no-web-llm-project"
    cli.prepare_project(project, task="验证一个主张")
    request = project / "loop-artifacts" / "stages" / "01" / "r1" / "cross-check.json"
    request.write_text('{"claim":"需要核验"}\n', encoding="utf-8")
    monkeypatch.delenv("RALPH_WEB_LLM_PROVIDERS_JSON", raising=False)

    with pytest.raises(WebLLMConfigurationError, match="至少配置两个"):
        run_web_llm_cross_check(project, request.relative_to(project))


def test_web_llm_cross_check_accepts_playwright_browser_receipts(tmp_path: Path, monkeypatch):
    project = tmp_path / "browser-web-llm-project"
    cli.prepare_project(project, task="验证一个主张")
    request = project / "loop-artifacts" / "stages" / "01" / "r1" / "cross-check.json"
    request.write_text('{"claim":"需要核验"}\n', encoding="utf-8")
    monkeypatch.setenv("RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON", json.dumps([
        {"id": "perplexity-review", "site": "perplexity"},
        {"id": "chatgpt-review", "site": "chatgpt"},
    ]))
    monkeypatch.delenv("RALPH_WEB_LLM_PROVIDERS_JSON", raising=False)

    def fake_run(command, **kwargs):
        payload = json.loads(kwargs["input"])
        assert command[0] == "node"
        assert payload["headless"] is False
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "response": f"uncertain from {payload['site']}",
            "page_url": payload["url"],
        }), stderr="")

    monkeypatch.setattr("ralph_runtime.web_llm.subprocess.run", fake_run)
    report = run_web_llm_cross_check(project, request.relative_to(project))

    assert report["successful_provider_ids"] == ["perplexity-review", "chatgpt-review"]
    receipt = json.loads((project / report["receipt"]).read_text(encoding="utf-8"))
    assert {item["transport"] for item in receipt["responses"]} == {"browser_playwright"}
