Ich wollte meinen PAM-Crawler auf einem Raspberry Pi in Betrieb nehmen, bin aber an den Netzwerkrestriktionen bei uns in der Firma gescheitert – IP-Ermittlung und Scanner sind komplett blockiert. Deshalb habe ich dieses Skript entwickelt, das die IP Adresse des Pis nach Start automatisch an meine Email Adresse versendet.

# Anleitung: Raspberry Pi IP-Adresse bei Systemstart per E-Mail senden

Dieses Tutorial beschreibt, wie Sie einen Raspberry Pi so einrichten, dass er nach jedem Start automatisch seine aktuelle IP-Adresse per E-Mail versendet. Dies ist besonders nützlich für den "Headless"-Betrieb (ohne Monitor), um sich per SSH verbinden zu können.

Wir verwenden ein Python-Skript für den E-Mail-Versand und einen `systemd`-Service, um einen zuverlässigen Start nach erfolgreicher Netzwerkverbindung sicherzustellen.

## Voraussetzungen

  * Ein Raspberry Pi mit Raspberry Pi OS und Internetverbindung.
  * Ein E-Mail-Konto, das SMTP-Zugang erlaubt (z.B. Gmail).
  * Ein für die Anwendung erstelltes **App-Passwort**, nicht Ihr reguläres E-Mail-Passwort.
      * Anleitung für Google/Gmail: [Google-Konto-Hilfe - Mit App-Passwörtern anmelden](https://support.google.com/accounts/answer/185833)

-----

## Schritt 1: Das Python-Skript (`send_ip.py`) erstellen

Dieses Skript ermittelt die IP-Adresse und versendet sie über einen SMTP-Server.

### 1.1. Datei erstellen

Öffnen Sie ein Terminal auf Ihrem Raspberry Pi und erstellen Sie die Skript-Datei im Home-Verzeichnis des Benutzers `pi`.

```bash
nano /home/pi/send_ip.py
```

### 1.2. Python-Code einfügen

Kopieren Sie den folgenden Code in den `nano`-Editor.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import subprocess
import time
from email.mime.text import MIMEText

# --- Konfiguration: Passen Sie diese Werte an! ---

# E-Mail-Adresse und App-Passwort des Absenders (z.B. von Gmail)
# WICHTIG: Verwenden Sie ein "App-Passwort", nicht Ihr normales Passwort.
SENDER_EMAIL = "DEINE_EMAIL@gmail.com"
SENDER_PASSWORD = "DEIN_APP_PASSWORT"

# E-Mail-Adresse des Empfängers
RECIPIENT_EMAIL = "EMPFAENGER_EMAIL@example.com"

# SMTP-Server-Einstellungen (Beispiel für Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_ip_address():
    """Ermittelt die aktuelle IP-Adresse des Raspberry Pi."""
    try:
        # Führt den Befehl 'hostname -I' aus, um die IP-Adresse zu erhalten
        ip_address = subprocess.check_output(['hostname', '-I'], timeout=5).decode('utf-8').strip()
        # Nur die erste IP-Adresse verwenden, falls mehrere vorhanden sind
        return ip_address.split()[0]
    except Exception as e:
        # Protokolliert einen Fehler, falls die IP nicht ermittelt werden kann
        print(f"Fehler beim Ermitteln der IP-Adresse: {e}")
        return None

def send_email(ip_address):
    """Versendet eine E-Mail mit der IP-Adresse."""
    if not ip_address:
        print("Keine IP-Adresse zum Senden vorhanden. Breche ab.")
        return

    subject = f"Raspberry Pi IP-Adresse: {ip_address}"
    body = f"Der Raspberry Pi wurde gestartet.\n\n" \
           f"Datum: {time.strftime('%d.%m.%Y %H:%M:%S')}\n" \
           f"IP-Adresse: {ip_address}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        # Verbindung zum SMTP-Server aufbauen und E-Mail senden
        print(f"Verbinde mit {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS-Verschlüsselung aktivieren
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        print("E-Mail erfolgreich versendet.")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

if __name__ == "__main__":
    ip = get_ip_address()
    if ip:
        send_email(ip)
```

### 1.3. Skript konfigurieren

Passen Sie im Code die folgenden drei Variablen an:

  * `SENDER_EMAIL`: Ihre E-Mail-Adresse, von der gesendet wird.
  * `SENDER_PASSWORD`: Das App-Passwort, das Sie für Ihr Konto generiert haben.
  * `RECIPIENT_EMAIL`: Die E-Mail-Adresse, an die die Benachrichtigung gesendet werden soll.

Speichern und schließen Sie die Datei mit `Strg + X`, dann `Y` (oder `J`) und `Enter`.

### 1.4. Skript ausführbar machen

Damit das System das Skript ausführen darf, müssen Sie die Berechtigungen anpassen.

```bash
chmod +x /home/pi/send_ip.py
```

-----

## Schritt 2: Automatischer Start per `systemd`-Service

Ein `systemd`-Service stellt sicher, dass das Skript erst gestartet wird, wenn das Netzwerk vollständig verfügbar ist.

### 2.1. Service-Datei erstellen

Erstellen Sie mit `sudo`-Rechten eine neue Service-Datei.

```bash
sudo nano /etc/systemd/system/send-ip.service
```

### 2.2. Service-Konfiguration einfügen

Kopieren Sie den folgenden, kommentierten Inhalt in den Editor.

```ini
# Inhalt für /etc/systemd/system/send-ip.service

[Unit]
# Eine einfache Beschreibung des Services, sichtbar in Status-Meldungen.
Description=Send IP address via Email after network is up

# Diese Direktiven weisen systemd an, zu warten, bis das Netzwerk 
# als "online" gilt. Dies ist der Schlüssel für die Zuverlässigkeit.
Wants=network-online.target
After=network-online.target

[Service]
# 'simple' bedeutet, systemd betrachtet den Service als gestartet, 
# sobald der ExecStart-Befehl ausgeführt wurde.
Type=simple

# Der Befehl, der ausgeführt werden soll. Volle Pfade sind Best Practice.
ExecStart=/usr/bin/python3 /home/pi/send_ip.py

# Das Skript wird als Benutzer 'pi' ausgeführt, nicht als 'root'.
# Dies ist eine wichtige Sicherheitspraxis.
User=pi

[Install]
# Definiert, dass dieser Service beim Erreichen des "multi-user.target" 
# (normaler Systembetrieb mit Netzwerk) gestartet werden soll.
WantedBy=multi-user.target
```

Speichern und schließen Sie die Datei (`Strg + X`, `Y`/`J`, `Enter`).

-----

## Schritt 3: Den Service aktivieren und verwalten

Nun teilen wir `systemd` mit, dass der neue Service existiert und bei jedem Start ausgeführt werden soll.

### 3.1. `systemd`-Daemon neu laden

Damit `systemd` die neue `send-ip.service`-Datei erkennt:

```bash
sudo systemctl daemon-reload
```

### 3.2. Service für den Systemstart aktivieren

Dieser Befehl sorgt dafür, dass der Service bei jedem Boot-Vorgang automatisch gestartet wird.

```bash
sudo systemctl enable send-ip.service
```

### 3.3. Service manuell testen (Optional)

Sie können den Service sofort ausführen, um die Funktion zu testen, ohne den Raspberry Pi neu starten zu müssen.

```bash
sudo systemctl start send-ip.service
```

Überprüfen Sie Ihr E-Mail-Postfach. Sie sollten nun eine E-Mail mit der IP-Adresse erhalten haben.

-----

## Schritt 4: Überprüfung und Fehlersuche

Falls etwas nicht funktioniert, sind dies die wichtigsten Befehle zur Diagnose.

  * **Status des Services prüfen:**
    Zeigt an, ob der Service aktiv (`active (exited)`), fehlgeschlagen (`failed`) oder inaktiv ist.

    ```bash
    systemctl status send-ip.service
    ```

  * **Logs des Services ansehen:**
    Zeigt die Bildschirmausgaben (z.B. `print`-Anweisungen) des Python-Skripts an. Hier finden Sie Fehlermeldungen, falls das Skript nicht korrekt ausgeführt wurde.

    ```bash
    journalctl -u send-ip.service
    ```

    Um die Logs live zu verfolgen, fügen Sie die Option `-f` hinzu:

    ```bash
    journalctl -u send-ip.service -f
    ```

**Herzlichen Glückwunsch\! Ihr Raspberry Pi wird Sie nun nach jedem Start zuverlässig über seine IP-Adresse informieren.**
