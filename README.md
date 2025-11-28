# AVD - Projeto de Machine Learning para Previsão de Umidade Relativa

**Disciplina**: Análise e Visualização de Dados - 2025.2  
**Instituição**: CESAR School  
**Problema Escolhido**: 7.6 - Prever Umidade Relativa

## 👥 Equipe

<!-- ADICIONE AQUI OS NOMES E USUÁRIOS DO GITHUB DOS MEMBROS DO GRUPO -->
<!-- Exemplo: -->
<!-- - Nome Completo (@usuario_github) -->
<!-- - Nome Completo (@usuario_github) -->

---

Projeto de Machine Learning para previsão de umidade relativa do ar utilizando dados meteorológicos do INMET (Instituto Nacional de Meteorologia). O projeto utiliza Random Forest para modelagem e MLflow para tracking de experimentos, com infraestrutura containerizada via Docker Compose.

## 📋 Índice

- [Equipe](#-equipe)
- [Descrição](#-descrição)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Configuração Inicial](#-configuração-inicial)
- [Execução do Projeto](#-execução-do-projeto)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Troubleshooting](#-troubleshooting)

## 🎯 Descrição

Este projeto processa dados meteorológicos de estações do Nordeste do Brasil (INMET) e treina modelos de Machine Learning para prever a umidade relativa do ar. O sistema inclui:

- **Processamento de dados**: Limpeza e preparação de dados meteorológicos
- **Treinamento de modelos**: Random Forest Regressor com pipeline de pré-processamento
- **Tracking de experimentos**: MLflow para versionamento e comparação de modelos
- **Armazenamento**: MinIO (S3-compatible) para artefatos e MySQL para metadados
- **API**: FastAPI para upload de dados para S3
- **Integração**: Snowflake para armazenamento de dados processados

## 🏗️ Arquitetura

O projeto utiliza Docker Compose para orquestrar os seguintes serviços:

- **FastAPI**: Interface de ingestão dos dados do INMET e integração com S3
- **MinIO**: Armazenamento de dados brutos e modelos (S3-compatible)
- **Snowflake**: Estruturação de dados tratados (configuração via variáveis de ambiente)
- **Jupyter**: Ambiente de análise, limpeza e modelagem preditiva
- **MLflow**: Registro e versionamento dos modelos de ML
- **MySQL**: Banco de dados para metadados do MLflow

### Fluxo do Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  MinIO/S3   │────▶│  Snowflake  │────▶│   Jupyter   │
│  (Ingestão) │     │ (Armazen.)  │     │ (Estrutura)  │     │ (Modelagem) │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                      │
                                                                      ▼
                                                               ┌─────────────┐
                                                               │   MLflow    │
                                                               │  (Tracking) │
                                                               └──────┬──────┘
                                                                      │
                                                                      ▼
                                                               ┌─────────────┐
                                                               │    MinIO    │
                                                               │  (Artifacts) │
                                                               └─────────────┘
```

**Fluxo completo:**

1. FastAPI recebe dados do INMET (API/CSV) e armazena em S3/MinIO
2. Dados são estruturados em Snowflake
3. Jupyter Notebook lê da base estruturada, trata e treina um modelo
4. Modelo é versionado no MLflow e exportado novamente para S3/MinIO
5. Dashboard (ThingsBoard/Trendz) consome os dados e mostra visualizações

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git** (para clonar o repositório)

### Verificar instalação

```bash
docker --version
docker-compose --version
git --version
```

## ⚙️ Configuração Inicial

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd avd-projeto
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure as variáveis:

```bash
cp .env-example .env
```

Edite o arquivo `.env` e preencha as seguintes variáveis:

#### Variáveis obrigatórias (para funcionamento local):

```env
# MinIO (armazenamento local)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY_ID=minioadmin
MINIO_SECRET_ACCESS_KEY=minioadmin

# MySQL
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mlflow
MYSQL_USER=mlflow_user
MYSQL_PASSWORD=mlflow_pass

# MLflow
MLFLOW_MINIO_ENDPOINT_URL=http://minio:9000
MLFLOW_ARTIFACT_BUCKET=mlflow
MLFLOW_BACKEND_URI=mysql+pymysql://mlflow_user:mlflow_pass@mysql:3306/mlflow
```

#### Variáveis opcionais (para integração com AWS/Snowflake):

```env
# AWS (para upload para S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=
S3_BUCKET=
S3_PATH=

# Snowflake (para fetch de dados)
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_TABLE=
```

> **Nota**: As variáveis do MinIO e MySQL acima são suficientes para executar o projeto localmente. As variáveis da AWS e Snowflake são necessárias apenas se você quiser usar essas integrações.

## 🚀 Execução do Projeto

### Passo 1: Iniciar os containers

No diretório raiz do projeto, execute:

```bash
docker-compose up -d
```

Este comando irá:

- Construir as imagens Docker necessárias
- Iniciar todos os serviços (Jupyter, MLflow, MinIO, MySQL)
- Configurar os buckets do MinIO automaticamente

### Passo 2: Verificar se os serviços estão rodando

```bash
docker-compose ps
```

Todos os containers devem estar com status `Up`. Você deve ver:

- `jupyter_app` (porta 8888)
- `mlflow` (porta 5000)
- `minio` (portas 9000 e 9001)
- `mysql` (porta 13308)
- `fastapi_app` (porta 8000)

### Passo 3: Acessar os serviços

Após alguns segundos, os serviços estarão disponíveis:

- **Jupyter Notebook**: http://localhost:8888
- **MLflow UI**: http://localhost:5000
- **MinIO Console**: http://localhost:9001
  - Usuário: `minioadmin`
  - Senha: `minioadmin`
- **FastAPI**: http://localhost:8000
- **MySQL**: `localhost:13308`

### Passo 4: Executar o notebook de treinamento

1. Acesse o Jupyter em http://localhost:8888
2. Navegue até `model_training.ipynb`
3. Execute todas as células (Menu: `Cell` → `Run All` ou `Shift+Enter` em cada célula)

O notebook irá:

- Carregar os dados processados
- Treinar um modelo Random Forest
- Registrar o experimento no MLflow
- Salvar artefatos (modelo e predições) no MinIO

## 📖 Como Usar

### Treinar um modelo

1. **Preparar os dados**: Certifique-se de que o arquivo CSV processado está em `/data/processed/`
2. **Abrir o notebook**: Acesse `model_training.ipynb` no Jupyter
3. **Ajustar parâmetros** (opcional):
   - `FILE_PATH`: Caminho do arquivo CSV
   - `FEATURES`: Features utilizadas no modelo
   - `TARGET`: Variável alvo
4. **Executar**: Execute todas as células do notebook

### Visualizar experimentos no MLflow

1. Acesse http://localhost:5000
2. Navegue até o experimento "Default"
3. Clique em um run para ver:
   - Parâmetros do modelo
   - Métricas (MAE, etc.)
   - Artefatos (modelo treinado, CSV de predições)

### Upload de dados para S3 (opcional)

Se você configurou as credenciais AWS:

```bash
curl -X POST "http://localhost:8000/upload"
```

Ou use o script de pipeline:

```bash
bash scripts/pipeline.sh --upload
```

### Processar dados do Snowflake (opcional)

Se você configurou as credenciais do Snowflake:

```bash
docker-compose exec jupyter python /scripts/fetch_from_snowflake.py
```

## 📁 Estrutura do Projeto

```
avd-projeto/
├── data/                          # Dados do projeto
│   ├── raw/                       # Dados brutos
│   ├── processed/                 # Dados processados
│   └── artifacts/                 # Modelos e predições gerados
├── jupyter_app/                   # Container Jupyter (jupyterlab/)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── notebooks/                 # Notebooks de tratamento e modelagem
│       ├── model_training.ipynb   # Notebook principal de treinamento
│       ├── eda.ipynb              # Análise exploratória
│       └── mae_analysis.ipynb     # Análise de métricas
├── mlflow_app/                    # Container MLflow (mlflow/)
│   ├── Dockerfile
│   └── requirements.txt
├── fastapi_app/                   # Container FastAPI (fastapi/)
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── scripts/                        # Scripts auxiliares
│   ├── pipeline.sh                # Script de pipeline completo
│   ├── fetch_from_snowflake.py    # Fetch de dados do Snowflake
│   ├── process_and_merge_datasets.py  # Processamento de datasets
│   └── snowflake_script_adaptado.sql  # Script SQL do Snowflake
├── sql_scripts/                    # Scripts SQL de estruturação e consultas
│   └── (a criar)
├── trendz/                         # Dashboards exportados do Trendz
│   └── (a criar)
├── reports/                        # Relatórios e resultados
│   └── (relatório técnico em PDF a criar)
├── docker-compose.yml             # Orquestração dos contêineres
├── .env-example                   # Exemplo de variáveis de ambiente
├── README.md                      # Este arquivo
└── LICENSE                        # Licença do projeto
```

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'sklearn'"

**Solução**: Reconstrua o container do Jupyter:

```bash
docker-compose build jupyter
docker-compose up -d jupyter
```

### Erro: "Access Denied" ao salvar artefatos no MLflow

**Solução**: Verifique se as variáveis de ambiente estão configuradas corretamente:

```bash
docker-compose exec jupyter env | grep -E "AWS_|MLFLOW_"
```

Certifique-se de que:

- `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` estão configurados
- `MLFLOW_S3_ENDPOINT_URL` está sem barra no final

### Erro: "Invalid Host header" no MLflow

**Solução**: O MLflow já está configurado com `--allowed-hosts`. Se o erro persistir, verifique os logs:

```bash
docker-compose logs mlflow
```

### Container não inicia

**Solução**: Verifique os logs do container:

```bash
docker-compose logs <nome-do-container>
```

Exemplos:

```bash
docker-compose logs jupyter
docker-compose logs mlflow
docker-compose logs mysql
```

### Porta já em uso

**Solução**: Pare outros serviços que possam estar usando as portas ou altere as portas no `docker-compose.yml`.

### Limpar tudo e começar do zero

```bash
# Parar e remover containers
docker-compose down

# Remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reconstruir tudo
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Funcionamento Básico

### Fluxo de Dados

1. **Dados brutos** → `data/raw/` ou `data/2023/`, `data/2024/`
2. **Processamento** → Scripts em `scripts/` processam e limpam os dados
3. **Dados processados** → `data/processed/concatenado_clean_*.csv`
4. **Treinamento** → Notebook `model_training.ipynb` treina o modelo
5. **Registro** → MLflow registra parâmetros, métricas e artefatos
6. **Armazenamento** → Artefatos salvos no MinIO e metadados no MySQL

### Modelo de Machine Learning

- **Algoritmo**: Random Forest Regressor
- **Features**: Temperatura do bulbo seco, Pressão atmosférica, Radiação global
- **Target**: Umidade relativa do ar
- **Métrica**: MAE (Mean Absolute Error)
- **Pré-processamento**: StandardScaler

### Artefatos Gerados

Após executar o notebook, você terá:

- `rf_model.pkl`: Modelo treinado
- `predictions_partial.csv`: Predições do conjunto de teste
- `predictions_full.csv`: Predições do conjunto completo
- Registro completo no MLflow com histórico de experimentos

## 📝 Notas Importantes

- O projeto usa **MinIO local** para armazenamento de artefatos (não requer AWS)
- O **MySQL** armazena apenas metadados do MLflow (experimentos, runs, etc.)
- Os **dados processados** devem estar em `/data/processed/` dentro do container
- O **Jupyter** não requer autenticação (token vazio) para facilitar o desenvolvimento
- Todos os serviços estão na mesma rede Docker (`app-net`)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido para o projeto AVD - CESAR School - 2025.2**
