# Zugriff auf die Streamlit App limitieren

**Zusammenfassung:**
Um den Zugriff auf die auf der Streamlit Cloud gehostete SEA-App zu beschränken, bietet sich die plattform-interne "Private App"-Funktion an. Diese Methode erfordert keine Code-Änderungen und bietet eine einfache Verwaltung von berechtigten Nutzern über das Streamlit Dashboard.

---

## Empfohlene Methode: App auf "Private" setzen (Streamlit Cloud)

Diese Methode ist ideal, wenn nur ein spezifischer, bekannter Personenkreis (z. B. Kollegen oder bestimmte Kunden) die App nutzen soll.

### Schritt-für-Schritt Anleitung:

1.  **Im Dashboard einloggen:** Gehe auf [share.streamlit.io](https://share.streamlit.io/) und melde dich mit dem Account an, unter dem die App bereitgestellt (deployed) wurde (in der Regel über GitHub).
2.  **App-Einstellungen öffnen:** Suche die SEA-App in der Liste deiner Anwendungen. Klicke auf die drei vertikalen Punkte (`...`) neben dem App-Namen und wähle **"Settings"** (Einstellungen).
3.  **Sichtbarkeit ändern:** Navigiere im Einstellungsmenü zum Reiter **"Sharing"** (Freigabe).
4.  **Auf "Private" umstellen:** Ändere die Sichtbarkeitseinstellung von "Public" (Öffentlich) auf **"Private"** (Privat).
5.  **Viewer hinzufügen:** Im gleichen Reiter kannst du nun unter "Viewer emails" die E-Mail-Adressen der Personen eintragen, die Zugriff auf die App erhalten sollen. Trage eine E-Mail pro Zeile ein und speichere die Einstellungen.

### Wie der Zugriff für die Benutzer funktioniert:

*   **Entwickler:** Personen, die in dem verknüpften GitHub-Repository Schreibzugriff (Write access) haben, haben automatisch vollen Zugriff auf die App und ihre Verwaltung.
*   **Eingeladene Benutzer (Viewer):** Wenn eine der von dir eingetragenen Personen den Link zur App öffnet, wird sie von einem Login-Bildschirm begrüßt.
    *   **Identifizierung:** Der Nutzer muss seine E-Mail-Adresse bestätigen.
    *   **Google-Konten:** Handelt es sich bei der E-Mail um ein Google-Konto, kann sich der Nutzer bequem per "Single Sign-On" mit seinem Google-Login authentifizieren.
    *   **Andere E-Mail-Provider:** Für alle anderen Adressen schickt Streamlit einen einmaligen Login-Link (Magic Link) an diese E-Mail-Adresse. Der Link ist für 15 Minuten gültig. Nach einem Klick auf diesen Link erhält die Person Zugang zur App.
*   **Nicht berechtigte Benutzer:** Personen, die den Link haben, aber nicht in der Viewer-Liste stehen oder keine GitHub-Rechte haben, erhalten keinen Zugriff und bekommen eine entsprechende Fehlermeldung angezeigt.

---

## Alternative (für spätere Erweiterungen): Implementierung eines Login-Systems im Code

Sollte es in der Zukunft notwendig sein, die App öffentlich zugänglich zu lassen, aber Teile davon durch eine Bezahlschranke (Paywall) oder ein internes Rechtesystem zu schützen, kann ein Login-System direkt im Python-Code (`app.py`) implementiert werden.

*   **Community Paket:** Für einen klassischen Benutzernamen/Passwort-Schutz eignet sich das Paket `streamlit-authenticator`.
*   **Enterprise SSO:** Für eine Integration in bestehende Firmennetzwerke (Microsoft Entra ID, Google Workspace, Okta) bietet Streamlit ab Version 1.32 native Befehle wie `st.login()` zur Anbindung via OpenID Connect (OIDC). Dies erfordert jedoch die Einrichtung der App beim jeweiligen Identitätsanbieter (z. B. Azure Portal).

*Für den aktuellen Projektstand wird die einfache "Private App" Einstellung (Methode 1) aus Gründen der Sicherheit und Wartungsfreundlichkeit präferiert.*
