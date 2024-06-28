# Utilizzare un'immagine ufficiale di Python come immagine di base
FROM python:3.11-slim

# Impostare la directory di lavoro
WORKDIR /app

# Copiare i file requirements.txt e runtime.txt nella directory di lavoro
COPY requirements.txt .

# Installare le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copiare il resto dei file dell'applicazione nella directory di lavoro
COPY . .

# Comando per eseguire l'applicazione
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
