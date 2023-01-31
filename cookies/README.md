COOKIES stands for <ins>**Co**</ins>mpile <ins>**o**</ins>nline, <ins>**k**</ins>eep <ins>**i**</ins>ts <ins>**e**</ins>xecution <ins>**s**</ins>upervised

Cookies is the docker-image, which will run in multiple instances and do the actual Java compilation and execution work of schoco. For each compilation and execution there's a new container-instance used (TODO: perhaps we can keep the same containers running at least for the compilation!!). Cookies itself is hardly useful and is tighlty coupled to schoco.

It is based on [codeboard-mantra](https://github.com/codeboardio/mantra), but works slightly different concerning the creation, starting and stopping of the containers:

- Create and start at least one container to keep it fully ready to start working. Creating and starting takes roughly around 0.3 seconds. We can save this time for each single compilation/execution when we do not wait with starting a container until a new command is coming in. Instead the container is already running, gets prepared for the specific command, and then the command gets executed (using the API inside the container - written in Java, see /api).