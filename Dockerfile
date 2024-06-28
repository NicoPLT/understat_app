# Usa un'immagine di base ufficiale di Python
FROM python:3.11

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice sorgente nell'immagine
COPY . .

# Comanda per avviare l'app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
