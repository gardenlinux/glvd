# Garden Linux Vulnerability Database (GLVD)

Central entrypoint for the **Garden Linux Vulnerability Database** project — an application for tracking security vulnerabilities in Garden Linux.

Live instance: https://security.gardenlinux.org/

## Quickstart (local)
Start the full stack using Podman Compose:

```bash
podman compose --file deployment/compose/compose.yaml up
```

By default this starts Postgres, the API and ingestion components defined in deployment/compose.

## Releases & versioning
Releases are published on GitHub: https://github.com/gardenlinux/glvd/releases

GLVD uses CalVer: `YYYY.MM.DD`.

## Components
The project is split into dedicated repositories:

- `glvd-postgres` — Containerfile and images for the Postgres database (central data store).  
    https://github.com/gardenlinux/glvd-postgres
- `glvd-data-ingestion` — Schema creation and importers (NVD, Debian security tracker, ...).  
    https://github.com/gardenlinux/glvd-data-ingestion
- `glvd-api` — Backend HTTP API and a minimal web UI.  
    https://github.com/gardenlinux/glvd-api
- `package-glvd` — Client CLI packaged for Garden Linux.  
    https://github.com/gardenlinux/package-glvd
- `glvd-triage-cli` - CLI for importing triage data from YAML files.
    https://github.com/gardenlinux/glvd-triage-cli

## Deployments

Kubernetes
- Kubernetes manifests are in `deployment/k8s`. These manifests are targeted at Gardener clusters.
- See `deploy-k8s.sh` for deployment steps and environment details.

Compose
- Compose spec is in `deployment/compose/compose.yaml`. Use Podman Compose to run locally (see Quickstart).

Operational tips
- Ensure Postgres persistence is configured before production use.
- Use the ingestion component to keep vulnerability data up to date (scheduled runs recommended).

## Contributing & license
Contributions, bug reports and pull requests are welcome — open issues or PRs on the GitHub organization repositories. See the repository for contribution guidelines, code of conduct and license details.

Copyright © 2025 The Linux Foundation Europe. All rights reserved.
Garden Linux Vulnerability Database is a project of NeoNephos Foundation. For applicable policies including privacy policy, terms of use and trademark usage guidelines, please see [linuxfoundation.eu](https://linuxfoundation.eu/).
