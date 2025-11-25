-- 1. Database a se utilizar

USE DATABASE SNOWFLAKE_LEARNING_DB;

USE SCHEMA PUBLIC;



-- FILE FORMAT compatível com o novo CSV (separador: vírgula, decimais já convertidos)

CREATE OR REPLACE FILE FORMAT my_csv_format

TYPE = 'CSV'

FIELD_DELIMITER = ','

SKIP_HEADER = 1

TRIM_SPACE = TRUE

NULL_IF = ('', 'NULL', 'NA', 'na')

EMPTY_FIELD_AS_NULL = TRUE

ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;





-- TABELA FINAL COM 20 COLUNAS (incluindo ESTACAO)

CREATE OR REPLACE TABLE csv_concatenado (

    estacao VARCHAR,

    data VARCHAR,

    hora_utc VARCHAR,

    precipitacao_total FLOAT,

    pressao_atm_est FLOAT,

    pressao_max_1h FLOAT,

    pressao_min_1h FLOAT,

    radiacao_global FLOAT,

    temperatura_bulbo_seco FLOAT,

    temperatura_ponto_orvalho FLOAT,

    temperatura_max_1h FLOAT,

    temperatura_min_1h FLOAT,

    orvalho_max_1h FLOAT,

    orvalho_min_1h FLOAT,

    umidade_rel_max_1h FLOAT,

    umidade_rel_min_1h FLOAT,

    umidade_rel FLOAT,

    vento_direcao FLOAT,

    vento_rajada_max FLOAT,

    vento_velocidade FLOAT

);



-- STREAM

CREATE OR REPLACE STREAM concatenado_stream 

ON TABLE csv_concatenado;



-- PIPE ADAPTADO PARA 20 COLUNAS (decimais já convertidos, sem necessidade de REPLACE)

CREATE OR REPLACE PIPE concatenado_pipe

AUTO_INGEST = TRUE

AS

COPY INTO csv_concatenado

FROM (

    SELECT

        $1 AS estacao,

        $2 AS data,

        $3 AS hora_utc,

        $4::FLOAT AS precipitacao_total,

        $5::FLOAT AS pressao_atm_est,

        $6::FLOAT AS pressao_max_1h,

        $7::FLOAT AS pressao_min_1h,

        $8::FLOAT AS radiacao_global,

        $9::FLOAT AS temperatura_bulbo_seco,

        $10::FLOAT AS temperatura_ponto_orvalho,

        $11::FLOAT AS temperatura_max_1h,

        $12::FLOAT AS temperatura_min_1h,

        $13::FLOAT AS orvalho_max_1h,

        $14::FLOAT AS orvalho_min_1h,

        $15::FLOAT AS umidade_rel_max_1h,

        $16::FLOAT AS umidade_rel_min_1h,

        $17::FLOAT AS umidade_rel,

        $18::FLOAT AS vento_direcao,

        $19::FLOAT AS vento_rajada_max,

        $20::FLOAT AS vento_velocidade

    FROM @my_s3_stage

)

FILE_FORMAT = (FORMAT_NAME = my_csv_format);



SELECT SYSTEM$PIPE_STATUS('concatenado_pipe');



-- TABELA CLEAN

CREATE OR REPLACE TABLE concatenado_clean LIKE csv_concatenado;



-- TASK ADAPTADA PARA 20 COLUNAS (incluindo ESTACAO)

CREATE OR REPLACE TASK concatenado_task

WAREHOUSE = compute_wh

SCHEDULE = '1 MINUTE'

AS

MERGE INTO concatenado_clean AS ctc

USING (

    SELECT *

    FROM concatenado_stream

    WHERE NOT (

        precipitacao_total IS NULL AND

        pressao_atm_est IS NULL AND

        radiacao_global IS NULL AND

        temperatura_bulbo_seco IS NULL AND

        temperatura_ponto_orvalho IS NULL AND

        umidade_rel IS NULL AND

        vento_direcao IS NULL AND

        vento_velocidade IS NULL

    )

) AS src

ON ctc.estacao = src.estacao

AND ctc.data = src.data

AND ctc.hora_utc = src.hora_utc



WHEN NOT MATCHED THEN

INSERT VALUES (

    src.estacao,

    src.data,

    src.hora_utc,

    src.precipitacao_total,

    src.pressao_atm_est,

    src.pressao_max_1h,

    src.pressao_min_1h,

    src.radiacao_global,

    src.temperatura_bulbo_seco,

    src.temperatura_ponto_orvalho,

    src.temperatura_max_1h,

    src.temperatura_min_1h,

    src.orvalho_max_1h,

    src.orvalho_min_1h,

    src.umidade_rel_max_1h,

    src.umidade_rel_min_1h,

    src.umidade_rel,

    src.vento_direcao,

    src.vento_rajada_max,

    src.vento_velocidade

);



ALTER TASK concatenado_task RESUME;



SHOW STAGES LIKE 'my_s3_stage';



SHOW PIPES;



SHOW INTEGRATIONS;



SELECT * FROM csv_concatenado LIMIT 10;



LIST @my_s3_stage;



SELECT *

FROM

    TABLE(SNOWFLAKE.INFORMATION_SCHEMA.COPY_HISTORY(

        TABLE_NAME => 'csv_concatenado',

        START_TIME => DATEADD(HOUR, -24, CURRENT_TIMESTAMP())

    ))

ORDER BY

    LAST_LOAD_TIME DESC;

