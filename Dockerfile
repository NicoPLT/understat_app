# Utilizza l'immagine di base di Python 3.11
FROM python:3.11

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y build-essential libc-dev python3-dev

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Esegui l'applicazione
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
