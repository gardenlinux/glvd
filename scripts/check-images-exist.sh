#!/bin/bash
set -e

# Assert podman is running (especially important on macOS/Windows)
if ! podman info &>/dev/null; then
  echo "ERROR: podman is not running or not available. On macOS/Windows, ensure the podman VM is started (e.g., 'podman machine start')." >&2
  exit 1
fi

# Get the today's version number
# GLVD versions follow the calver schema - year - month - day
GLVD_VERSION_TODAY=$(date +%Y.%m.%d)
echo $GLVD_VERSION_TODAY

IMAGES=(
  "ghcr.io/gardenlinux/glvd-postgres:$GLVD_VERSION_TODAY"
  "ghcr.io/gardenlinux/glvd-api:$GLVD_VERSION_TODAY"
  "ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY"
)

# If GITHUB_TOKEN is set, use it for registry authentication
if [[ -n "$GITHUB_TOKEN" ]]; then
  export REGISTRY_AUTH_FILE=$(mktemp)
  echo "{\"auths\": {\"ghcr.io\": {\"auth\": \"$(echo -n "USERNAME:$GITHUB_TOKEN" | base64)\"}}}" > "$REGISTRY_AUTH_FILE"
  AUTH_OPT="--authfile $REGISTRY_AUTH_FILE"
else
  AUTH_OPT=""
fi

for img in "${IMAGES[@]}"; do
  output=$(podman manifest inspect $AUTH_OPT "$img" 2>&1)
  if [[ $? -ne 0 ]]; then
    if echo "$output" | grep -q "403 Forbidden"; then
      echo "ERROR: Access denied (403 Forbidden) for image $img. Check your GITHUB_TOKEN permissions or authentication setup." >&2
    else
      echo "ERROR: Image $img does not exist or could not be inspected." >&2
      echo "Detail: $output" >&2
    fi
  fi
done

# Clean up temp auth file if used
cleanup() {
  if [[ -n "$REGISTRY_AUTH_FILE" ]]; then
    rm -f "$REGISTRY_AUTH_FILE"
  fi
}
trap cleanup EXIT
