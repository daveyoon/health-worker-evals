"""Minimal model clients (stdlib only). A model spec is "provider:model",
e.g. "anthropic:claude-opus-5-5", "openai:gpt-5", "google:gemini-2.5-pro".
"mock:good" and "mock:bad" exist for offline pipeline tests."""
import json
import os
import time
import urllib.error
import urllib.request


def _post(url, headers, body, retries=4):
    data = json.dumps(body).encode()
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"{url} -> {e.code}: {e.read().decode()[:500]}") from e


def _key(name):
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"set {name} to call this provider")
    return v


def anthropic(model, system, prompt, max_tokens):
    r = _post("https://api.anthropic.com/v1/messages",
              {"x-api-key": _key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"},
              {"model": model, "max_tokens": max_tokens, "system": system,
               "messages": [{"role": "user", "content": prompt}]})
    return "".join(b.get("text", "") for b in r["content"] if b["type"] == "text")


def openai(model, system, prompt, max_tokens):
    r = _post("https://api.openai.com/v1/chat/completions",
              {"authorization": f"Bearer {_key('OPENAI_API_KEY')}"},
              {"model": model, "max_completion_tokens": max_tokens,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]})
    return r["choices"][0]["message"]["content"] or ""


def google(model, system, prompt, max_tokens):
    r = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
              {"x-goog-api-key": _key("GEMINI_API_KEY")},
              {"systemInstruction": {"parts": [{"text": system}]},
               "contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"maxOutputTokens": max_tokens}})
    parts = r["candidates"][0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts)


def mock(model, system, prompt, max_tokens):
    # Deterministic stand-ins so the whole pipeline can be tested without keys.
    if model == "bad":
        return "Give nifedipine under the tongue and continue all current medicines. No need to refer."
    return "MOCK_GOOD"


PROVIDERS = {"anthropic": anthropic, "openai": openai, "google": google, "mock": mock}


def complete(spec, system, prompt, max_tokens=1500):
    provider, _, model = spec.partition(":")
    if provider not in PROVIDERS:
        raise ValueError(f"unknown provider in {spec!r}; expected one of {sorted(PROVIDERS)}")
    return PROVIDERS[provider](model, system, prompt, max_tokens)
