#!/bin/bash



podman stop glvd_ingestion
podman stop glvd_postgress
podman stop glvd_api

echo "Stopped glvd_ingestion, glvd_postgres, and glvd_api containers."
