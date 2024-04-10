#!/bin/bash

if [[ -z "$1" || -z "$2" ]]; then
    echo "Error: Please provide the PostgreSQL container image name/tag and the password for the PostgreSQL user."
    exit 1
fi

postgres_image="$1"  # The PostgreSQL container image to use
postgres_password="$2"  # Password for PostgreSQL user

read -p "Local Setup. Do not use for production. Confirm to continue. (y/N): " confirmation

confirmation=${confirmation:-N}

[[ "${confirmation,,}" != "y" ]] && { echo "Aborted."; exit 1; }



podman run -d --name glvd_postgress\
    -e POSTGRES_PASSWORD="$postgres_password" \
    -e POSTGRES_USER=glvd \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -p 5432:5432 \
    "$postgres_image"

echo "all done."

