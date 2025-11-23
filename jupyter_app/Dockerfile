FROM jupyter/base-notebook:latest

WORKDIR /home/jovyan/work

USER root
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER $NB_UID

EXPOSE 8888

CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.notebook_dir=/home/jovyan/work"]