# Steadforge Labs – die Firma, die Hyperstead weiterentwickelt

Diese Anleitung sagt dir Schritt für Schritt, was wohin kommt. Alles andere macht die Firma selbst.

## Firmenprofil

| | |
|---|---|
| **Name** | Steadforge Labs („stead“ aus Hyperstead, „forge“ = Schmiede: die Werkstatt, in der Hyperstead geschmiedet wird) |
| **Vision** | Hyperstead wird vom lokalen KI-Büro zu einer sicheren SaaS-Plattform: Kunden schließen ein Abo ab, tragen ihre eigenen API-Schlüssel ein und bauen eigene Firmen mit Agenten auf. Die lokale Version bleibt. |
| **Mission** | Hyperstead in kleinen, getesteten Schritten verbessern, ehrlich berichten, nur mit deiner Freigabe veröffentlichen. |
| **Eigentümer** | ABI, letzte Freigabeinstanz für Push, Merge, Release und Deployment |
| **Firmensprache** | Deutsch mit dir. Code, Oberfläche und Agenten-Prompts bleiben Englisch (Regel des Repos). |

### Team (kommt fertig aus der Vorlage)

| Rolle | Unter | Rechte | Pflichten |
|---|---|---|---|
| CEO | dir | delegieren, prüfen, einstellen, Dateien, Werkstatt | planen, verteilen, Team zusammenstellen, Freigabebericht, OK einholen |
| CTO – Software Engineering & Release Management | CEO | delegieren, prüfen, Code, Ausführen, Werkstatt | Umsetzung leiten, Branches, Code-Review, CHANGES.md, Commits/PRs vorbereiten |
| Cloud architect | CTO | Code, Web, Dateien, Werkstatt | Weg zur SaaS: Konten, Mandanten, Schlüssel, Abos, Hosting (ADRs in docs/adr/) |
| Backend developer | CTO | Code, Ausführen, Werkstatt | Backend + Tests |
| Frontend developer | CTO | Code, Bilder, Werkstatt | Oberfläche (static/index.html) + Tests |
| QA & Security | CEO (unabhängig) | Code, Ausführen, Web, Werkstatt | Tests, Regressionen, Sicherheit, TEST_REPORT.md mit Urteil |
| Product & Business | CEO | Web, Dateien, Medien | Pakete, Preise, Markt, Roadmap |

Der CEO darf weitere Mitarbeiter einstellen. Hyperstead gibt Neuen aber nur einfache Rechte (Web, Bilder, Dateien, Medien, Code).
Rechte wie Werkstatt kannst nur du setzen, und neue Mitarbeiter bekommen ihre KI von dir (Menü ⚠ Models). Das ist Absicht:
so kann sich die Firma keine Rechte selbst geben.

### Entwicklungszyklus
Analysieren → Entwickeln → Testen (QA) → Freigabebericht (CEO) → **dein OK für genau diesen Stand** → Push, Pull Request, Merge → Ergebnis prüfen und melden.

## Was wohin kommt

### 1. Einmal auf dem Gerät (Pi oder Laptop)
1. In `.env` die Zeile `PCL_ALLOW_WERKSTATT=1` eintragen (sonst können die Agenten keine Befehle wie git oder pytest ausführen). Hyperstead neu starten.
   `PCL_WERKSTATT_FREI=1` bitte **nicht** setzen: Stufe 3 würde auch Push und Merge ohne Antrag erlauben.
2. GitHub-Anmeldung für git auf dem Gerät, als derselbe Benutzer, unter dem Hyperstead läuft:
   - Pi: `gh auth login` (GitHub CLI), danach `gh auth setup-git`.
   - Windows-Laptop: Git für Windows bringt den Git Credential Manager mit; einmal `git push` in einem beliebigen Repo im Terminal, im Browser anmelden.
   Die GitHub-Verbindung unter ☁️ Cloud (`GITHUB_UPLOAD_TOKEN`) ist nur für Datei-Uploads und reicht dafür **nicht**.
   Agenten sehen die Anmeldung nie: Befehle laufen ohne Schlüssel in der Umgebung, `.env` und `tokens/` sind gesperrt.
3. Test: im Terminal `gh auth status` (Pi) bzw. `git ls-remote https://github.com/KhungFu/hyperstead-neu` (Windows) muss ohne Fehler laufen.

### 2. In der App
1. Seitenleiste **＋ New project** → Vorlage **🛠️ Software company (develops Hyperstead itself)** → Name `Steadforge Labs` →
   KI für Leitung und Team wählen (Empfehlung: Leitung = dein stärkstes Modell, z. B. Claude über das Abo; Team = günstigeres Modell).
2. Seitenleiste **🧠 Company knowledge** → den ganzen Text aus [`firmenwissen.md`](firmenwissen.md) in das Textfeld kopieren → Speichern.
   Wichtig: Nur Text (.md/.txt) steht direkt im Kopf jedes Agenten. Ein PDF wird den Agenten nur als Datei genannt und erst bei Bedarf gelesen.
   Wenn du zusätzlich das PDF hochladen willst, ist das in Ordnung, aber der Text im Feld ist die verbindliche Fassung.
3. Rechte prüfen: Jeden Agenten anklicken. Beim CEO, CTO, den Entwicklern und QA das Häkchen **Workshop** an, Stufe **2 · normal**.
   Bei QA kannst du Stufe 1 wählen, wenn jeder Befehl erst gefragt werden soll.
4. Optional: unter **🕘 Schedule** einen täglichen Kontrollgang des CEO (z. B. 18:00), dann bekommst du jeden Abend den Stand.

### 3. Der erste Auftrag
CEO anklicken → Tab **Tasks** → den Text aus [`ceo-startauftrag.md`](ceo-startauftrag.md) einfügen → **Assign task**.
Der CEO analysiert mit dem Team das Repo, lässt testen und legt dir den Plan in 📬 Mail (und per Telegram) vor. Veröffentlicht wird dabei nichts.

## So läuft eine Freigabe
1. Das Team entwickelt und testet auf einem Branch. Der CEO schickt dir den **Freigabebericht** in 📬 Mail und per Telegram
   (Änderungen, Dateien, Tests, Risiken, Branch/Commit, geplante Aktionen).
2. Du antwortest in der Mail (Antwort = Nachbesserung) mit einem Satz aus [`freigabe-antworten.md`](freigabe-antworten.md),
   z. B. „OK für Stand abc1234 auf Branch feature/x: Push, Pull Request und Squash-Merge“.
3. Das Team führt `git push` aus. Hyperstead hält den Befehl als **Antrag** an: CEO prüft, du bekommst ✅/❌ unter ✋ Approvals und per Telegram,
   mit dem genauen Befehl. Erst dein ✅ führt ihn aus. Dasselbe gilt für `gh pr merge`, `gh release` und Deployments.
4. Danach meldet der CEO Commit-Hash und Merge-Status.

So hast du zwei Sicherungen: dein OK im Text **und** den Knopf für jeden einzelnen Veröffentlichungs-Befehl.
Das OK gilt immer nur für den genannten Stand.

## Empfehlung: Sprache der Software (nicht umgesetzt, nur Empfehlung)
**Empfehlung: jetzt bei Python bleiben, den künftigen SaaS-Server in Go bauen, Schritt für Schritt statt alles neu.**
- **Geschwindigkeit:** Hyperstead wartet fast immer auf KI-Anbieter (Sekunden je Antwort). Ob der Server dabei 1 ms oder 0,1 ms braucht, merkt
  kein Kunde. Go ist für so einen Server mit vielen gleichzeitigen Kunden praktisch so schnell wie Rust und deutlich schneller als Python.
- **Sicherheit:** Go und Rust sind beide speichersicher. Für ein SaaS sind Rechteprüfung, Datentrennung je Kunde und verschlüsselte Schlüssel
  wichtiger als die Sprache.
- **Wartung:** Go baut in Sekunden auch auf dem Pi und dem 8-GB-Laptop, liefert eine einzige Programmdatei und ändert sich kaum von Version zu
  Version. KI-Agenten schreiben Go zuverlässig. Rust ist am schnellsten, aber das Bauen dauert auf deinen Geräten lange und der Code ist für
  Agenten schwerer richtig zu schreiben.
- **Weg:** Kein großer Neubau. Zuerst Mandanten und Abos im bestehenden Python-Code planen, dann die SaaS-Teile (Konten, Abos, Job-Warteschlange)
  als eigenen Go-Dienst daneben stellen und Python-Teile nur ersetzen, wenn sie messbar bremsen. Die Firma soll das im ersten Plan als ADR bewerten.
