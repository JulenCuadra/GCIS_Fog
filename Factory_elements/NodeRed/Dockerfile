FROM nodered/node-red

RUN curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-amd64 -o kompose

RUN chmod +x kompose

USER root

RUN mv ./kompose /usr/local/bin/kompose

RUN npm install xmlhttprequest

COPY Application.xsd /xmlSchemas/Application.xsd

CMD node-red
