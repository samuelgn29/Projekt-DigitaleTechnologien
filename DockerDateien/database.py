import paho.mqtt.client as mqtt
import requests
import psycopg2
import json
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

load_dotenv()   # Lädt die .env-Datei

# Konfiguration des Loggings für Fehler
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------- Konfiguration -----------------------------

# OpenWeatherMap API-Details
API_KEY = os.getenv("API_KEY")    # API-Schlüssel für Wetterdaten
CITY_ID = os.getenv("CITY_ID")                            # City-ID für München
URL = f"http://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={API_KEY}&units=metric"

# MQTT Broker-Details
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))  # Stellt sicher, dass es eine Zahl ist
MQTT_TOPIC = "weather/munich"

# MQTT User-Details
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# PostgreSQL-Datenbankdetails
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER_DATABASE")
DB_PASSWORD = os.getenv("DB_PASSWORD_DATABASE")

# Datenabrufintervall in Sekunden
FETCH_INTERVAL = 600

# ----------------------------- Funktionen -----------------------------

def fetch_weather_data():
    """
    Ruft die aktuellen Wetterdaten von der OpenWeatherMap API ab.
    :return: Dictionary mit Wetterdaten oder None bei Fehlern.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"]
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return None


def publish_to_mqtt(data):
    """
    Veröffentlicht die Wetterdaten über den MQTT-Broker.
    :param data: Dictionary mit Wetterdaten.
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)  # Authentifizierung aktivieren
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=120)
        client.loop_start()
        payload = json.dumps(data)
        client.publish(MQTT_TOPIC, payload)
    except Exception as e:
        logging.error(f"Error publishing to MQTT: {e}")
    finally:
        client.loop_stop()
        client.disconnect()


def save_to_database(timestamp, temperature, humidity, pressure):
    """
    Speichert die Wetterdaten in der PostgreSQL-Datenbank.
    :param timestamp: Zeitstempel der Daten.
    :param temperature: Temperaturwert.
    :param humidity: Luftfeuchtigkeit.
    :param pressure: Luftdruck.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cur = conn.cursor()

        # Überprüfen, ob der Datensatz bereits existiert
        check_query = """
        SELECT COUNT(*) FROM weather_app
        WHERE timestamp = %s AND temperature = %s AND humidity = %s AND pressure = %s
        """
        cur.execute(check_query, (timestamp, temperature, humidity, pressure))
        if cur.fetchone()[0] > 0:
            logging.warning("⚠️ Datensatz bereits in der Datenbank, kein Insert.")
            return

        # Datensatz einfügen
        insert_query = """
        INSERT INTO weather_app (timestamp, temperature, humidity, pressure)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(insert_query, (timestamp, temperature, humidity, pressure))
        conn.commit()
    except psycopg2.Error as db_error:
        logging.error(f"Database error: {db_error}")
        conn.rollback()  # Rollback, falls ein Fehler auftritt
    except Exception as e:
        logging.error(f"Error saving to database: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def on_connect(client, userdata, flags, rc, properties=None):
    """
    Verbindungs-Callback für den MQTT-Client.
    """
    if rc == 0:
        client.subscribe(MQTT_TOPIC, qos=1)
    else:
        logging.error(f"Connection failed with code {rc}")


last_message = None

def on_message(client, userdata, message):
    """
    Verarbeitet eingehende MQTT-Nachrichten und speichert sie in der Datenbank.
    """
    global last_message
    try:
        payload = message.payload.decode()
        if payload == last_message:
            return
        last_message = payload

        data = json.loads(payload)
        if all(key in data for key in ("timestamp", "temperature", "humidity", "pressure")):
            save_to_database(data["timestamp"], data["temperature"], data["humidity"], data["pressure"])
        else:
            logging.error("Received data is missing required keys.")
    except Exception as e:
        logging.error(f"Error processing MQTT message: {e}")


def start_mqtt_subscriber():
    """
    Startet den MQTT-Subscriber-Client, um eingehende Nachrichten zu verarbeiten.
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)  # Authentifizierung aktivieren
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logging.error(f"Error starting MQTT subscriber: {e}")


# ----------------------------- Hauptprogramm -----------------------------

if __name__ == "__main__":
    import threading

    # MQTT-Subscriber in separatem Thread starten
    subscriber_thread = threading.Thread(target=start_mqtt_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Regelmäßiges Abrufen und Veröffentlichen der Wetterdaten
    while True:
        weather_data = fetch_weather_data()
        if weather_data:
            publish_to_mqtt(weather_data)
        time.sleep(FETCH_INTERVAL)
