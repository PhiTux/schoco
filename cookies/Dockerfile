From alpine:3.17

COPY cookies.sh /app/cookies.sh

RUN apk add --no-cache openjdk8 junit libc6-compat bash \
    #&& groupadd -r cookies \
    #&& useradd -r -s /bin/false -g cookies cookies \
    && chown 1234:1234 /app/cookies.sh

# The individual CMD gets set on the running container with EXEC
ENTRYPOINT ["tail", "-f", "/dev/null"]