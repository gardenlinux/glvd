# GLVD Versioning Schema Reference

This document describes the implemented versioning schema and release process for GLVD deployments.

## Versioning Scheme

- **Calendar Versioning (CalVer)** is used for all container images.
    - Format: `YYYY.MM.DD` (e.g., `2025.11.11`)
    - Multiple releases per day are not supported, in the worst case, manual intervention would be needed (deleting a previously created git tag/image tag, etc).
    - All images in a release share the **exact same** CalVer tag.

## Artifacts

The following images are versioned and released together:
- `ghcr.io/gardenlinux/glvd-init` – DB schema and data dump (must match API)
- `ghcr.io/gardenlinux/glvd-api` – Spring Boot Java backend
- `ghcr.io/gardenlinux/glvd-postgres` – Postgres with debversion extension
- `ghcr.io/gardenlinux/glvd-data-ingestion` – Data import job (includes DB migrations)

## Release Workflow

See [perform-release.md](../ops/perform-release.md) for detailed instructions.

1. **Component Release**
    - Each component repository triggers a `release` workflow.
    - Images are built and pushed with the new CalVer tag.

2. **Central Manifest Update**
    - The central `gardenlinux/glvd` repository updates deployment manifests (Kubernetes, Docker Compose) to reference the new CalVer tags using `scripts/update-image-tags.py`.

3. **Production Deployment**
    - Updated manifests are applied to the production cluster, rolling out the new stable release.

4. **Database Schema Versioning & Migration**
    - Each release specifies the required DB schema version in the manifest.
    - Migration scripts are applied automatically before deploying the new application version.

5. **Dev Environment**
    - The dev environment uses `:latest` tag, built and updated on each push to the `main` branch

## Handling Breaking Changes

- There is no way to indicate breaking changes as there is in SemVer
- Breaking changes are to be avoided

## Rollback

- Previous stable versions remain available via their CalVer tags.
- Rollback is performed by redeploying manifests with the previous version.

## Environment Reference

| Environment | Image Tag Used   | Source of Truth         |
|-------------|-----------------|-------------------------|
| dev         | `:latest`       | Default branch builds   |
| stable      | `YYYY.MM.DD`    | Release repo manifest   |
