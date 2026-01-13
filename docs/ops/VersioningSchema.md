# GLVD Versioning Schema

## Problem Statement

GLVD is deployed to a Gardener cluster. Until November 2025, there was no versioning in place; all components were always deployed to the latest commit at the same time. Now we want a **stable environment** and a **dev environment**.  
- The **dev environment** will always use the latest commit.
- The **stable environment** should use consistent, tested versions.

We have the following artifacts that need to be aligned:
- `ghcr.io/gardenlinux/glvd-init` (DB schema and data dump; must be compatible with the API)
- `ghcr.io/gardenlinux/glvd-api` (Spring Boot Java backend app)
- `ghcr.io/gardenlinux/glvd-postgres` (Postgres container with debversion extension)
- `ghcr.io/gardenlinux/glvd-data-ingestion` (Daily job to import new data, must be compatible with the DB schema and contains DB migrations)

## Versioning Approach: Calendar Versioning (CalVer)

- All images use **CalVer**: `YYYY.MM.DD` (e.g., `2025.11.11`).
- All images for a given release share the same CalVer tag.
- If multiple releases happen on the same day, append a counter: `YYYY.MM.DD.N` (e.g., `2025.11.11.2`).

## Release Process

1. **Component Release Workflows**  
    - In each individual component repository, a `release` workflow is triggered (manually or via automation).
    - Each repository creates a new release, building and pushing its image with a CalVer tag (e.g., `2025.11.11`).

2. **Central Manifest Update**  
    - In the central `gardenlinux/glvd` repository, the deployment YAML files (Kubernetes and Docker Compose) are updated to reference the new CalVer-tagged images using the `update-image-tags.py` script.

3. **Production Deployment**  
    - The updated deployment manifests are applied to the production cluster, rolling out the new stable release.

4. **Database Schema Versioning & Migration**  
    - Each GLVD release specifies the required database schema version in the manifest.
    - Database migrations are managed as part of the release process: the appropriate migration scripts are applied automatically before deploying the new application version, ensuring compatibility between the API and the database schema.

5. **Dev Environment**  
    - The dev environment continues to use `:latest` or a `dev` tag, built from the default branch of each repo.

This process ensures coordinated releases, consistent deployments, and automated handling of database schema changes.

## Handling Breaking Changes

- If a breaking change is required, it will be clearly communicated in release notes and documentation.
- Optionally, a suffix (e.g., `2025.11.11-bc1`) can be used for breaking changes, but generally, communication is preferred over encoding this in the version.

## Rollback

- Previous stable versions remain available via their CalVer tags.
- Rollback is as simple as redeploying manifests with the previous version.

## Summary Table

| Environment | Image Tag Used   | Source of Truth         |
|-------------|-----------------|-------------------------|
| dev         | `:latest`       | Default branch builds   |
| stable      | `YYYY.MM.DD`    | Release repo manifest   |

## Automation Recommendations

- Use GitHub Actions for all build, tag, and publish steps.
- Use branch protection and required checks in the release repo.
- Automate manifest updates and release notes generation.
