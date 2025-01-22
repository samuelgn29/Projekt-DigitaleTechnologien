#  Installationsanleitung

## Voraussetzungen
- Python 3.8+
- PostgreSQL installiert und konfiguriert
- MQTT-Broker (z. B. HiveMQ oder Mosquitto)
- API-Key für OpenWeatherMap

Container über cmd erstellen und starten.

    1. Dateien dashboard.py, docker-compose Dockerfile, main.py, requirements.txt und .env runterladen
    2. Runtergeladenen Dateien im selben Ordner speichern
    3. CMD öffnen und zu dem Ordner navigieren in dem sich die Dateien befinden. Bsp.: "cd C:\Users\samue\Desktop\Uni\DigitaleTechnologien"
    4. Befehl "docker compose build" ausführen
    5. Befehl "docker compose up" ausführen -> Container wird gestartet
    6. Anwendung lokal im Browser aufrufen mit der URL aus den logs: "http://localhost:8088"
    7. Anmelden mit BN:user123 PW:password
    8. Falls die Anwendung lokal auf dem Rechner gestartet wird und man nicht mit dem Wlan der HSWT verbudnen ist, muss das VPN gestartet werden, da man sonst keine Daten aus der DB abrufen kann

