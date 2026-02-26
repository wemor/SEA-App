# Firebase Setup für die SEA-App

Die SEA-App unterstützt nun das Speichern und Laden von Berechnungs-Projekten direkt über **Firebase Firestore**. Die Projekte werden in einer Firebase Collection namens `sea_projects` abgelegt.

Damit die Streamlit-App auf deine Firebase-Datenbank zugreifen darf, benötigt sie die Zugangsdaten in Form eines Service-Account-JSON. Dieser Key darf aus Sicherheitsgründen niemals direkt in den Quellcode (GitHub) eingecheckt werden. 
Stattdessen müssen die Zugangsdaten in den **Streamlit Secrets** hinterlegt werden.

## 1. Firebase Service Account Key beschaffen
Genauso wie für deine Sales Logbook App benötigst du den Admin-Schlüssel:
1. Gehe in deine **Firebase Console**.
2. Öffne die Projekteinstellungen (Zahnrad) -> **Dienstkonten** (Service Accounts).
3. Klicke auf **"Neuen privaten Schlüssel generieren"** (Generate new private key).
4. Es wird eine `.json`-Datei heruntergeladen. 

## 2. In Streamlit Cloud eintragen (Live-App)
Damit die öffentlich gehostete Cloud-App funktioniert:
1. Gehe in dein [Streamlit Cloud Dashboard](https://share.streamlit.io/).
2. Klicke bei deiner SEA-App auf die 3 Punkte `...` -> **Settings** -> **Secrets**.
3. Kopiere den *kompletten* Inhalt deiner heruntergeladenen JSON-Datei und füge ihn dort im TOML-Format ein.
Das Ganze muss zwingend unter dem Schlüssel-Namen `[firebase]` stattfinden.

**Beispiel, wie das Format in den Streamlit-Secrets aussehen muss:**

```toml
[firebase]
type = "service_account"
project_id = "dein-projekt-id"
private_key_id = "12345abcde..."
private_key = "-----BEGIN PRIVATE KEY-----\nDeinLangerKey...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxx@dein-projekt.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/..."
```

*(Streamlit konvertiert typischerweise JSON-Datenstruktur sehr einfach in TOML - die Einrückung oder Quotes müssen wie oben abgebildet sein).*

## 3. Lokal testen (Auf deinem PC)
Wenn du die App lokal auf deinem Computer via `streamlit run app.py` testen möchtest:
1. Erstelle lokal in deinem Workspace (`C:\Users\WernerMoretti\OneDrive - wemo\Antigravity_WS\SEA-App`) einen neuen Ordner namens `.streamlit`, falls er noch nicht existiert.
2. Erstelle darin eine Datei namens `secrets.toml`.
3. Füge exakt den gleichen TOML-Block wie unter Schritt 2 in diese Datei ein.

*(Die Datei `.streamlit/secrets.toml` ist glücklicherweise bereits in der `.gitignore` der Streamlit-Templates ausgeschlossen und landet so nicht versehentlich auf GitHub).*

Sobald die Secrets hinterlegt sind, wird im Tab "💾 File" der Bereich **☁️ Cloud (Firebase)** freigeschaltet und du kannst Projekte speichern und laden!
