# Busca dados presentes no snowflake

import os
from datetime import datetime
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Snowflake
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_TABLE = os.getenv("SNOWFLAKE_TABLE", "wine_raw")

OUTPUT_DIR = "/data/processed"

# Conectar ao Snowflake e buscar dados
try:
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    conn.cursor().execute("ALTER SESSION SET USE_CACHED_RESULT = FALSE;")
    print("Conexão com Snowflake bem-sucedida.")

    query = f"SELECT * FROM {SNOWFLAKE_TABLE};"
    df = pd.read_sql(query, conn)
    print(f"Dados coletados: {df.shape[0]} linhas, {df.shape[1]} colunas.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"{SNOWFLAKE_TABLE}_{timestamp}.csv")

    df.to_csv(output_path, index=False)
    print(f"Arquivo salvo: {output_path}")

except Exception as e:
    print(f"Erro: {e}")
finally:
    conn.close()
