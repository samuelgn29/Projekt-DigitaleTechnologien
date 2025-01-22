# Wetter-Dashboard mit Streamlit & MQTT

Dieses Projekt ist eine Anwendung zur Überwachung von Wetterdaten, die über die OpenWeatherMap API abgerufen und in einer PostgreSQL-Datenbank gespeichert werden. 
Die Daten werden über einen MQTT-Broker verteilt und in einem interaktiven Streamlit-Dashboard visualisiert.

## 📌 Funktionen
- 📡 Echtzeit-Abruf von Wetterdaten (Temperatur, Luftfeuchtigkeit, Luftdruck)
- 🔗 MQTT-Publishing und Subscribing
- 🗄 Speicherung der Daten in einer PostgreSQL-Datenbank
- 📊 Visualisierung mit Plotly in Streamlit

###  Voraussetzungen
- Python 3.8+
- PostgreSQL
- MQTT-Broker (HiveMQ oder eigener Broker)
- Streamlit

### 1. Setup
```bash
Die Anleitung zur Installation finden Sie im INSTALL.md
