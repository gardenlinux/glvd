# Garden Linux Vulnerability Database

This repository contains the central entrypoint to the Garden Linux Vulnerability Database (glvd) project.
It implements an application to track security vulnerabilities in Garden Linux.

> [!NOTE]  
> GLVD is work in progress and does not provide a stable api yet.

## Components

The code of glvd is located in multiple repositories inside the `gardenlinux` org on GitHub.

glvd is implemented in various components.

### [Postgres container image](https://github.com/gardenlinux/glvd-postgres)

A postgres database is the central component of glvd.
This repository contains a Containerfile to run this database.

### [Data Ingestion](https://github.com/gardenlinux/glvd-data-ingestion)

Data ingestion creates the required database schema and imports data from external sources such as NVD and the debian security tracker.

### [Backend API](https://github.com/gardenlinux/glvd-api)

The backend api exposed an HTTP API to get data out of the database.

It also contains a simple web interface.

### [Client cli tool](https://github.com/gardenlinux/package-glvd)

The client is available in the Garden Linux APT repo.

## Deploy your own instance

### Kubernetes

Manifest files for a kubernetes deployment are located in [deployment/k8s](deployment/k8s).
Those deployments are used to create setup of glvd on a [Gardener](https://gardener.cloud) cluster.

See the `deploy-k8s.sh` script for details.

### [Compose Spec](https://compose-spec.io)

A setup for [Compose](https://podman-desktop.io/docs/compose/running-compose) can be found in `deployment/compose/compose.yaml`.

Example command to start locally:

```bash
podman compose --file deployment/compose/compose.yaml up
```

This will give you a running instance of the database and the backend, but the database has no schema and no data.

To init the db, you may run something like:

```bash
podman run -it --rm --network=compose_glvd --env PGHOST=glvd-postgres ghcr.io/gardenlinux/glvd-init:latest
```

Note that this will wipe the existing database, so in case you want to keep data be sure to back it up.
