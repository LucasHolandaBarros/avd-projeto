import pandas as pd
import glob

# Caminhos das pastas
caminhos = [
    "data/2023/*.csv",
    "data/2024/*.csv"
]

# Coletar todos os CSVs das duas pastas
todos_csvs = []
for caminho in caminhos:
    todos_csvs.extend(glob.glob(caminho))

print("Arquivos encontrados:", len(todos_csvs))

blocos = []

# Colunas que devem ser numéricas no Snowflake
colunas_numericas = [
    "PRECIPITACAO_TOTAL", "PR_ATM_EST", "PR_MAX_1H", "PR_MIN_1H",
    "RADIACAO_GLOBAL", "TEMP_BULBO_SECO", "TEMP_PONTO_ORVALHO",
    "TEMP_MAX_1H", "TEMP_MIN_1H", "ORVALHO_MAX_1H", "ORVALHO_MIN_1H",
    "UMID_REL_MAX_1H", "UMID_REL_MIN_1H", "UMIDADE_REL",
    "VENTO_DIRECAO", "VENTO_RAJADA_MAX", "VENTO_VELOCIDADE",
    "LATITUDE", "LONGITUDE", "ALTITUDE"
]

for arquivo in todos_csvs:
    print(f"\n📌 Lendo arquivo: {arquivo}")

    with open(arquivo, encoding='latin1') as f:
        linhas = f.read().splitlines()

    # Encontrar header real
    header_index = None
    for i, linha in enumerate(linhas):
        if linha.startswith("Data;Hora"):
            header_index = i
            break

    if header_index is None:
        print("⚠ Header não encontrado. Pulando arquivo.")
        continue

    colunas = linhas[header_index].split(";")
    dados = linhas[header_index+1:]

    # Criar dataframe do bloco
    try:
        df = pd.DataFrame([linha.split(";") for linha in dados], columns=colunas)
    except Exception as e:
        print("❌ Erro ao criar DataFrame:", e)
        continue

    # Metadados nas linhas anteriores ao header
    metadados = linhas[:header_index]
    for meta in metadados:
        if ":" in meta:
            chave, valor = meta.split(":", 1)
            df[chave.strip()] = valor.strip()

    # 🔹 Substituir vírgula por ponto e converter para float
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

    print("✔ Bloco adicionado:", df.shape)
    blocos.append(df)

# FINAL — concatena tudo
if not blocos:
    raise Exception("❌ Nenhum bloco foi carregado. Verifique os caminhos e headers.")

df_final = pd.concat(blocos, ignore_index=True)

# Salvar CSV final pronto para Snowflake
df_final.to_csv("data/csv_concatenado1.csv", index=False, encoding='utf-8', sep=';')

print("\n🎉 CSV final gerado com sucesso! Todos os números estão no formato correto (float).")
