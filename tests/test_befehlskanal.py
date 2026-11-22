"""Zweiter Telegram-Kanal fuer Befehle, die der Besitzer selbst ausfuehren muss (Wunsch ABI 2026-11-22)."""
import queue

import app as A


def _drain(q):
    out = []
    while not q.empty():
        out.append(q.get_nowait())
    return out


def _tg(monkeypatch, cmd_chats=()):
    q = queue.Queue()
    monkeypatch.setattr(A, "_tg_out", q)
    monkeypatch.setattr(A, "TG_TOKEN", "x")
    monkeypatch.setattr(A, "TG_CHATS", {"111"})
    monkeypatch.setattr(A, "TG_CMD_CHATS", set(cmd_chats))
    return q


def test_owner_commands_block():
    assert A.owner_commands_block(None) == "" and A.owner_commands_block([]) == ""
    b = A.owner_commands_block(["git pull", {"cmd": "sudo systemctl restart hyperstead", "why": "restart on the Pi"}, {"cmd": " "}])
    assert "COMMANDS FOR THE OWNER" in b
    assert "```shell\ngit pull\n```" in b
    assert "# restart on the Pi\nsudo systemctl restart hyperstead" in b
    assert A.extract_commands(b) == ["git pull", "# restart on the Pi\nsudo systemctl restart hyperstead"]


def test_extract_nur_shell_bloecke():
    text = "Hi\n```python\nprint(1)\n```\n```bash\nls -la\n```\n```powershell\nGet-Item .\n```\n```\nplain\n```\n```bash\nls -la\n```"
    assert A.extract_commands(text) == ["ls -la", "Get-Item ."]


def test_eigener_kanal(monkeypatch):
    q = _tg(monkeypatch, {"222"})
    n = A.tg_notify_commands(5, "Done.\n```bash\necho '<a>' && cd ~/x\n```", "Setup")
    msgs = _drain(q)
    assert n == 1 and len(msgs) == 1
    chat, text, _, _, translate, as_html = msgs[0]
    assert chat == "222" and as_html and not translate
    assert "⌨️ COMMAND for you · #5" in text and "<pre>echo &#x27;&lt;a&gt;&#x27; &amp;&amp; cd ~/x</pre>" in text


def test_ohne_zweiten_kanal_gleicher_chat(monkeypatch):
    q = _tg(monkeypatch)
    A.tg_notify_commands(7, "```sh\na\n```\n```sh\nb\n```")
    msgs = _drain(q)
    assert [m[0] for m in msgs] == ["111", "111"]
    assert "1/2" in msgs[0][1] and "2/2" in msgs[1][1]


def test_ohne_telegram_nichts(monkeypatch):
    q = queue.Queue()
    monkeypatch.setattr(A, "_tg_out", q)
    monkeypatch.setattr(A, "TG_TOKEN", "")
    assert A.tg_notify_commands(1, "```bash\nls\n```") == 0 and q.empty()


def test_post_schickt_info_und_befehle(monkeypatch):
    from conftest import make_project, make_agent
    q = _tg(monkeypatch, {"222"})
    pid = make_project()
    aid = make_agent(pid, "CEO")
    tid = A.ex("INSERT INTO tasks(project_id,agent_id,title,description,status,result,created) VALUES(?,?,?,?,?,?,0)",
               (pid, aid, "Install", "", "done", "Report.\n```bash\npip install x\n```"))
    A.tg_notify_post(tid)
    msgs = _drain(q)
    assert msgs[0][0] == "111" and "Report." in msgs[0][1] and not msgs[0][5]  # Info wie bisher
    assert msgs[1][0] == "222" and "<pre>pip install x</pre>" in msgs[1][1]
    A.tg_notify_post(tid, chats=["111"])  # /post zeigt nur erneut, ohne Befehle
    assert len(_drain(q)) == 1


def test_prompt_nennt_owner_commands():
    from conftest import make_project, make_agent
    pid = make_project()
    a = A.q1("SELECT * FROM agents WHERE id=?", (make_agent(pid, "CEO"),))
    p = A.q1("SELECT * FROM projects WHERE id=?", (pid,))
    assert "owner_commands" in A.build_system(a, p, "work")
    assert "owner_commands" not in A.build_system(a, p, "recruit")
