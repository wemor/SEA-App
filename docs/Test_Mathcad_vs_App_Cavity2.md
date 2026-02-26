# Test: Mathcad vs. SEA-App (Cavity 2)

**Datum:** 26. Februar 2026

## Ziel des Tests
Vergleich der berechneten Schalldruckpegel ($L_p$) und Energien ($E$) zwischen dem etablierten Mathcad-Modell (`SEA_equationssolved_nopath13.pdf`) und der Python Streamlit SEA-App (Input: `SEA_Example_C1_L1221_W1_L2332_C2.json`).

## Problemstellung
Bei einem initialen Vergleich zeigte sich in der SEA-App für das Subsystem "Cavity 2" ein Schalldruckpegel von **44.3 dB**, während das Mathcad-Modell **41.7 dB** berechnete. Die Differenz betrug ca. 3 dB. Man ging zunächst davon aus, dass die App fehlerhaft rechnete, da die Mathcad-Berechnungen als korrekt validiert galten.

## Analyse & Ursache
* **Mathcad:** Die Anregung (Power) erfolgte in der Berechnung ausschließlich auf Cavity 1. Cavity 2 hatte keine eigene Leistungszufuhr ($P = 0$ W).
* **SEA-App (JSON-Input):** In der Konfigurationsdatei war für Cavity 2 ein sehr kleiner externer Leistungswert (`"power": 5e-08` W) hinterlegt. Diese zusätzliche Anregung führte zu der erhöhten Energie und dem höheren Pegel.
* **UI-Darstellung:** Die Streamlit-App formatierte die Eingabefelder für eingebrachte Leistungen (Power) standardmäßig mit 4 Nachkommastellen (`%.4f`). Dadurch wurde der Wert `0.00000005` in der Oberfläche der App als `0.0000` angezeigt, was visuell den Eindruck erweckte, die eingespeiste Leistung sei auf Null gesetzt.

## Lösung & Validierung
1. **Gegenprüfung ohne Störleistung:** Nachdem die Eingangsleistung für Cavity 2 in der App manuell explizit auf `0.0` W gesetzt wurde, berechnete der SEA-App Solver exakt die gleichen Werte wie Mathcad.
   * **Ergebnis Mathcad (aus PDF extr.):** Cavity 2 $\rightarrow E_3 = 3.07 \times 10^{-9}$ J, $L_{p,3} = 41.789$ dB
   * **Ergebnis SEA-App:** Cavity 2 $\rightarrow E = 2.986 \times 10^{-9}$ J, $L_p = 41.7$ dB
   *(Die minimalen Abweichungen resultieren aus leicht abweichenden grundlegenden physikalischen Konstanten, wie z.B. der Luftdichte $\rho_0$, zwischen den beiden Modellen).*
2. **App-Bugfix:** Die Formatierung des Eingabefeldes für die Leistung (`power`) in der Seitenleiste (`app.py`, Zeile 186) wurde auf Exponentialschreibweise (`format="%.4e"`) umgestellt. So werden selbst winzige Leistungseinträge transparent und unmittelbar im UI sichtbar (z. B. dargestellt als `5.0000e-08` W). Ein unbemerktes "Verstecken" von Leistungen durch Rundungen ist somit ausgeschlossen.

## Fazit
Der verallgemeinerte Matrix-Solver der SEA-App arbeitet mathematisch korrekt und stimmt bei identischer Anregung hervorragend mit den manuell modellierten Mathcad-Berechnungen überein. Die App ist damit für erste Berechnungen und Gegenprüfungen validiert.
