"""Firmen-Kooperation: oberster Chef lagert Teile eines Auftrags an eine andere Firma aus (Wunsch ABI 2026-11-12)."""
import json
import app as A
from conftest import drain, make_agent, make_project, make_task, task


def _zwei_firmen():
    pa, pb = make_project("Agentur"), make_project("Druckerei")
    ceo = make_agent(pa, "CEO", delegate=True, judge=True)
    make_agent(pa, "Helfer", parent=ceo)
    leiter = make_agent(pb, "Leiter", delegate=True, judge=True)
    make_agent(pb, "Macher", parent=leiter, write_files=True)
    return pa, pb, ceo, leiter


def test_auslagern_hin_und_zurueck():
    pa, pb, ceo, leiter = _zwei_firmen()
    A.proj_dir(pa).mkdir(parents=True, exist_ok=True)
    (A.proj_dir(pa) / "brief.txt").write_text("Bitte blau", encoding="utf-8")
    tid = make_task(pa, ceo, "Flyer drucken OUTSOURCE TO Druckerei SEND FILE brief.txt")
    drain()
    t = task(tid)
    assert t["status"] == "done" and t["inbox"] == "new"
    kids = A.q("SELECT * FROM tasks WHERE parent_task_id=?", (tid,))
    assert len(kids) == 1 and kids[0]["project_id"] == pb and kids[0]["agent_id"] == leiter
    assert kids[0]["title"].startswith("[Agentur]") and kids[0]["status"] == "done"
    # Datei ging hin ...
    sent = A.proj_dir(pb) / "input" / "from-Agentur" / f"task-{kids[0]['id']}" / "brief.txt"
    assert sent.read_text(encoding="utf-8") == "Bitte blau"
    assert f"input/from-Agentur/task-{kids[0]['id']}/brief.txt" in kids[0]["description"]
    # ... und das Ergebnis kam zurueck
    back = A.proj_dir(pa) / "partner" / "Druckerei" / f"task-{kids[0]['id']}" / "macher_note.txt"
    assert back.is_file()
    assert "Delivered by the partner firm Druckerei" in kids[0]["result"]
    # Druckerei bekommt keine eigene Post, Partnerschaft wird sichtbar
    assert kids[0]["inbox"] in ("", None)
    assert A.q1("SELECT note FROM firm_links WHERE a=? AND b=?", (min(pa, pb), max(pa, pb)))["note"] == "outsourcing"
    assert A.q1("SELECT 1 FROM audit WHERE event='outsourced'") and A.q1("SELECT 1 FROM audit WHERE event='outsourced_back'")
    # Bericht des Chefs nennt die Partnerfirma
    up = A.review_prompt(t, [task(kids[0]["id"])])
    assert "partner firm Druckerei" in up


def test_firmenverzeichnis_nur_fuer_obersten_chef():
    pa, pb, ceo, leiter = _zwei_firmen()
    a, p = A.q1("SELECT * FROM agents WHERE id=?", (ceo,)), A.q1("SELECT * FROM projects WHERE id=?", (pa,))
    block = A.firms_block(a, p)
    assert "Druckerei" in block and "Leiter" in block and "Agentur" not in block
    assert "mock" not in block  # keine Anbieter/Rechte der anderen Firma
    sys = A.build_system(a, p, "plan", firms=block)
    assert '"outsource"' in sys and "PARTNER FIRMS" in sys
    assert '"outsource"' not in A.build_system(a, p, "plan")
    helfer = A.q1("SELECT * FROM agents WHERE name='Helfer'")
    assert not A.can_outsource(helfer, p) and A.can_outsource(a, p)


def test_annehmen_und_auslagern_abschaltbar(client):
    pa, pb, ceo, leiter = _zwei_firmen()
    assert client.get(f"/api/projects/{pb}/coop").json == {"send": True, "accept": True}
    assert client.put(f"/api/projects/{pb}/coop", json={"accept": False}, headers={"X-PCL": "1"}).json["accept"] is False
    assert A.partner_firms(pa) == []
    assert client.get("/api/firms").json["firms"][1]["coop"]["accept"] is False
    tid = make_task(pa, ceo, "Flyer OUTSOURCE TO Druckerei")
    drain()
    assert not A.q1("SELECT 1 FROM tasks WHERE project_id=?", (pb,))
    assert task(tid)["status"] == "done"
    client.put(f"/api/projects/{pb}/coop", json={"accept": True}, headers={"X-PCL": "1"})
    client.put(f"/api/projects/{pa}/coop", json={"send": False}, headers={"X-PCL": "1"})
    assert not A.can_outsource(A.q1("SELECT * FROM agents WHERE id=?", (ceo,)), A.q1("SELECT * FROM projects WHERE id=?", (pa,)))
    assert client.put("/api/projects/9999/coop", json={}, headers={"X-PCL": "1"}).status_code == 404


def test_keine_ringe_und_unbekannte_firma():
    pa, pb, ceo, leiter = _zwei_firmen()
    parent = make_task(pa, ceo, "oben", status="waiting_subtasks")
    child = A.ex("INSERT INTO tasks(project_id,agent_id,parent_task_id,title,status,created,updated) VALUES(?,?,?,?,?,0,0)",
                 (pb, leiter, parent, "unten", "running"))
    t = task(child)
    assert A.project_chain(t) == {pa, pb}
    assert A.partner_firms(pb, A.project_chain(t)) == []  # zurueck an die Agentur geht nicht
    notes = []
    assert A.resolve_outsourcing([{"firm": "Gibtsnicht", "title": "x"}], task(parent), notes) == [] and "Unknown partner firm" in notes[0]


def test_top_task_endet_an_der_firmengrenze():
    pa, pb, ceo, leiter = _zwei_firmen()
    parent = make_task(pa, ceo, "oben", status="waiting_subtasks")
    child = A.ex("INSERT INTO tasks(project_id,agent_id,parent_task_id,title,status,created,updated) VALUES(?,?,?,?,?,0,0)",
                 (pb, leiter, parent, "unten", "running"))
    assert A.top_task(task(child))["id"] == child


def test_planfreigabe_gilt_auch_fuers_auslagern(client):
    pa, pb, ceo, leiter = _zwei_firmen()
    A.set_setting(f"gates:{pa}", json.dumps({"plan": True}))
    tid = make_task(pa, ceo, "Flyer OUTSOURCE TO Druckerei")
    drain()
    assert task(tid)["status"] == "waiting_approval"
    ap = A.q1("SELECT * FROM approvals WHERE task_id=? AND kind='plan'", (tid,))
    assert "partner firm Druckerei" in ap["payload"] and json.loads(ap["data"])[0]["firm_id"] == pb
    assert not A.q1("SELECT 1 FROM tasks WHERE project_id=?", (pb,))
    A.decide_gate(ap, True)
    assert task(tid)["status"] == "waiting_subtasks"
    assert A.q1("SELECT 1 FROM tasks WHERE project_id=? AND parent_task_id=?", (pb, tid))


def test_firma_loeschen_waehrend_auftrag_laeuft(client):
    pa, pb, ceo, leiter = _zwei_firmen()
    parent = make_task(pa, ceo, "oben", status="waiting_subtasks")
    A.ex("INSERT INTO tasks(project_id,agent_id,parent_task_id,title,status,created,updated) VALUES(?,?,?,?,?,0,0)",
         (pb, leiter, parent, "unten", "queued"))
    client.delete(f"/api/projects/{pb}", headers={"X-PCL": "1"})
    assert task(parent)["status"] == "queued"  # Auftraggeber macht weiter
    # umgekehrt: Auftraggeber geloescht -> Auftrag wird in der Partnerfirma ein eigener oberster Auftrag
    pc = make_project("Dritte")
    leiter2 = make_agent(pc, "L2", delegate=True)
    p2 = make_task(pa, ceo, "oben2", status="waiting_subtasks")
    c2 = A.ex("INSERT INTO tasks(project_id,agent_id,parent_task_id,title,status,created,updated) VALUES(?,?,?,?,?,0,0)",
              (pc, leiter2, p2, "unten2", "queued"))
    client.delete(f"/api/projects/{pa}", headers={"X-PCL": "1"})
    assert task(c2)["parent_task_id"] is None


def test_auftraggeber_gibt_zur_ueberarbeitung_zurueck():
    pa, pb, ceo, leiter = _zwei_firmen()
    tid = make_task(pa, ceo, "Flyer REVISE OUTSOURCE TO Druckerei")
    drain()
    kid = A.q1("SELECT * FROM tasks WHERE parent_task_id=?", (tid,))
    assert kid["project_id"] == pb and kid["rounds"] == 1 and kid["status"] == "done"
    assert "Revised" in kid["result"] and task(tid)["status"] == "done"
    assert A.q1("SELECT COUNT(*) c FROM audit WHERE event='outsourced_back'")["c"] == 2
