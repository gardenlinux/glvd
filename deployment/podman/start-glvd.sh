#!/bin/bash
set -e

# Alternative option to compose file, avoiding the dependency on Docker Compose

# Create network if not exists
if ! podman network exists glvd; then
  podman network create glvd
fi

# Create volume if not exists
if ! podman volume exists glvd_db_volume; then
  podman volume create glvd_db_volume
fi

# Start Postgres
podman run -d \
  --name glvd-postgres \
  --network glvd \
  --hostname glvd-postgres \
  -e POSTGRES_USER=glvd \
  -e POSTGRES_DB=glvd \
  -e POSTGRES_PASSWORD=glvd \
  -v glvd_db_volume:/var/lib/postgresql \
  -p 5432:5432 \
  ghcr.io/gardenlinux/glvd-postgres:2026.02.25

# Wait for Postgres to be healthy
echo "Waiting for Postgres to be ready..."
until podman exec glvd-postgres pg_isready -U glvd -d glvd; do
  sleep 2
done

# Start glvd-init (one-shot)
podman run --rm \
  --name glvd-init \
  --network glvd \
  -e PGHOST=glvd-postgres \
  ghcr.io/gardenlinux/glvd-init:2026.02.25

# Give init some time to complete
sleep 15

# Start API
podman run -d \
  --name glvd-api \
  --network glvd \
  --hostname glvd \
  -e SPRING_DATASOURCE_URL="jdbc:postgresql://glvd-postgres:5432/glvd" \
  -e SPRING_DATASOURCE_USERNAME="glvd" \
  -e SPRING_DATASOURCE_PASSWORD="glvd" \
  -e SPRING_JPA_DATABASEPLATFORM="org.hibernate.dialect.PostgreSQLDialect" \
  -e SPRING_JPA_PROPERTIES_HIBERNATE_BOOT_ALLOW_JDBC_METADATA_ACCESS="false" \
  -e SPRING_JPA_HIBERNATE_DDLAUTO="none" \
  -e SPRING_SQL_INIT_MODE="never" \
  -p 8080:8080 \
  ghcr.io/gardenlinux/glvd-api:2026.02.25

echo "GLVD stack started with podman."
echo "Open http://localhost:8080 to interact with the web ui"
