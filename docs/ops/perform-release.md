# How to release a new version of glvd

## Perform releaes of components

Each of the component repos has its own release workflow.
The version number of a release is automatically determined.

```bash
gh workflow run release.yaml --repo gardenlinux/glvd-api
gh workflow run release.yaml --repo gardenlinux/glvd-postgres
gh workflow run release.yaml --repo gardenlinux/glvd-data-ingestion
```

## Perform release of the main project

Once all components created a release successfully, perform the release of glvd itself

```bash
gh workflow run release.yaml --repo gardenlinux/glvd
```

## Upgrade prod cluster to the new release

```bash
# Ensure you target the desired cluster
export KUBECONFIG=/path/to/prod-cluster.yaml

# Migrate the DB schema to the latest version
kubectl -n glvd run db-migration-rel-$(date +%Y-%m-%d) --restart='Never' --image=ghcr.io/gardenlinux/glvd-data-ingestion:$(date +%Y.%m.%d) --env=DATABASE_URL=postgres://glvd:$(kubectl -n glvd get secret/postgres-credentials --template="{{.data.password}}" | base64 -d)@glvd-database-0.glvd-database:5432/glvd -- python3 /usr/local/src/bin/migrate-all

# Update the container images
kubectl --namespace glvd set image sts/glvd-database glvd-postgres=ghcr.io/gardenlinux/glvd-postgres:$(date +%Y.%m.%d)
kubectl --namespace glvd set image deploy/glvd glvd-api=ghcr.io/gardenlinux/glvd-api:$(date +%Y.%m.%d)-linuxamd64_bare
kubectl --namespace glvd set image cj/glvd-ingestion data-ingestion=ghcr.io/gardenlinux/glvd-data-ingestion:$(date +%Y.%m.%d)
```
