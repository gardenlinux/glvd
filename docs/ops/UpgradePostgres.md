# Postgres Upgrades

Upgrading postgres from one major version to another (16 to 17, or 17 to 18) is not as simple as replacing the container.

This document describes a rough workflow that should work with the glvd setup (where postgres is run in a stateful set).

```bash
# Scale to zero so we can delete the sts
kubectl scale sts/glvd-database --replicas=0
# Delete sts
kubectl delete -f deployment/k8s/00_db-statefulset.yaml
# edit the manifest to have a new volume mounted at /backup
# Re-crate sts with backup volume mounted
kubectl apply -f deployment/k8s/00_db-statefulset.yaml
# open shell in db container
kubectl exec -it glvd-database-0 -- bash
# dump db on backup volume
pg_dump -v -p 5432 -U glvd -d glvd --format=custom -f /backup/glvd.dump
# Scale to zero so we can delete the sts
kubectl scale sts/glvd-database --replicas=0
# Delete sts with old pg version
kubectl delete -f deployment/k8s/00_db-statefulset.yaml

# crate sts with new version, with backup volume and *new* data volume
# note that there might be breaking changes, for example in pg 18 the PGDATA env var behaves differently
kubectl apply -f deployment/k8s/00_db-statefulset-pg18.yaml

# ensure the db comes up properly (note potential breaking changes)

# open shell in new db container
kubectl exec -it glvd-database-0 -- bash
# restore from backup
pg_restore -v -p 5432 -U glvd -d glvd /backup/glvd.dump
```

## References

- https://ralph.blog.imixs.com/2025/03/16/postgresql-major-upgrade-in-kubernetes/
- https://www.postgresql.org/docs/current/app-pgdump.html
