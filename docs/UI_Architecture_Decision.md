# UI-Architektur-Entscheidung: SEA-App

## Ausgangslage
Es wurde ein UI-Konzept für die SEA-App erstellt (`UI proposal_v1.png`), welches folgende Elemente beinhaltet:
- Eine klassische obere Toolbar (File, Calculation, Results, Materials)
- Einen linken "Project Tree" zur Navigation durch die Modellstruktur
- Einen zentralen Canvas für die "SEA Model Visualization"
- Eine rechte Seitenleiste zur Auswahl von "SEA Elements" (Cavity, Wall, etc.)
- Einen unteren Bereich für "Tool Messages"

## Evaluierte Optionen

### Option 1: Streamlit (Aktueller Stack)
Streamlit ist hervorragend für schnelle Daten-Dashboards, besitzt aber ein starreres Layout-Modell.
- **Top Toolbar:** Schwer permanent am oberen Rand zu fixieren; kann mit horizontalen Spalten (`st.columns`) simuliert werden (scrollt aber mit).
- **Linker Project Tree:** Sehr gut umsetzbar mit der nativen `st.sidebar`.
- **Zentrale Visualisierung:** Kann im Hauptbereich platziert werden.
- **Rechte Element-Leiste:** Kann durch Aufteilung der Hauptspalte simuliert werden (z.B. 80% für Graphen, 20% für Buttons).
- **Interaktive Limitierungen:** Jeder Klick in Streamlit lädt das gesamte Skript neu. Flüssiges Drag & Drop für den graphischen Modellaufbau ist ohne komplexe Custom-Components kaum realisierbar. Das UI fühlt sich statischer an.
- **Hosting:** Kann weiterhin problemlos über die **Streamlit Community Cloud** gehostet werden.

### Option 2: Custom Web Stack (FastAPI + HTML/JS/Tailwind)
Dies entspricht dem Stack der existierenden *Engineering-App*.
- **UI Flexibilität:** Absolute Freiheit. Fixierte Toolbars, Footer und Sidebar-Layouts sind Standard (HTML/CSS).
- **Interaktivität:** Flüssig ohne Neuladen der Seite (Single Page Application). Echtes Drag & Drop im Graphen ist mit JS-Bibliotheken (wie D3.js oder vis.js) sehr gut machbar.
- **Architektur:** `sea_app.core` bleibt unberührt und wird durch eine REST-API (FastAPI) gekapselt.
- **Hosting:** Kann **nicht** in der Streamlit Community Cloud gehostet werden. Erfordert Plattformen wie Render.com (wie bei der Engineering-App verwendet).

## Entscheidung (Stand: 24.02.2026)
Es wurde beschlossen, **vorerst bei Streamlit zu bleiben**, um die Hosting-Möglichkeit über die **Streamlit Community Cloud** beizubehalten.

Das Ziel für die nächste Iteration ist es, das `UI proposal_v1.png` Layout so gut wie möglich innerhalb der Grenzen von Streamlit anzunähern:
- Der Project Tree wird weiterhin in der linken `st.sidebar` abgebildet.
- Eine simulierte "Top Toolbar" wird mit `st.columns` am Anfang der Seite eingefügt.
- Der Hauptbereich wird in zwei Spalten geteilt (visuelles Modell / rechte Elemente-Toolbar).
- Ein einfacher Nachrichtenbereich (Tool Messages) wird am unteren Ende der Seite integriert.
- Wir akzeptieren das Rerun-Verhalten von Streamlit und verzichten vorerst auf echtes Drag & Drop.
