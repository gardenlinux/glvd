# How to release a new version of glvd

glvd consists of several components, each packaged as a separate container image.  
Before releasing glvd itself, you must release all of its components.  
Each component has its own repository and release workflow.

## Perform releases of components

Trigger the release workflow for each component repository.  
The release version is set automatically, no manual steps are needed.

```bash
gh workflow run release.yaml --repo gardenlinux/glvd-api
gh workflow run release.yaml --repo gardenlinux/glvd-postgres
gh workflow run release.yaml --repo gardenlinux/glvd-data-ingestion
```

### Check releases

Check that all component's release images exist:

```bash
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
    exit 1
  fi
done
```

If the script succeeds, it will print only the version number. If any image is missing, an error message will be displayed and the script will exit with a non-zero status.

#### Error handling

Release failures are rare, but OCI image pushes can occasionally fail.

If a release fails in any repository, follow these steps to recover:

1. If a simple re-run does not resolve the issue, apply the necessary fix to the `main` branch.
2. Delete the corresponding GitHub release.
3. Remove the associated git tag for the failed release.
4. Delete the release branch.
5. Re-run the release workflow.

This ensures a clean state before attempting the release again.

## Perform release of the main project

After all components have been successfully released, you can release the main glvd project:

```bash
gh workflow run release.yaml --repo gardenlinux/glvd
```

## Upgrade prod cluster to the new release

To upgrade an existing cluster, ensure that you use the correct image tag everywhere. Image tags are based on the current date and are created by the release workflows you triggered earlier. Before proceeding, double-check that all release workflows completed successfully, as any failed workflow will prevent the upgrade from working.

```bash
# Ensure you target the desired cluster
export KUBECONFIG=/path/to/prod-cluster.yaml

# Get the today's version number
# GLVD versions follow the calver schema - year - month - day
GLVD_VERSION_TODAY=$(date +%Y.%m.%d)
echo $GLVD_VERSION_TODAY

# Test if release images exist
podman manifest inspect ghcr.io/gardenlinux/glvd-postgres:$GLVD_VERSION_TODAY > /dev/null ; echo $?
podman manifest inspect ghcr.io/gardenlinux/glvd-api:$GLVD_VERSION_TODAY > /dev/null ; echo $?
podman manifest inspect ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY > /dev/null ; echo $?

# Migrate the DB schema to the latest version
# Can't use dots in the name, so use date with dashes instead
kubectl -n glvd run db-migration-rel-$(date +%Y-%m-%d) --restart='Never' --image=ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY --env=DATABASE_URL=postgres://glvd:$(kubectl -n glvd get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)@glvd-database-0.glvd-database:5432/glvd -- python3 /usr/local/src/bin/migrate-all

# Update the container images
kubectl --namespace glvd set image sts/glvd-database glvd-postgres=ghcr.io/gardenlinux/glvd-postgres:$GLVD_VERSION_TODAY
kubectl --namespace glvd set image deploy/glvd glvd-api=ghcr.io/gardenlinux/glvd-api:$GLVD_VERSION_TODAY-linuxamd64_bare
kubectl --namespace glvd set image cj/glvd-ingestion data-ingestion=ghcr.io/gardenlinux/glvd-data-ingestion:$GLVD_VERSION_TODAY
```
