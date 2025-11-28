# Garden Linux Vulnerability Database (GLVD)

GLVD (Garden Linux Vulnerability Database) is an application for tracking security issues in Garden Linux. It combines information from public resources such as the [NIST National Vulnerability Database (NVD)](https://nvd.nist.gov/), the [Debian Security Tracker](https://security-tracker.debian.org/), and [kernel.org](https://kernel.org/) with our own triage information. GLVD helps you stay informed about vulnerabilities affecting Garden Linux.

## Using GLVD

[Main entrypoint](https://security.gardenlinux.org)

[API Documentation](https://github.com/gardenlinux/glvd-api)

[User Guide](./docs/user/README.md)

## Features

- Aggregates vulnerability data from multiple trusted sources
- Tracks and triages security issues specific to Garden Linux
- Provides a REST API and web interface for querying vulnerabilities
- Supports automated data ingestion and schema management
- Easily deployable via Kubernetes or Compose

## Architecture & Components

GLVD is composed of several modular components, each maintained in its own repository within the `gardenlinux` GitHub organization:

### [Postgres Container Image](https://github.com/gardenlinux/glvd-postgres)

PostgreSQL database for storing vulnerability data. Includes a Containerfile for easy deployment.

### [Data Ingestion](https://github.com/gardenlinux/glvd-data-ingestion)

Automates schema creation and imports vulnerability data from external sources (NVD, Debian Security Tracker, kernel.org).

### [Backend API](https://github.com/gardenlinux/glvd-api)

Exposes an HTTP REST API for accessing vulnerability data. Also includes a simple web interface for browsing and searching vulnerabilities.

### [Client CLI Tool](https://github.com/gardenlinux/package-glvd)

Command-line client available via the Garden Linux APT repository for interacting with GLVD.

## Getting Started

### Deploy Your Own Instance

#### Kubernetes

Manifest files for deploying GLVD on Kubernetes are available in [`deployment/k8s`](deployment/k8s). These can be used to set up GLVD on a [Gardener](https://gardener.cloud) cluster.

To deploy, see the `deploy-k8s.sh` script for step-by-step instructions.

#### Compose Spec

A Compose setup is provided in [`deployment/compose/compose.yaml`](deployment/compose/compose.yaml).

To start GLVD locally:

```bash
podman compose --file deployment/compose/compose.yaml up
```

This will launch the database and backend API. Note: The database will be empty initially.

To initialize the database schema and import data:

```bash
podman run -it --rm --network=compose_glvd --env PGHOST=glvd-postgres ghcr.io/gardenlinux/glvd-init:latest
```

**Warning:** This operation will reset the database. Backup your data if needed.

## Contributing

We welcome contributions! Please see the individual component repositories for and open issues.

## Support & Documentation

- [GLVD API Documentation](https://github.com/gardenlinux/glvd-api)
- For questions or support, open an issue in the relevant repository.
