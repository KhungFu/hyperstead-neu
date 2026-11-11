# Erster Auftrag an den CEO (zum Einfügen als neuer Auftrag)

Hallo CEO, das ist der erste Auftrag für Steadforge Labs. Bitte antworte mir immer auf Deutsch.

Ziel: Verschaffe dir und dem Team einen vollständigen Überblick über Hyperstead und lege mir einen ersten Verbesserungsplan vor.
In diesem Auftrag wird NICHTS veröffentlicht: kein Push, kein Pull Request, kein Merge, kein Release, kein Deployment.

1. Arbeitsort: Der CTO prüft, ob es im Projektordner den Ordner repo/ gibt. Wenn nicht:
   git clone https://github.com/KhungFu/hyperstead-neu repo
   Danach git -C repo status und git -C repo log --oneline -5. Lest repo/CLAUDE.md und repo/README.md zuerst.
2. Bestandsaufnahme (CTO mit Backend und Frontend): Aufbau, wichtigste Module, Datenbank, Rechte-System, Werkzeuge, Schwachstellen,
   technische Schulden, alles, was eine Cloud-Version mit vielen Kunden verhindert (z. B. eine SQLite-Datei für alle, ein Besitzer-Login).
3. Tests (QA & Security): python -m pytest -q tests im Ordner repo ausführen, Ergebnis festhalten. Sicherheitsprüfung auf Geheimnisse im Code,
   fehlende Rechteprüfungen und Risiken für einen Mehrkunden-Betrieb. Ergebnis als TEST_REPORT.md.
4. SaaS-Zielbild (Cloud-Architekt + Product & Business): Wie wird Hyperstead mandantenfähig (Konten, Login, Datentrennung,
   verschlüsselte API-Schlüssel der Kunden, Abos, Limits je Paket, Hosting, Backups)? Schlagt 3 bis 4 Pakete vor (Leistungen und Grenzen,
   Preise mit Marktvergleich und Quellen). Entscheidungen als ADR in docs/adr/.
5. Team: Prüfe, ob das Team für diesen Plan reicht. Stelle bei Bedarf passende Mitarbeiter ein (mit klaren Rollen, Pflichten und nur den
   nötigen Rechten). Nenne mir, welche neuen Mitarbeiter eine KI zugewiesen bekommen müssen und wer welche Rechte von mir braucht.
6. Plan: Schreibe den Verbesserungsplan nach plan/verbesserungsplan.md:
   - Die 10 wichtigsten Verbesserungen, sortiert nach Nutzen und Risiko, je mit Aufwand (S/M/L), betroffenen Dateien und Abnahmekriterium.
   - Fahrplan zur SaaS in Phasen (je Phase Ziel, Ergebnis, Risiken).
   - Vorschlag für das erste Arbeitspaket, das ihr als Nächstes umsetzen wollt.
7. Bericht an mich (auf Deutsch, kurz und klar): Was ihr gefunden habt, Testergebnis, die wichtigsten Risiken, der Plan in Stichpunkten,
   das vorgeschlagene erste Arbeitspaket und die Frage, ob ihr damit beginnen dürft.

Regeln: Es gilt die Freigaberegel aus dem Firmenwissen. Keine Zugangsdaten in Dateien, Logs oder Berichte. Nichts als erledigt melden,
was nicht geprüft ist.
