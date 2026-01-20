#!/bin/bash
set -e

# Get the today's version number
# GLVD versions follow the calver schema - year - month - day
GLVD_VERSION_TODAY=$(date +%Y.%m.%d)
echo $GLVD_VERSION_TODAY

# Migrate the DB schema to the latest version
# Can't use dots in the name, so use date with dashes instead
kubectl -n glvd run db-migration-rel-$(date +%Y-%m-%d) --restart='Never' --image=ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY --env="DATABASE_URL=postgres://glvd:$(kubectl -n glvd get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)@glvd-database-0.glvd-database:5432/glvd" -- python3 /usr/local/src/bin/migrate-all
sleep 20
kubectl -n glvd logs db-migration-rel-$(date +%Y-%m-%d)

# Update the container images
kubectl --namespace glvd set image sts/glvd-database glvd-postgres=ghcr.io/gardenlinux/glvd-postgres:$GLVD_VERSION_TODAY
sleep 10

kubectl --namespace glvd set image deploy/glvd glvd-api=ghcr.io/gardenlinux/glvd-api:$GLVD_VERSION_TODAY-linuxamd64_bare
sleep 10

kubectl --namespace glvd set image cj/glvd-ingestion data-ingestion=ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY

kubectl --namespace glvd logs deploy/glvd
