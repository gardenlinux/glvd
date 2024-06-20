#!/bin/bash

if [[ -z "$1" || -z "$2" ]]; then
    echo "Error: Please provide the glvd API container image name/tag and the password for the PostgreSQL user."
    exit 1
fi

api_image="$1"  # The glvd API container image to use
postgres_password="$2"  # Password for PostgreSQL user


podman run -d --name glvd_ingestion \
    --network host \
    --entrypoint "" \
    -e PGPASSWORD="$postgres_password" \
    -e PGUSER=glvd \
    -e PGDATABASE=glvd \
    ${api_image} /bin/sh -c 'glvd-data ingest-nvd'


echo "all done."

