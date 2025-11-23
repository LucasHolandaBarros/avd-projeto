FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "mysql+pymysql://mlflow:mlflow@mlflow-db:3306/mlflow", \
     "--default-artifact-root", "s3://mlflow-artifacts", \
     "--host", "0.0.0.0", "--port", "5000"]
