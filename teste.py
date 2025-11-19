import mlflow

print("Version:", mlflow.__version__)

mlflow.set_tracking_uri("http://localhost:5000")

with mlflow.start_run():
    mlflow.log_param("x", 42)
    mlflow.log_metric("acc", 0.99)

print("OK!")
