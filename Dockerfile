FROM debian:bullseye-slim

LABEL maintainer="Alistair Young <avatar@arkane-systems.net>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y reprepro gpg python3 python3-git python3-gnupg expect python3-debian

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python3", "/entrypoint.py"]
