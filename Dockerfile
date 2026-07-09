# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port Flet (8550)
EXPOSE 8550

# Lancer l'application Flet
CMD ["python", "main.py"]