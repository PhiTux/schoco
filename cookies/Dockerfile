FROM alpine:3.17

COPY cookies.sh /app/cookies.sh
COPY hamcrest-all-1.3.jar /app/hamcrest.jar
COPY api/*.class /

RUN apk add --no-cache openjdk8 junit libc6-compat bash \
    && chmod +x /app/cookies.sh

# The Entrypoint starts the minimum-API written in Java.
# The container just waits for commands via the API.
# When a /compile /run /test command is coming in, 
# then the cookies.sh-Script gets executed
ENTRYPOINT ["java", "Java_api"]
