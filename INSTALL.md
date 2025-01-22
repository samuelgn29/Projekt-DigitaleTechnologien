#  Installationsanleitung

## Voraussetzungen
- Python 3.8+
- PostgreSQL installiert und konfiguriert
- MQTT-Broker (z. B. HiveMQ oder Mosquitto)
- API-Key für OpenWeatherMap

## Container über cmd erstellen und starten.
    1. Dateien dashboard.py, docker-compose Dockerfile, main.py, requirements.txt und .env runterladen
    2. Beim Download kann es sein, dass die .env-Datei zu "env" umbenannt wird. Falls das passiert, muss diese manuell wieder zu ".env" umbenannt werden
    3. Runtergeladenen Dateien im selben Ordner speichern
    4. CMD öffnen und zu dem Ordner navigieren in dem sich die Dateien befinden. Bsp.: "cd C:\Users\samue\Desktop\Uni\DigitaleTechnologien"
    5. Befehl "docker compose build" ausführen
    6. Befehl "docker compose up" ausführen -> Container wird gestartet
    7. Anwendung lokal im Browser aufrufen mit der URL: "http://localhost:8088" (wenn die Anwendung lokal gestartet wurde), oder "http://10.154.4.40:8088/" (wenn die Anwendung auf DaBivSim läuft)
    8. Anmelden mit BN:user123 PW:password
    9. Falls die Anwendung lokal auf dem Rechner gestartet wird und man nicht mit dem Wlan der HSWT verbudnen ist, muss das VPN gestartet werden, da man sonst keine Daten aus der DB abrufen kann

