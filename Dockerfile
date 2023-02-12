# Only contains nginx until now. 
# Used to filter incoming traffic to ONLY (!!!) allow websocket-container-attachment to /var/run/docker.sock.

#FROM alpine:3.17
FROM nginx:1.23.3-alpine-slim

#RUN apk add --no-cache nginx
#USER nginx
#COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

CMD nginx -g 'daemon off;'