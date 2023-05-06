# build vue
FROM node:18.12.1-alpine3.17 as build-vue
WORKDIR /app
COPY ./frontend/package*.json .
RUN npm install
COPY ./frontend .
RUN npm run build


FROM nginxinc/nginx-unprivileged:1.24-alpine
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-vue /app/dist /usr/share/nginx/html

# Only contains nginx and the frontend. Is the only entrypoint to the schoco-network!
# Used to filter incoming traffic to ONLY (!!!) allow websocket-container-attachment to /var/run/docker.sock.