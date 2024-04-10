#!/bin/bash

if [[ -z "$1" || -z "$2" ]]; then
    echo "Error: Please provide the glvd API container image name/tag and the password for the PostgreSQL user."
    exit 1
fi

api_image="$1"  # The glvd API container image to use
postgres_password="$2"  # Password for PostgreSQL user

read -p "Local Setup. Do not use for production. Confirm to continue. (y/N): " confirmation

confirmation=${confirmation:-N}

[[ "${confirmation,,}" != "y" ]] && { echo "Aborted."; exit 1; }



podman run -d --name glvd_api\
    -e PGPASSWORD="$postgres_password" \
    -e PGUSER=glvd \
    -e PGDATABASE=glvd \
    -p 8000:8000\
    "$api_image"

echo "all done."

