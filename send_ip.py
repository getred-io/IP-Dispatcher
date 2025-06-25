#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import subprocess
from email.mime.text import MIMEText

# --- Konfiguration ---
# E-Mail-Adresse und App-Passwort des Absenders (z.B. von Gmail)
# WICHTIG: Verwenden Sie ein "App-Passwort", nicht Ihr normales Passwort.
# Anleitung für Gmail: https://support.google.com/accounts/answer/185833
SENDER_EMAIL = "DEINE_EMAIL@gmail.com"
SENDER_PASSWORD = "DEIN_APP_PASSWORT"

# E-Mail-Adresse des Empfängers
RECIPIENT_EMAIL = "EMPFÄNGER_EMAIL@example.com"

# SMTP-Server-Einstellungen (Beispiel für Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_ip_address():
    """Ermittelt die aktuelle IP-Adresse des Raspberry Pi."""
    try:
        # Führt den Befehl 'hostname -I' aus, um die IP-Adresse zu erhalten
        ip_address = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
        return ip_address.split()[0] # Nur die erste IP-Adresse verwenden
    except Exception as e:
        print(f"Fehler beim Ermitteln der IP-Adresse: {e}")
        return None

def send_email(ip_address):
    """Versendet eine E-Mail mit der IP-Adresse."""
    if not ip_address:
        print("Keine IP-Adresse zum Senden vorhanden.")
        return

    subject = f"Raspberry Pi IP-Adresse: {ip_address}"
    body = f"Der Raspberry Pi wurde gestartet.\n\nSeine IP-Adresse ist: {ip_address}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        # Verbindung zum SMTP-Server aufbauen und E-Mail senden
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS-Verschlüsselung aktivieren
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        print("E-Mail erfolgreich versendet.")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

if __name__ == "__main__":
    ip = get_ip_address()
    send_email(ip)
