#!/bin/bash

# Stop and remove glvd_ingestion container
if podman inspect glvd_ingestion &> /dev/null; then
    podman stop glvd_ingestion
    podman rm glvd_ingestion
    echo "Container glvd_ingestion stopped and removed."
else
    echo "Container glvd_ingestion not found."
fi

# Stop and remove glvd_postgres container
if podman inspect glvd_postgress &> /dev/null; then
    podman stop glvd_postgress
    podman rm glvd_postgress
    echo "Container glvd_postgres stopped and removed."
else
    echo "Container glvd_postgres not found."
fi

# Stop and remove glvd_api container
if podman inspect glvd_api &> /dev/null; then
    podman stop glvd_api
    podman rm glvd_api
    echo "Container glvd_api stopped and removed."
else
    echo "Container glvd_api not found."
fi

