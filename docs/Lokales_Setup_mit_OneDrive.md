# SEA App - Lokales Setup & OneDrive-Synchronisierung

In diesem Projektordner wird die App über **OneDrive** zwischen mehreren Rechnern (z. B. Desktop und Laptop) synchronisiert. Das funktioniert für den Quellcode (die `.py`-Dateien) hervorragend, bereitet aber beim Python-Umgebungsordner (`.venv`) oft erhebliche Probleme.

## 🔴 Das Problem mit dem `.venv`-Ordner & OneDrive

Der `.venv`-Ordner enthält die lokal heruntergeladenen Python-Abhängigkeiten (z. B. Streamlit, Numpy, Pandas) – das sind oft über 10.000 winzige Dateien.
Wenn OneDrive versucht, diesen Ordner über die Cloud auf einen anderen Rechner zu synchronisieren, passiert folgendes:
1. **Verzögerung / Stau:** Der Upload/Download frisst extrem viel Zeit. Wichtige Code-Änderungen (`app.py`) bleiben im "Synchronsierungs-Stau" stecken und kommen auf dem anderen Rechner nicht an.
2. **Pfad-Konflikte:** Eine Python-Umgebung ist eigentlich hart an den Pfad der lokalen Python-Installation des jeweiligen Rechners gebunden. Eine 1:1 Kopie auf einen anderen PC funktioniert ohnehin oft fehlerhaft.

## 🟢 Die Lösung: Lokale Neu-Installation auf jedem Gerät

Um dieses Problem auf einem neuen Rechner (oder wenn die Synchronisation festhängt) sofort zu lösen, wird die Umgebung auf dem jeweiligen Gerät einfach **lokal neu erstellt**. Das dauert im Terminal weniger als eine Minute:

### Schritt-für-Schritt Anleitung

Befolge diese 3 Schritte direkt im VS Code Terminal, sobald du den Rechner wechselst und die App (oder OneDrive) streikt:

**1. Alten Stau auflösen (Löschen)**
Lösche den problematischen `.venv`-Ordner, um OneDrive sofort zu entlasten. Das geht per Rechtsklick im VS Code Explorer oder über das Terminal:
```powershell
Remove-Item -Recurse -Force .venv
```
*(Sobald der Ordner gelöscht ist, wird die blockierte `app.py` normalerweise in wenigen Sekunden synchronisiert!)*

**2. Frische, leere Umgebung erstellen**
Erstelle eine neue, exakt auf diesen PC zugeschnittene Python-Umgebung:
```powershell
python -m venv .venv
```

**3. Schnell-Installation aller nötigen Pakete**
Anstatt auf OneDrive zu warten, lädst du die nötigen Pakete rasend schnell über die `requirements.txt` Datei aus dem Internet herunter:
```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

Fertig! Starte danach die App wie gewohnt:
```powershell
.\.venv\Scripts\streamlit run app.py
```
