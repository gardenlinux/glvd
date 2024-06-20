#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Error: Please provide the password for the PostgreSQL user."
    exit 1
fi

postgres_image="ghcr.io/gardenlinux/glvd-postgres:edge"
api_image="ghcr.io/gardenlinux/glvd:edge"
postgres_password="$1"  # Password for PostgreSQL user

read -p "Local Setup. Do not use for production. Confirm to continue. (y/N): " confirmation

confirmation=${confirmation:-N}

[[ "${confirmation,,}" != "y" ]] && { echo "Aborted."; exit 1; }


./start-postgres.sh $postgres_image $postgres_password
./start-api.sh $api_image $postgres_password
./start-ingestion.sh $api_image $postgres_password


echo "all done."

