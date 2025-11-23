# Envio dos dados para o S3
from fastapi import FastAPI
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do S3
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PATH = os.getenv("S3_PATH", "")
LOCAL_FILE_PATH = "/data/raw/csv_concatenado.csv"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)

# Inicializar FastAPI
app = FastAPI(title="Upload para S3", version="1.0")

# Endpoint para docker check
@app.get("/")
def health():
    """Endpoint de verificação simples"""
    return {"status": "ok"}

# Endpoint para upload de arquivo
@app.post("/upload")
def upload_file():
    """
    Endpoint para upload de arquivo para o S3.

    Args:
        None

    Returns:
        dict: Mensagem de sucesso ou erro

    Raises:
        FileNotFoundError: Se o arquivo local não for encontrado
        Exception: Para outros erros durante o upload
    """
    try:

        if not os.path.exists(LOCAL_FILE_PATH):
            return {"error": f"Arquivo não encontrado: {LOCAL_FILE_PATH}"}

        # Adicionando timestamp ao nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"csv_{timestamp}concatenado.csv"

        # Caminho dentro do bucket
        s3_key = f"{S3_PATH}{filename}"

        # Upload
        s3.upload_file(LOCAL_FILE_PATH, S3_BUCKET, s3_key)

        return {
            "message": f"Enviado com sucesso: s3://{S3_BUCKET}/{s3_key}"
        }

    except Exception as e:
        return {"error": f"Falha ao enviar: {str(e)}"}
