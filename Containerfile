FROM docker.io/library/debian:trixie-slim

# XXX: Debian unstable required for python3-sqlalchemy (>= 2)
RUN sed -i -e 's/Suites: trixie trixie-updates/\0 unstable/' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends python3-asyncpg python3-pip python3-poetry-core python3-requests python3-sqlalchemy/unstable && \
    apt-get upgrade -y --no-install-recommends git curl debian-archive-keyring postgresql-client
COPY . /usr/local/src
RUN pip install --break-system-packages --no-deps --editable /usr/local/src
