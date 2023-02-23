# build vue
FROM node:18.12.1-alpine3.17 as build-vue
WORKDIR /app
COPY ./frontend/package*.json .
RUN npm install
COPY ./frontend .
RUN npm run build


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim
COPY ./fastapi/requirements.txt /app/requirements.txt
RUN apt update && \
    apt install -y nginx libcurl4-openssl-dev libssl-dev gcc && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt
## TODO directly uninstall gcc again??
COPY ./fastapi/java_helloWorld /app/java_helloWorld
COPY ./fastapi/*.py /app

#USER nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build-vue /app/dist /usr/share/nginx/html
COPY ./schoco-start.sh /schoco-start.sh
#CMD nginx -g 'daemon off;'
CMD /schoco-start.sh



# Only contains nginx until now. 
# Used to filter incoming traffic to ONLY (!!!) allow websocket-container-attachment to /var/run/docker.sock.

#FROM alpine:3.17

#RUN apk add --no-cache nginx
#USER nginx
#COPY nginx/nginx.conf /etc/nginx/nginx.conf

#CMD nginx -g 'daemon off;'