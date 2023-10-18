FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim
COPY ./requirements.txt /app/requirements.txt
RUN apt-get update && \
    apt-get install -y libcurl4-openssl-dev libssl-dev gcc && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
COPY . /app
