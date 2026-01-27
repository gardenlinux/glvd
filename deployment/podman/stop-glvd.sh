#!/bin/bash
set -e

# Stop and remove containers if they exist
for c in glvd-api glvd-init glvd-postgres; do
  if podman container exists "$c"; then
    echo "Stopping $c..."
    podman stop "$c" || true
    echo "Removing $c..."
    podman rm "$c" || true
  fi
done

# Remove network if it exists
if podman network exists glvd; then
  echo "Removing network glvd..."
  podman network rm glvd
fi

# Remove volume if it exists
if podman volume exists glvd_db_volume; then
  echo "Removing volume glvd_db_volume..."
  podman volume rm glvd_db_volume
fi

echo "GLVD podman environment cleaned up."
