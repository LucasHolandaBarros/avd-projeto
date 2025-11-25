import pandas as pd
import glob

# -----------------------------
# Configurações
# -----------------------------
caminhos = [
    "data/2023/Garanhuns.csv",
    "data/2024/Garanhuns.csv"
]

# Colunas que devem ser numéricas no Snowflake
colunas_numericas = [
    "PRECIPITACAO_TOTAL", "PR_ATM_EST", "PR_MAX_1H", "PR_MIN_1H",
    "RADIACAO_GLOBAL", "TEMP_BULBO_SECO", "TEMP_PONTO_ORVALHO",
    "TEMP_MAX_1H", "TEMP_MIN_1H", "ORVALHO_MAX_1H", "ORVALHO_MIN_1H",
    "UMID_REL_MAX_1H", "UMID_REL_MIN_1H", "UMIDADE_REL",
    "VENTO_DIRECAO", "VENTO_RAJADA_MAX", "VENTO_VELOCIDADE",
    "LATITUDE", "LONGITUDE", "ALTITUDE"
]

# Colunas que podem conter ; ou " dentro dos dados
colunas_sujas = [
    "REGIAO","UF","ESTACAO","CODIGO (WMO)",
    "LATITUDE","LONGITUDE","ALTITUDE","DATA DE FUNDACAO"
]

# -----------------------------
# Coletar todos os CSVs
# -----------------------------
todos_csvs = []
for caminho in caminhos:
    todos_csvs.extend(glob.glob(caminho))

print("📂 Arquivos encontrados:", len(todos_csvs))

blocos = []

# -----------------------------
# Processar cada CSV
# -----------------------------
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

    # -----------------------------
    # Criar DataFrame
    # -----------------------------
    dados_limpos = []
    for linha in dados:
        # remover aspas e espaços extras, mas não os ; delimitadores
        linha = linha.replace('"', '').strip()
        dados_limpos.append(linha)

    try:
        df = pd.DataFrame([linha.split(";") for linha in dados_limpos], columns=colunas)
    except Exception as e:
        print("❌ Erro ao criar DataFrame:", e)
        continue

    # -----------------------------
    # Limpar ; dentro das células “sujas”
    # -----------------------------
    for col in colunas_sujas:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.replace(';','').strip() if isinstance(x,str) else x)

    # -----------------------------
    # Converter colunas numéricas
    # -----------------------------
    for col in colunas_numericas:
        if col in df.columns:
            # substitui vírgula por ponto e converte qualquer valor para float, mesmo vazios
            df[col] = df[col].apply(lambda x: float(str(x).replace(',', '.')) if x not in [None,''] else None)

    blocos.append(df)
    print("✔ Bloco adicionado:", df.shape)

# -----------------------------
# Concatenar todos os blocos
# -----------------------------
if not blocos:
    raise Exception("❌ Nenhum bloco foi carregado. Verifique os arquivos CSV.")

df_final = pd.concat(blocos, ignore_index=True)

# -----------------------------
# Salvar CSV final
# -----------------------------
df_final.to_csv("data/csv_concatenado1.csv", index=False, encoding='utf-8', sep=';')

print("\n🎉 CSV final gerado com sucesso! Todos os números estão no formato correto (float com ponto).")
