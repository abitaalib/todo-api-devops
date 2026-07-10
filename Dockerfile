FROM python:3.12-slim

WORKDIR /app

# Copier les dépendances en premier (optimisation cache Docker)
COPY requirements.txt ./
RUN pip install --no-cache-dir flask==3.0.3

# Copier le code
COPY app.py ./

EXPOSE 5000

CMD ["python", "app.py"]
