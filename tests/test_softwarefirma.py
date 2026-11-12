"""Firmenvorlage 'softwarefirma' (Steadforge Labs, entwickelt Hyperstead selbst) und Freigaberegel fuer Veroeffentlichungen."""
import json
import app as A
import company_templates as CT
import werkstatt as W


def test_vorlage_softwarefirma_anlegen(client):
    assert any(t["key"] == "softwarefirma" for t in client.get("/api/templates").json)
    r = client.post("/api/projects/from_template", json={"template": "softwarefirma", "name": "Steadforge Labs", "provider": "mock"})
    assert r.status_code == 200
    pid = r.json["id"]
    ags = {a["role"]: a for a in A.q("SELECT * FROM agents WHERE project_id=? ORDER BY id", (pid,))}
    ceo = ags["CEO"]
    assert ceo["parent_id"] is None
    pc = json.loads(ceo["perms"])
    assert pc["recruit"] and pc["delegate"] and pc["judge"] and pc["werkstatt"]
    assert not pc["upload"] and not pc["publish"] and not pc["shell"]  # veroeffentlicht nie an der Freigabe vorbei
    cto = next(a for r_, a in ags.items() if r_.startswith("CTO"))
    assert cto["parent_id"] == ceo["id"] and json.loads(cto["perms"])["code"]
    qa = next(a for r_, a in ags.items() if r_.startswith("Quality"))
    assert qa["parent_id"] == ceo["id"]  # QA prueft unabhaengig von der Entwicklung
    for a in ags.values():
        assert a["provider"] == "mock"  # Vorlage startet mit KI, nicht 'unassigned'
    assert CT.RELEASE_RULE in ceo["system_prompt"] and CT.RELEASE_RULE in cto["system_prompt"]


def test_freigaberegel_inhalt():
    for w in ("Push, merge, release", "explicitly approved", "branch + commit", "tests run", "risks", "verified", "credentials"):
        assert w in CT.RELEASE_RULE, w


def test_push_vom_cli_agenten_gesperrt():
    """Claude-CLI mit Werkstatt Stufe 2: Push/Merge/Release stehen in --disallowedTools."""
    pid = A.ex("INSERT INTO projects(name,goal,created) VALUES('S','',0)")
    perms = dict(A.DEFAULT_PERMS, werkstatt=True, werkstatt_stufe=2)
    aid = A.ex("INSERT INTO agents(project_id,name,role,provider,model,system_prompt,perms,created) VALUES(?,?,?,?,?,?,?,0)",
               (pid, "CTO", "CTO", "claude_cli", "", "", json.dumps(perms)))
    a = A.q1("SELECT * FROM agents WHERE id=?", (aid,))
    import os
    os.environ["PCL_ALLOW_WERKSTATT"] = "1"
    try:
        out = A.werkstatt_cli_args(a, ["claude", "-p", "--tools", ""])
    finally:
        os.environ.pop("PCL_ALLOW_WERKSTATT", None)
    deny = out[0][out[0].index("--disallowedTools") + 1]
    for c in ("git push", "gh pr merge", "gh release", "gh api"):
        assert f"Bash({c} *)" in deny, c
    assert W.classify("git push origin main", "/tmp/x")[0] == "antrag"
