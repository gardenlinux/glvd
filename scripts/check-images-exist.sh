#!/bin/bash
set -e

# Get the today's version number
# GLVD versions follow the calver schema - year - month - day
GLVD_VERSION_TODAY=$(date +%Y.%m.%d)
echo $GLVD_VERSION_TODAY

IMAGES=(
  "ghcr.io/gardenlinux/glvd-postgres:$GLVD_VERSION_TODAY"
  "ghcr.io/gardenlinux/glvd-api:$GLVD_VERSION_TODAY"
  "ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY"
)

for img in "${IMAGES[@]}"; do
  if ! podman manifest inspect "$img" &>/dev/null; then
    echo "ERROR: Image $img does not exist." >&2
  fi
done
