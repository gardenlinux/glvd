# GLVD Data Model

This document describes the core database schema for GLVD, focusing on what developers need to know to work with or extend the system.

## Overview

GLVD ingests vulnerability and package data from multiple sources and stores it in a PostgreSQL database. The schema is designed to support:
- Tracking CVEs and their metadata (from NVD, Debian, kernel, etc.)
- Mapping CVEs to distributions, packages, and Garden Linux images
- Supporting triage and context for CVEs (e.g., resolution status, use case, overrides)
- Efficient queries for API and reporting

## Key Tables

### `all_cve`
Stores all known CVEs, including metadata and raw data from upstream sources.

| Column    | Type                        | Description                              |
|-----------|-----------------------------|------------------------------------------|
| cve_id    | text (PK)                   | CVE identifier (e.g. CVE-2023-1234)      |
| last_mod  | timestamptz (not null)      | Last modification timestamp              |
| data      | json (not null)             | Raw CVE data (from NVD, etc.)            |

---

### `nvd_cve`
Stores CVEs as ingested from the NIST NVD.

| Column    | Type                        | Description                              |
|-----------|-----------------------------|------------------------------------------|
| cve_id    | text (PK)                   | CVE identifier                           |
| last_mod  | timestamptz (not null)      | Last modification timestamp              |
| data      | json (not null)             | Raw NVD data                             |

---

### `dist_cpe`
Defines supported distributions (Debian, Garden Linux, etc.) using CPE identifiers.

| Column        | Type         | Description                        |
|---------------|--------------|------------------------------------|
| id            | integer (PK) | Internal ID                        |
| cpe_vendor    | text         | CPE vendor (e.g. debian)           |
| cpe_product   | text         | CPE product (e.g. debian_linux)    |
| cpe_version   | text         | CPE version (e.g. 12)              |
| deb_codename  | text         | Debian codename (e.g. bullseye)    |

---

### `debsrc`
Source packages per distribution.

| Column           | Type              | Description                        |
|------------------|-------------------|------------------------------------|
| dist_id          | integer (FK)      | References `dist_cpe(id)`          |
| gardenlinux_version | text           | Garden Linux version (optional)    |
| last_mod         | timestamptz       | Last modification timestamp        |
| deb_source       | text              | Source package name                |
| deb_version      | debversion        | Source package version             |
| minor_deb_version| text              | Minor version (optional)           |

---

### `deb_cve`
Links CVEs to Debian source packages and distributions, with vulnerability status and version info.

| Column            | Type              | Description                        |
|-------------------|-------------------|------------------------------------|
| dist_id           | integer (FK)      | Distribution                       |
| gardenlinux_version | text            | Garden Linux version (optional)    |
| cve_id            | text              | CVE identifier                     |
| last_mod          | timestamptz       | Last modification timestamp        |
| cvss_severity     | integer           | CVSS severity (optional)           |
| deb_source        | text              | Source package name                |
| deb_version       | debversion        | Package version                    |
| deb_version_fixed | debversion        | Version where fixed (optional)     |
| debsec_vulnerable | boolean           | True if vulnerable                 |
| data_cpe_match    | json              | CPE match data                     |

---

### `debsec_cve`
Represents the raw CVE list from Debian Security Tracker for each distribution.

| Column               | Type              | Description                        |
|----------------------|-------------------|------------------------------------|
| dist_id              | integer (FK)      | Distribution                       |
| gardenlinux_version  | text              | Garden Linux version (optional)    |
| cve_id               | text              | CVE identifier                     |
| last_mod             | timestamptz       | Last modification timestamp        |
| deb_source           | text              | Source package name                |
| deb_version_fixed    | debversion        | Version where fixed (optional)     |
| debsec_tag           | text              | Tag from Debian CVE list           |
| debsec_note          | text              | Note from Debian CVE list          |
| minor_deb_version_fixed | text           | Minor version fixed (optional)     |

---

### `cve_context`
Tracks triage and context for CVEs in Garden Linux, including resolution status, use case, and overrides.

| Column             | Type              | Description                        |
|--------------------|-------------------|------------------------------------|
| id                 | integer (PK)      | Internal ID                        |
| dist_id            | integer           | Distribution                       |
| gardenlinux_version| text              | Garden Linux version (optional)    |
| cve_id             | text              | CVE identifier                     |
| create_date        | timestamptz       | When context was created           |
| use_case           | text              | Context/use case (required)        |
| score_override     | numeric           | Optional CVSS override             |
| description        | text              | Triage/description                 |
| is_resolved        | boolean           | True if resolved                   |
| triaged            | boolean           | True if triaged                    |

---

### `cve_context_kernel`
Kernel-specific CVE context, including LTS version, fix status, and subsystem relevance.

| Column                | Type      | Description                        |
|-----------------------|-----------|------------------------------------|
| cve_id                | text      | CVE identifier                     |
| lts_version           | text      | Kernel LTS version                 |
| fixed_version         | text      | Version where fixed (optional)     |
| is_fixed              | boolean   | True if fixed                      |
| is_relevant_subsystem | boolean   | True if relevant subsystem         |
| source_data           | jsonb     | Raw source data                    |

---

### `image_variant`
Tracks Garden Linux image builds and their metadata.

| Column        | Type         | Description                        |
|---------------|--------------|------------------------------------|
| id            | bigint (PK)  | Internal ID                        |
| namespace     | text         | Image namespace (default: gardenlinux) |
| image_name    | text         | Image name                         |
| image_version | text         | Image version                      |
| commit_id     | text         | Git commit ID (optional)           |
| metadata      | jsonb        | Additional metadata                |
| packages      | text[]       | List of packages in image          |

---

### `image_package`
Links images to packages.

| Column         | Type         | Description                        |
|----------------|--------------|------------------------------------|
| image_variant_id | bigint (FK)| References `image_variant(id)`     |
| package_name   | text         | Package name                       |

---

### `migrations`
Tracks applied DB migrations.

| Column      | Type         | Description                        |
|-------------|--------------|------------------------------------|
| id          | integer (PK) | Migration ID                       |
| migrated_at | timestamptz  | When migration was applied         |

---

## Key Views

- **`cvedetails`**: Aggregates CVE, context, and package info for API queries.
- **`sourcepackagecve`**: Maps CVEs to source packages and vulnerability status.
- **`kernel_cve`**: Kernel-specific CVE view, including fix and subsystem info.
- **`triage`**: Combines CVE, package, and triage context for reporting.
- **`imagesourcepackagecve`**: Maps CVEs to packages and images for Garden Linux.

## Notes for Developers

- Use the `debversion` extension for all Debian version columns.
- All timestamps use `timestamptz` for consistency.
- The schema is designed for extensibility: new sources or context can be added with minimal disruption.
- Use the views for most queries; they encapsulate the necessary joins and logic.
- Triage and context are first-class: use `cve_context` and `cve_context_kernel` to track overrides, resolutions, and Garden Linux specifics.

---
For further details, see the [GLVD ingestion repository](https://github.com/gardenlinux/glvd-data-ingestion) and the API documentation.
