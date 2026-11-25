"""Jede Umgebungsvariable, die der Code liest, steht in .env.example (Wunsch ABI 2026-11-22: .env.example aktuell halten).

Neue Variable -> Zeile mit Kommentar und sicherem Platzhalter in .env.example (im Cloud-Repo auch deploy/cloud/env.example),
oder, wenn nur intern/von Programmen gesetzt, in INTERN unten eintragen.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Liest os.environ.get("X"), os.getenv("X"), os.environ["X"], _env("X"), T._env("X"), _env_secs("X")
READ = re.compile(r"""(?:environ\.get|getenv|\b_env|_env_secs)\(\s*["']([A-Z][A-Z0-9_]{2,})["']|environ\[\s*["']([A-Z][A-Z0-9_]{2,})["']\s*\]""")

# Werte, die kein Besitzer eintraegt: vom System, von Hyperstead selbst an Unterprozesse/Instanzen gesetzt, oder nur fuer Tests.
INTERN = {
    "COMSPEC", "WINDIR", "CARGO_HOME", "CODEX_HOME",                       # Betriebssystem / Werkzeuge
    "HYPERSTEAD_SELFTEST_REEXEC", "HYPERSTEAD_VORAUS_REEXEC",             # Neustart im venv
    "PCL_PROMPT", "PCL_OUTPUT", "PCL_STORAGE",                            # an Makro-Skripte uebergeben
    "TELEGRAM_API",                                                       # nur Tests (Fake-Server)
    # vom Verwalter/Portal bzw. Dockerfile fuer Kunden-Instanzen gesetzt (Cloud-Repo)
    "PCL_LABEL", "PCL_PORTAL_URL", "PCL_PORTAL_PUBLIC", "PCL_PROXY_HOST", "PCL_FIRM_LIMIT", "PCL_SESSION_FILE",
    "PCL_CLOUD", "PORTAL_DB", "VERWALTER", "VERWALTER_URL", "DOCKER_SOCKET", "PCL_PORTAL_CONTAINER", "PCL_PROXY_CONTAINER",
    "PCL_OWNER_USER", "PCL_OWNER_EMAIL", "PCL_OWNER_PWHASH",
    # API-Schluessel, die der Kunde im Cloud-Modus unter 🔑 API keys eintraegt (schluessel.py)
    "GITHUB_DEV_TOKEN", "GITHUB_DEV_REPO",
}


def _read_names():
    names = {}
    for p in ROOT.rglob("*.py"):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in ("tests", "venv", ".venv", "node_modules") or any(x.startswith(".") for x in rel.parts):
            continue
        for m in READ.finditer(p.read_text(encoding="utf-8", errors="replace")):
            names.setdefault(m.group(1) or m.group(2), str(rel))
    return names


def _documented():
    text = ""
    for f in (ROOT / ".env.example", ROOT / "deploy" / "cloud" / "env.example"):
        if f.exists():
            text += f.read_text(encoding="utf-8")
    return set(re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", text))


def test_alle_variablen_in_env_example():
    doc = _documented()
    fehlt = {n: f for n, f in _read_names().items() if n not in doc and n not in INTERN}
    assert not fehlt, "In .env.example fehlen (mit Kommentar und Platzhalter ergaenzen): " + ", ".join(
        f"{n} ({f})" for n, f in sorted(fehlt.items()))


def test_env_example_ohne_echte_werte():
    """Aktive Zeilen mit Schluesseln/Passwoertern muessen leer sein."""
    for f in (ROOT / ".env.example", ROOT / "deploy" / "cloud" / "env.example"):
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*([A-Z][A-Z0-9_]*)=(.*)", line)
            if m and re.search(r"KEY|TOKEN|SECRET|PASSWORD", m.group(1)):
                assert not m.group(2).split("#")[0].strip(), f"{f.name}: {m.group(1)} hat einen Wert"
