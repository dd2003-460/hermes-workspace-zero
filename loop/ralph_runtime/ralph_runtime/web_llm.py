"""Auditable cross-checks through configured web-LLM APIs or browser UIs.

Claude Code's WebSearch can find public evidence, but it cannot submit a
question to an authenticated ChatGPT/Claude/Gemini web page.  This module
provides the missing, explicit boundary: configured OpenAI-compatible HTTPS
endpoints and configured Playwright browser profiles both produce durable
receipts.  Browser profiles type the same bounded question into a real web UI;
they never read browser cookies or credentials.  A model answer remains a
*review signal*, never primary factual evidence; callers still need independent
authoritative sources.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .result_artifacts import state_stage_artifact_dir
from .state import load_state


class WebLLMConfigurationError(ValueError):
    """The project requested a web-LLM check without usable provider config."""


_BROWSER_SITES = {
    "perplexity": "https://www.perplexity.ai/",
    "chatgpt": "https://chatgpt.com/",
    "gemini": "https://gemini.google.com/app",
}


def _bounded_text(value: Any, limit: int) -> str:
    text = str(value or "").replace("\x00", " ").strip()
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 80)] + "\n[… truncated by RALPH web-LLM boundary …]"


def configured_providers(raw: str | None = None) -> list[dict[str, str]]:
    """Read sanitized OpenAI-compatible provider settings from the environment.

    ``RALPH_WEB_LLM_PROVIDERS_JSON`` is a JSON array.  Each item requires
    ``id``, ``endpoint``, ``model`` and ``api_key_env``.  API values themselves
    are never placed in the JSON, events or receipts.
    """

    payload = raw if raw is not None else os.environ.get("RALPH_WEB_LLM_PROVIDERS_JSON", "")
    if not payload.strip():
        return []
    try:
        items = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise WebLLMConfigurationError("RALPH_WEB_LLM_PROVIDERS_JSON 必须是 JSON 数组") from exc
    if not isinstance(items, list):
        raise WebLLMConfigurationError("RALPH_WEB_LLM_PROVIDERS_JSON 必须是 JSON 数组")

    providers: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, Mapping):
            raise WebLLMConfigurationError(f"provider[{index}] 必须是对象")
        provider_id = str(raw_item.get("id", "")).strip()
        endpoint = str(raw_item.get("endpoint", "")).strip()
        model = str(raw_item.get("model", "")).strip()
        api_key_env = str(raw_item.get("api_key_env", "")).strip()
        parsed = urlparse(endpoint)
        if not provider_id or not model or not api_key_env:
            raise WebLLMConfigurationError(
                f"provider[{index}] 需要 id、model 和 api_key_env"
            )
        if provider_id in seen:
            raise WebLLMConfigurationError(f"provider id 重复：{provider_id}")
        if parsed.scheme != "https" or not parsed.netloc:
            raise WebLLMConfigurationError(
                f"provider[{index}] endpoint 必须是 HTTPS URL；拒绝本地/明文端点"
            )
        seen.add(provider_id)
        providers.append(
            {
                "id": provider_id,
                "endpoint": endpoint,
                "model": model,
                "api_key_env": api_key_env,
                "endpoint_host": parsed.netloc,
            }
        )
    return providers


def configured_browser_providers(raw: str | None = None) -> list[dict[str, str]]:
    """Read browser-UI providers that the local Playwright runner may use.

    ``RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON`` is a JSON array containing
    ``id`` and ``site``.  ``site`` is deliberately a small allowlist of public
    LLM web applications, with an optional HTTPS ``url`` override for a
    user-authorized compatible deployment.  Credentials and browser storage
    are never part of this configuration or a persisted receipt.
    """

    payload = raw if raw is not None else os.environ.get("RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON", "")
    if not payload.strip():
        return []
    try:
        items = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise WebLLMConfigurationError("RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON 必须是 JSON 数组") from exc
    if not isinstance(items, list):
        raise WebLLMConfigurationError("RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON 必须是 JSON 数组")

    providers: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, Mapping):
            raise WebLLMConfigurationError(f"browser provider[{index}] 必须是对象")
        provider_id = str(raw_item.get("id", "")).strip()
        site = str(raw_item.get("site", "")).strip().lower()
        if not provider_id or not site:
            raise WebLLMConfigurationError(f"browser provider[{index}] 需要 id 和 site")
        if site not in _BROWSER_SITES:
            raise WebLLMConfigurationError(
                f"browser provider[{index}] site 必须是：{', '.join(sorted(_BROWSER_SITES))}"
            )
        if provider_id in seen:
            raise WebLLMConfigurationError(f"browser provider id 重复：{provider_id}")
        url = str(raw_item.get("url") or _BROWSER_SITES[site]).strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise WebLLMConfigurationError(
                f"browser provider[{index}] url 必须是 HTTPS URL；拒绝本地/明文端点"
            )
        seen.add(provider_id)
        providers.append(
            {
                "id": provider_id,
                "site": site,
                "url": url,
                "endpoint_host": parsed.netloc,
                "model": f"{site} web UI",
            }
        )
    return providers


def _all_providers() -> list[dict[str, str]]:
    providers = [*configured_providers(), *configured_browser_providers()]
    ids = [provider["id"] for provider in providers]
    if len(set(ids)) != len(ids):
        raise WebLLMConfigurationError("API provider 与 browser provider 的 id 不能重复")
    return providers


def web_llm_crosscheck_enabled() -> bool:
    """Whether the runtime can honestly require actual web-LLM receipts."""

    try:
        return len(_all_providers()) >= 2
    except WebLLMConfigurationError:
        return False


def _response_text(payload: Mapping[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
        raise ValueError("provider response has no choices[0]")
    message = choices[0].get("message")
    if not isinstance(message, Mapping):
        raise ValueError("provider response has no choices[0].message")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("provider response has empty choices[0].message.content")
    return _bounded_text(content, 8000)


def _review_prompt(claim: str, context: str) -> str:
    return (
        "Independently review the following claim. Give one verdict: supported, contradicted, or uncertain. "
        "State the decisive reason, distinguish factual evidence from inference, and do not invent citations. "
        "Your answer is an adversarial review signal, not an authoritative source.\n\n"
        f"Claim:\n{claim}\n\nContext:\n{context or '(none)'}"
    )


def _ask_provider(provider: Mapping[str, str], claim: str, context: str, timeout: float) -> dict[str, Any]:
    key = os.environ.get(provider["api_key_env"], "").strip()
    receipt = {
        "provider_id": provider["id"],
        "model": provider["model"],
        "endpoint_host": provider["endpoint_host"],
        "status": "error",
    }
    if not key:
        receipt["error"] = f"missing credential environment variable: {provider['api_key_env']}"
        return receipt
    prompt = _review_prompt(claim, context)
    body = json.dumps(
        {
            "model": provider["model"],
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful cross-validation reviewer. Never fabricate evidence or URLs.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        provider["endpoint"],
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - endpoint is HTTPS-validated config
            raw = response.read().decode("utf-8")
        text = _response_text(json.loads(raw))
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        receipt["error"] = _bounded_text(exc, 500)
        return receipt
    receipt.update(
        {
            "status": "ok",
            "response": text,
            "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
    )
    return receipt


def _browser_runner_path() -> Path:
    return Path(__file__).with_name("web_llm_browser_runner.mjs")


def _ask_browser_provider(provider: Mapping[str, str], claim: str, context: str, timeout: float) -> dict[str, Any]:
    """Ask a browser-UI provider through the local Playwright runner.

    The runner receives only the bounded review prompt and provider URL.  It
    starts a fresh context, which intentionally prevents silent reuse or
    extraction of a user's authenticated browser profile.
    """

    receipt: dict[str, Any] = {
        "provider_id": provider["id"],
        "model": provider["model"],
        "endpoint_host": provider["endpoint_host"],
        "transport": "browser_playwright",
        "status": "error",
    }
    runner = _browser_runner_path()
    if not runner.is_file():
        receipt["error"] = f"browser runner missing: {runner.name}"
        return receipt
    payload = {
        "site": provider["site"],
        "url": provider["url"],
        "prompt": _review_prompt(claim, context),
        "headless": os.environ.get("RALPH_WEB_LLM_BROWSER_HEADLESS", "0").strip().lower()
        in {"1", "true", "yes"},
        "timeout_ms": int(timeout * 1000),
    }
    try:
        completed = subprocess.run(
            ["node", str(runner)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout + 15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        receipt["error"] = _bounded_text(exc, 500)
        return receipt
    if completed.returncode != 0:
        receipt["error"] = _bounded_text(completed.stderr or completed.stdout or "browser runner failed", 500)
        return receipt
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        receipt["error"] = _bounded_text(f"browser runner returned invalid JSON: {exc}", 500)
        return receipt
    if not isinstance(result, Mapping) or not isinstance(result.get("response"), str) or not result["response"].strip():
        receipt["error"] = _bounded_text(
            result.get("error") if isinstance(result, Mapping) else "browser runner returned no response",
            500,
        )
        return receipt
    text = _bounded_text(result["response"], 8000)
    receipt.update(
        {
            "status": "ok",
            "response": text,
            "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "page_url": _bounded_text(result.get("page_url"), 500),
        }
    )
    return receipt


def _timeout_seconds() -> float:
    try:
        return min(120.0, max(5.0, float(os.environ.get("RALPH_WEB_LLM_TIMEOUT_SECONDS", "45"))))
    except ValueError:
        return 45.0


def run_web_llm_cross_check(project: str | Path, request_file: str | Path) -> dict[str, Any]:
    """Ask configured independent providers and persist a durable receipt."""

    root = Path(project).expanduser().resolve()
    state = load_state(root / "loop-state.json")
    stage_dir = state_stage_artifact_dir(root, state).resolve()
    path = Path(request_file).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if stage_dir not in path.parents:
        raise ValueError(
            f"web-LLM 请求必须位于当前阶段目录 `{stage_dir.relative_to(root)}` 中"
        )
    try:
        request_data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"web-LLM 请求 JSON 语法错误：{exc.msg}") from exc
    if not isinstance(request_data, Mapping):
        raise ValueError("web-LLM 请求必须是对象")
    field = request_data.get("field") if isinstance(request_data.get("field"), Mapping) else {}
    # A field worker is only permitted to mutate its single task JSON.  Accept
    # that task file directly so it does not need to create a second writable
    # request artifact before asking the configured reviewers.
    claim = _bounded_text(request_data.get("claim") or field.get("attribute") or field.get("concept"), 4000)
    context = _bounded_text(request_data.get("context") or field.get("rationale"), 6000)
    if not claim:
        raise ValueError("web-LLM 请求需要非空 claim")
    providers = _all_providers()
    requested = request_data.get("providers")
    if requested is not None:
        if not isinstance(requested, list) or not all(isinstance(item, str) and item.strip() for item in requested):
            raise ValueError("providers 必须是 provider id 数组")
        wanted = {item.strip() for item in requested}
        providers = [provider for provider in providers if provider["id"] in wanted]
    if len(providers) < 2:
        raise WebLLMConfigurationError(
            "至少配置两个独立 web-LLM provider 才能执行交叉核验；"
            "设置 RALPH_WEB_LLM_PROVIDERS_JSON（API）或 "
            "RALPH_WEB_LLM_BROWSER_PROVIDERS_JSON（受控 Playwright 网页 UI）。"
        )

    responses = [
        (
            _ask_browser_provider(provider, claim, context, _timeout_seconds())
            if provider.get("site")
            else _ask_provider(provider, claim, context, _timeout_seconds())
        )
        for provider in providers
    ]
    now = datetime.now(timezone.utc).isoformat()
    receipt = {
        "schema_version": 1,
        "kind": "ralph_web_llm_cross_check",
        "created_at": now,
        "request_ref": str(path.relative_to(root)),
        "claim": claim,
        "claim_sha256": hashlib.sha256(claim.encode("utf-8")).hexdigest(),
        "context_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
        "responses": responses,
        "successful_provider_ids": [item["provider_id"] for item in responses if item.get("status") == "ok"],
        "note": "LLM replies are adversarial review signals, not authoritative factual sources.",
    }
    output_dir = stage_dir / "web-llm"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{receipt['claim_sha256'][:16]}.json"
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {
        "ok": True,
        "receipt": str(output.relative_to(root)),
        "successful_provider_ids": receipt["successful_provider_ids"],
        "failed_provider_ids": [item["provider_id"] for item in responses if item.get("status") != "ok"],
        "requires_authoritative_sources": True,
    }
