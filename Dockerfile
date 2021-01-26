FROM debian:buster

LABEL maintainer="Alistair Young <avatar@arkane-systems.net>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y reprepro gpg python3 python3-git python3-gnupg expect python3-debian

ENTRYPOINT ["python3"]
