# Only contains nginx until now. 
# Used to filter incoming traffic to ONLY (!!!) allow websocket-container-attachment to /var/run/docker.sock.

FROM alpine:3.17

RUN apk add --no-cache nginx
USER nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

CMD nginx -g 'daemon off;'