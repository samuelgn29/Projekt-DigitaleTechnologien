import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from dotenv import load_dotenv
import os

# ----------------------------- Konfiguration -----------------------------

# PostgreSQL-Datenbankverbindung
DB_HOST = os.getenv("DB_HOST")                              # Datenbank-Adresse
DB_PORT = os.getenv("DB_PORT")                              # Datenbank-Port
DB_NAME = os.getenv("DB_NAME")                    # Name der Datenbank
DB_USER = os.getenv("DB_USER_DASHBOARD")                    # Benutzername
DB_PASSWORD = os.getenv("DB_PASSWORD_DASHBOARD")            # Passwort

# Benutzername und Passwort für die App
DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME")        # Standard-Benutzername
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")        # Standard-Passwort

# Schwellwerte für Benachrichtigungen
HUMIDITY_THRESHOLD = 60                                     # Maximal erlaubte Luftfeuchtigkeit (%)
MAXTEMPERATURE_THRESHOLD = 25                               # Maximal erlaubte Temperatur (°C)
MINTEMPERATURE_THRESHOLD = 18                               # Minimal erlaubte Temperatur (°C)

# Streamlit-Seitenkonfiguration
st.set_page_config(
    page_title="Wetter Dashboard", 
    page_icon="🌤️", 
    layout="wide"
)

# ----------------------------- Funktionen -----------------------------

def fetch_data():
    """
    Ruft die Wetterdaten aus der PostgreSQL-Datenbank ab und gibt sie als Pandas DataFrame zurück.
    """
    try:
        # SQLAlchemy-Engine für PostgreSQL erstellen
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

        # SQL-Abfrage ausführen
        query = "SELECT timestamp, temperature, humidity, pressure FROM weather_app ORDER BY timestamp ASC;"
        data = pd.read_sql_query(query, engine)  # ✅ Jetzt mit SQLAlchemy!

        return data
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return pd.DataFrame()


def login():
    """
    Zeigt die Anmeldemaske an und überprüft die Benutzeranmeldung.
    """
    st.title("🔒 Anmeldung")
    st.write("Bitte melden Sie sich mit Ihrem Benutzernamen und Passwort an.")
    
    # Eingabefelder für Benutzername und Passwort
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    
    # Button zur Anmeldung
    if st.button("Anmelden"):
        # Benutzername und Passwort validieren
        if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
            st.session_state["logged_in"] = True
            st.success("✅ Anmeldung erfolgreich!")
        else:
            st.error("❌ Falscher Benutzername oder Passwort.")

def main_app():
    """
    Hauptanwendung für das Dashboard, einschließlich Visualisierungen und Benachrichtigungen.
    """
    st.title("🌤️ Wetter Dashboard")
    st.markdown("### Analyse der aktuellen Wetterdaten mit Echtzeit-Visualisierungen.")

    # Wetterdaten abrufen
    data = fetch_data()

    if not data.empty:
        # Konvertierung des Zeitstempels in ein datetime-Format
        data['timestamp'] = pd.to_datetime(data['timestamp'])

        # Dashboard-Header: Zeigt die aktuellen Werte mit Benachrichtigungen
        latest_data = data.iloc[-1]  # Neuester Datensatz
        previous_data = data.iloc[-2] if len(data) > 1 else latest_data  # Vorheriger Datensatz

        col1, col2 = st.columns(2)

        # Temperaturanzeige mit Delta-Wert
        with col1:
            temp_delta = latest_data["temperature"] - previous_data["temperature"]
            st.metric("🌡️ Temperatur", f"{latest_data['temperature']} °C", delta=f"{temp_delta:.2f}°")

        # Luftfeuchtigkeit mit Delta-Wert
        with col2:
            humidity_delta = latest_data["humidity"] - previous_data["humidity"]
            st.metric("💧 Luftfeuchtigkeit", f"{latest_data['humidity']} %", delta=f"{humidity_delta:.1f}%")

        # Benachrichtigungen bei Überschreiten von Schwellwerten
        if latest_data["humidity"] > HUMIDITY_THRESHOLD:
            st.warning("💧 Hohe Luftfeuchtigkeit! Maßnahmen empfohlen.")
        if latest_data["temperature"] < MINTEMPERATURE_THRESHOLD:
            st.warning("🌡️ Niedrige Temperatur! Heizen empfohlen.")
        if latest_data["temperature"] > MAXTEMPERATURE_THRESHOLD:
            st.warning("🌡️ Hohe Temperatur! Lüften empfohlen.")

        # Sidebar-Filter für Zeitbereich
        st.sidebar.header("⚙️ Filteroptionen")
        start_date = st.sidebar.date_input("Startdatum", value=data['timestamp'].min().date())
        end_date = st.sidebar.date_input("Enddatum", value=data['timestamp'].max().date())
        start_time = st.sidebar.time_input("Startzeit", value=pd.Timestamp("00:00:00").time())
        end_time = st.sidebar.time_input("Endzeit", value=pd.Timestamp("23:59:59").time())

        if start_date <= end_date:
            # Zeitbereich erstellen
            start_datetime = pd.Timestamp.combine(start_date, start_time)
            end_datetime = pd.Timestamp.combine(end_date, end_time)
            filtered_data = data[(data['timestamp'] >= start_datetime) & (data['timestamp'] <= end_datetime)]

            if not filtered_data.empty:
                st.markdown("### 📈 Visualisierungen")

                # Visualisierung: Temperaturverlauf
                fig_temp = px.line(
                    filtered_data,
                    x='timestamp',
                    y='temperature',
                    title='Temperaturverlauf',
                    labels={"timestamp": "Zeit", "temperature": "Temperatur (°C)"},
                    template="plotly_dark",
                    line_shape="linear"
                )
                st.plotly_chart(fig_temp, use_container_width=True)

                # Visualisierung: Luftfeuchtigkeitsverlauf
                fig_humidity = px.line(
                    filtered_data,
                    x='timestamp',
                    y='humidity',
                    title='Feuchtigkeitsverlauf',
                    labels={"timestamp": "Zeit", "humidity": "Feuchtigkeit (%)"},
                    template="plotly_dark",
                    line_shape="linear"
                )
                st.plotly_chart(fig_humidity, use_container_width=True)

                # Visualisierung: Druckverlauf
                fig_pressure = px.line(
                    filtered_data,
                    x='timestamp',
                    y='pressure',
                    title='Druckverlauf',
                    labels={"timestamp": "Zeit", "pressure": "Druck (hPa)"},
                    template="plotly_dark",
                    line_shape="linear"
                )
                st.plotly_chart(fig_pressure, use_container_width=True)

                # Anzeige der Daten in tabellarischer Form
                st.markdown("### 📋 Tabellarische Daten")
                st.dataframe(filtered_data)
            else:
                st.warning("⚠️ Keine Daten im ausgewählten Zeitraum gefunden.")
        else:
            st.error("❌ Das Startdatum muss vor dem Enddatum liegen.")
    else:
        st.warning("⚠️ Keine Daten gefunden.")


# ----------------------------- Hauptprogramm -----------------------------

# Benutzer-Session initialisieren
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Authentifizierungskontrolle
if not st.session_state["logged_in"]:
    login()
else:
    main_app()
