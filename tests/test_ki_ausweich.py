"""Ausweich-KI (PCL_KI_AUSWEICH): scheitert z. B. die Claude-CLI (offline, Limit, Anmeldung), antwortet ein lokales Modell.
Dazu: claude.exe aus %USERPROFILE%\\.local\\bin wird unter Windows gefunden."""
import os

import pytest

from conftest import A, make_agent, make_project  # noqa: F401
import win_pfade


def _agent(provider="claude_cli"):
    pid = make_project()
    aid = make_agent(pid, "Chef", provider=provider)
    return A.q1("SELECT * FROM agents WHERE id=?", (aid,))


@pytest.fixture
def calls(monkeypatch):
    seen = []

    def fake(agent, messages, images=None):
        seen.append((agent["provider"], agent.get("model"), bool(images)))
        if agent["provider"] == "claude_cli":
            raise RuntimeError("Claude CLI is not signed in")
        return "lokal", 5
    monkeypatch.setattr(A, "_call_llm", fake)
    return seen


def test_ohne_einstellung_kein_ausweichen(calls, monkeypatch):
    monkeypatch.delenv("PCL_KI_AUSWEICH", raising=False)
    with pytest.raises(RuntimeError, match="not signed in"):
        A.call_llm(_agent(), [{"role": "user", "content": "hi"}])
    assert [c[0] for c in calls] == ["claude_cli"]


def test_claude_scheitert_ollama_antwortet(calls, monkeypatch):
    monkeypatch.setenv("PCL_KI_AUSWEICH", "ollama")
    monkeypatch.setenv("PCL_KI_AUSWEICH_MODEL", "qwen2.5:3b")
    a = _agent()
    assert A.call_llm(a, [{"role": "user", "content": "hi"}]) == ("lokal", 5)
    assert calls == [("claude_cli", "", False), ("ollama", "qwen2.5:3b", False)]
    ev = A.q1("SELECT * FROM audit WHERE event='ai_fallback' ORDER BY id DESC")
    assert ev and "claude_cli" in ev["detail"] and "ollama" in ev["detail"]


def test_test_knopf_weicht_nicht_aus(calls, monkeypatch):
    monkeypatch.setenv("PCL_KI_AUSWEICH", "ollama")
    with pytest.raises(RuntimeError):
        A.call_llm(_agent(), [{"role": "user", "content": "hi"}], ausweich=False)
    c = A.app.test_client()
    r = c.post("/api/providers/test", json={"provider": "claude_cli", "model": "sonnet"},
               headers={"Authorization": "Bearer " + os.environ.get("APP_TOKEN", "")})
    if r.status_code == 200:
        assert r.get_json()["ok"] is False


def test_ausweich_mit_bildern_dann_ohne(monkeypatch):
    monkeypatch.setenv("PCL_KI_AUSWEICH", "ollama")
    seen = []

    def fake(agent, messages, images=None):
        seen.append((agent["provider"], bool(images)))
        if agent["provider"] == "claude_cli" or images:
            raise RuntimeError("geht nicht")
        return "nur Text", 1
    monkeypatch.setattr(A, "_call_llm", fake)
    assert A.call_llm(_agent(), [{"role": "user", "content": "hi"}], [("image/png", "AAA")]) == ("nur Text", 1)
    assert seen == [("claude_cli", True), ("ollama", True), ("ollama", False)]


def test_beide_scheitern_klare_meldung(monkeypatch):
    monkeypatch.setenv("PCL_KI_AUSWEICH", "ollama")
    monkeypatch.setattr(A, "_call_llm", lambda a, m, i=None: (_ for _ in ()).throw(RuntimeError(a["provider"] + " kaputt")))
    with pytest.raises(RuntimeError, match="claude_cli kaputt.*fallback ollama also failed: ollama kaputt"):
        A.call_llm(_agent(), [{"role": "user", "content": "hi"}])


def test_kein_ausweichen_auf_sich_selbst_oder_ohne_ki(monkeypatch):
    monkeypatch.setenv("PCL_KI_AUSWEICH", "ollama")
    assert A.ausweich_agent({"provider": "ollama"}) is None
    assert A.ausweich_agent({"provider": ""}) is None
    monkeypatch.setenv("PCL_KI_AUSWEICH", "gibtsnicht")
    assert A.ausweich_agent({"provider": "claude_cli"}) is None


def test_claude_in_local_bin_wird_gefunden(tmp_path):
    lb = tmp_path / "home" / ".local" / "bin"
    lb.mkdir(parents=True)
    (lb / "claude.exe").write_text("")
    env = {"PATH": "x", "USERPROFILE": str(tmp_path / "home")}
    neu = win_pfade.erweitern(env, windows=True, here=tmp_path, registry=False)
    assert str(lb) in neu and str(lb) in env["PATH"]
