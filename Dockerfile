# Dockerfile for FastAPI app
FROM python:3.12-slim-bullseye

WORKDIR /app

# Install only security updates and required system packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]