#!/bin/bash
set -e

FLAG=$1  # argumento (ex: --upload)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo " Iniciando pipeline no diretório: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "[1] Subindo containers com Docker Compose..."
docker compose up -d

# --- Verificar o .env ---
if [ ! -f .env ]; then
  echo " Arquivo .env não encontrado no diretório raiz!"
  exit 1
fi

# --- Upload .csv ---
if [ "$FLAG" == "--upload" ]; then
  echo "[2] Enviando novos dados para o S3 via FastAPI..."
  echo "⏳ Aguarda o FastAPI iniciar..."
    sleep 10  
  curl -X POST "http://localhost:8000/upload"

  echo "[3] Aguardando Snowflake processar o load via Snowpipe..."
  sleep 10  
  
  echo "[4] Executando fetch_from_snowflake para puxar os dados do Snowflake..."
  docker compose exec jupyter python /scripts/fetch_from_snowflake.py
else
  echo "[2] [Skip] Upload para o S3 não solicitado."
fi

echo "[DONE] Pipeline concluído!"
