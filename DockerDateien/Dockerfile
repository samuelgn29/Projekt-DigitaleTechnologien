# Basis-Image mit Python
FROM python:3.12-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Anforderungen kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Arbeitsverzeichnisinhalt kopieren
COPY . .

# Exponiere Ports für Streamlit
EXPOSE 8501

# Kommando für die Ausführung
CMD ["sh", "-c", "python database.py & streamlit run dashboard.py"]
