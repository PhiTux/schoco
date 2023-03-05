FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim
COPY ./requirements.txt /app/requirements.txt
RUN apt-get update && \
    apt-get install -y nginx libcurl4-openssl-dev libssl-dev gcc && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt 
    #apt purge gcc
## TODO directly uninstall gcc again??
#COPY ./fastapi/java_helloWorld /app/java_helloWorld
#COPY ./fastapi/*.py /app
COPY . /app
