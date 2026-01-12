# Contributing to GLVD

## Project Overview

The GLVD code is spread across several repositories in the `gardenlinux` GitHub organization. Each repository implements one part of the system.

### [gardenlinux/glvd](https://github.com/gardenlinux/glvd)

This is the main entry point for GLVD. It contains project-wide documentation and infrastructure for deploying GLVD locally and in cloud environments.

### [`gardenlinux/glvd-postgres`](https://github.com/gardenlinux/glvd-postgres)

This repository provides the PostgreSQL container image used by GLVD.

> [!IMPORTANT]  
> The image includes the [postgresql-debversion](https://salsa.debian.org/postgresql/postgresql-debversion) extension (used to compare Debian package version numbers). Because of this dependency, the database image must be based on a Debian-style distribution.

### [`gardenlinux/glvd-data-ingestion`](https://github.com/gardenlinux/glvd-data-ingestion)

Handles creation of the database schema and imports data from external sources (for example NVD and the Debian security tracker).

### [`https://github.com/gardenlinux/glvd-api`](https://github.com/gardenlinux/glvd-api)

The backend service. It exposes an HTTP API to read data from the database and also contains a simple web UI.

### [`https://github.com/gardenlinux/package-glvd`](https://github.com/gardenlinux/package-glvd)

Provides the GLVD CLI client packaged for the Garden Linux APT repository.

## Setup a Local Dev Env

### On macOS — using Podman (Desktop / Machine)

Prerequisites
- Install Podman (podman.io). If using Podman Machine, run `podman machine init` and `podman machine start`.
- Download a compatible docker-compose (Compose v2) CLI and put it in your PATH. This lets Podman reuse it for Compose files.

How Podman Compose works
- By default `podman compose` uses the provider containers/podman-compose, which (as of Dec 2024) lacks some features GLVD needs.
- If a `docker-compose` binary is available in your PATH, `podman compose` will use that binary to create containers — this is the recommended approach for GLVD.

Bring up the local environment
- From the root of your local `gardenlinux/glvd` checkout run:

```
podman compose --file deployment/compose/compose.yaml up
```

Add `-d` to run in the background, if desired.

The compose setup includes a recent snapshot of the GLVD database.

That's it — Podman will start the database and backend containers for local development.

You can check this using the Spring Boot Actuator endpoint:

```
$ curl http://localhost:8080/actuator/health
{"groups":["liveness","readiness"],"status":"UP"}
```

Congratulations, you have a running instance of GLVD.

Let's have a closer look at our running containers:

```
$ podman ps
CONTAINER ID  IMAGE                                            COMMAND               CREATED      STATUS                  PORTS                   NAMES
aaaaaaaaaaaa  ghcr.io/gardenlinux/glvd-postgres:latest         postgres              2 weeks ago  Up 3 minutes (healthy)  0.0.0.0:5432->5432/tcp  compose-glvd-postgres-1
bbbbbbbbbbbb  ghcr.io/gardenlinux/glvd-api:latest              /jre/bin/java -ja...  2 weeks ago  Up 3 minutes            0.0.0.0:8080->8080/tcp  compose-glvd-1
```

- Two long‑running containers:
    - Postgres database (exposes port `5432` for local development)
    - Backend service (exposes port `8080`)
- For development you can connect to the database on `localhost:5432` with tools like `psql`, pgAdmin, or any PostgreSQL client to inspect, edit, backup, or restore data.
- In production the database is not exposed externally — it is only accessible to internal services.

### Exploring the API

Next, make yourself familiar with GLVD's HTTP API.
It is documented [here](https://gardenlinux.github.io/glvd-api/).

> [!TIP]
> For using your local instance, you'll need to use `http://localhost:8080` in all of the api urls instead of the provided urls.

After getting familiar with the API, you can have a look at the [example requests provided in the glvd-api repo](https://github.com/gardenlinux/glvd-api/tree/main/api-examples).

When you are done, stop the compose setup by running:

```
podman compose --file deployment/compose/compose.yaml down --volumes
```

### Make changes to the backend and try them out

Prerequisites:
- JDK 25 (SapMachine preferred, download and install from https://sapmachine.io)
  - Be sure to install the *JDK* version, the *JRE* is not enough

The backend is located in the `glvd-api` repository.

It has it's own database setup for convenience.

> [!TIP]
> There are two database setups in `glvd-api`.
> One is optimized for unit tests, it contains a minimal set of data needed to pass the tests.
> The other setup is intended for usage and runs with a full dump of the glvd database to give you a realistic user experience.
> Both use different ports for postgres, so they can run at the same time.
> Unit-tests use port `9876`, while for running the app the db uses postgres' default port `5432`.

#### Running the Application Locally

Inside your clone of `glvd-api`, follow those steps:

1. Get a dump of the Database (this needs the GitHub `gh` cli and `jq`)

```bash
./download-db-dump.sh
```

2. Start the application database:

```bash
./start-db-for-app.sh
```

3. Build and run the Spring Boot app:

```bash
./gradlew bootRun
```

4. After startup, check readiness:

```
curl http://localhost:8080/actuator/health
# Should return status code 200
```

5. Open http://localhost:8080 in your web browser to use the UI

Observe the logs of your backend instance.
It should say something like `Initializing Servlet 'dispatcherServlet'`.

Congratulations, you compiled the GLVD backend on your own, and are running it on your machine.
You can now make changes to the source code, stop, rebuild and restart your instance and see if it does what you expect.

### Reading the backend source code

The backend is implemented in Java using [Spring Boot](https://docs.spring.io/spring-boot/index.html).
Some basic understanding of both Java and Spring Boot is therefore required to work on the backend.

The `glvd-api` project implements both the HTTP API, and a very basic web user interface.

As of January 2026, the whole backend is read-only by design to ensure data integrity and prevent unauthorized modifications.
It does not include any endpoints or ui elements for adding, updating or deleting data.
This design decision aligns with the current use cases of GLVD, and there are no immediate plans to introduce write capabilities. However, this may be revisited in the future based on evolving project requirements.

The backend needs a database instance to start.
This is already there if you followed the steps described before.

It makes use of the `JpaRepository` class provided by Spring to ease database access.
You can find the `*Repository` classes by their name.

The `GlvdService` class is the UI-independent part which provides functions to be used both by the web UI and by the HTTP API. It acts as a bridge between the database access layer (via `*Repository` classes) and the presentation layer (UI/API).

The HTTP api is implemented as a simple `RestController`.

The web UI is built using [Thymeleaf](https://www.thymeleaf.org), which is a templating language that is built into Spring Boot. For contributors unfamiliar with Thymeleaf, you can refer to the [official Thymeleaf documentation](https://www.thymeleaf.org/documentation.html) to get started.
You can find the templates in `src/main/resources/templates`, and the code for populating them in `src/main/java/io/gardenlinux/glvd/UiController.java`.

The existing code should be relatively easy to adapt to changing requirements.

### Database schema

GLVD's database schema is described [here](https://github.com/gardenlinux/glvd/blob/main/docs/03_ingestion.md#database).

### Important VIEWs

GLVD makes use of VIEWs to provide much of the data needed by the backend.
The general idea is to solve things in the database as far as possible without resorting to procedural programming in the db.
If logic in the backend can be replaced by an SQL VIEW, this should be done.

We have the following views in GLVD:

- `sourcepackage` provides information on which package in which version is in a specific Garden Linux release
- `cve_with_context` provides additional context (i.e. 'triage') for a CVE
- `sourcepackagecve` provides CVEs affecting a source package in a specific version in a Garden Linux release
- `cvedetails` provides details of a CVE such as its CVSS Scores
- `nvd_exclusive_cve` provides a list of CVE that only appear in NVD but not in the debian security tracker
- `nvd_exclusive_cve_matching_gl` like `nvd_exclusive_cve`, but only with items that fuzzy-match any package in Garden Linux

### Inspect the db locally

You can inspect and edit the local database using the `psql` cli tool in the podman container like in this example:

```
$ podman exec -it compose-glvd-postgres-1 bash -c "psql -U glvd glvd"
psql (17.2 (Debian 17.2-1.pgdg120+1))
Type "help" for help.

glvd=# \dt
          List of relations
 Schema |    Name     | Type  | Owner
--------+-------------+-------+-------
 public | all_cve     | table | glvd
 public | cve_context | table | glvd
 public | deb_cve     | table | glvd
 public | debsec_cve  | table | glvd
 public | debsrc      | table | glvd
 public | dist_cpe    | table | glvd
 public | nvd_cve     | table | glvd
(7 rows)
glvd=# \dv
               List of relations
 Schema |          Name          | Type | Owner
--------+------------------------+------+-------
 public | cve_with_context       | view | glvd
 public | cvedetails             | view | glvd
 public | recentsourcepackagecve | view | glvd
 public | sourcepackage          | view | glvd
 public | sourcepackagecve       | view | glvd
(5 rows)
```

You can also use GUI clients such as [pgAdmin](https://www.pgadmin.org) using this jdbc url: `jdbc:postgresql://localhost:5432/glvd`.
All values (username, password, db name) are set to `glvd` by default **for the local setup**.



### Run automated tests locally

The `glvd-api` project has tests which require a database.
Inside the local checkout of `glvd-api`, the tests can be run with this:

```bash
./start-db-for-test.sh
./gradlew test
```

### Understanding the data ingestion process

The data ingestion process is required to run a functioning GLVD instance. It aggregates and reconciles information from several public sources — for example NIST, the Debian Security Tracker, and the kernel.org vulnerabilities repository — to build the database GLVD uses.

Running a full ingestion from scratch can be slow and is prone to failures due to rate limiting from those upstream services. To avoid that overhead, we publish container images that include prebuilt database dumps so you can get a usable GLVD instance quickly.

### Gardener Setup for GLVD

For testing and production we deploy GLVD to Gardener clusters. The Kubernetes manifests are in the repository at https://github.com/gardenlinux/glvd/tree/main/deployment/k8s, and deployment can be automated with the helper script at https://github.com/gardenlinux/glvd/blob/main/deploy-k8s.sh.

Note: this setup may change in the future (for example, we may adopt Helm).

A healthy GLVD cluster typically runs a stateful Postgres pod together with a backend pod. The database is managed by a StatefulSet and backed by a PersistentVolumeClaim, while the ingestion process runs as a cronjob to update the DB. Container images for the dev cluster are updated via GitHub Actions in the glvd-api and glvd-postgres repositories, so clusters always run the latest code from the `main` branch of those repos.
The prod cluster is updated by a deliberate release process which is described in [perform-release.md](../ops/perform-release.md).

You can inspect the cluster with kubectl; a representative output looks like this:

```
$ kubectl -n glvd get pods,jobs,sts,pvc
NAME                                READY   STATUS      RESTARTS   AGE
pod/glvd-6cddff8cb8-tbcvz           1/1     Running     0          3d13h
pod/glvd-database-0                 1/1     Running     0          3d13h
pod/glvd-ingestion-29465730-nv45h   0/1     Completed   0          3d7h
pod/glvd-ingestion-29470050-6klgd   0/1     Completed   0          7h39m

NAME                                STATUS     COMPLETIONS   DURATION   AGE
job.batch/glvd-ingestion-29464290   Complete   1/1           6m13s      4d7h
job.batch/glvd-ingestion-29465730   Complete   1/1           6m36s      3d7h
job.batch/glvd-ingestion-29470050   Complete   1/1           6m19s      7h39m

NAME                             READY   AGE
statefulset.apps/glvd-database   1/1     63d

NAME                                                       STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/postgres-backup-glvd-database-0      Bound    pv-shoot--xx   5Gi        RWO            default        <unset>                 63d
persistentvolumeclaim/postgres18-storage-glvd-database-0   Bound    pv-shoot--yy   5Gi        RWO            default        <unset>                 63d
```

### Inspect the db in the cluster

Similar to what we've seen before, we can also work with the database in the cluster like in this example:

```
kubectl exec -it glvd-database-0 -- bash -c 'PAGER= psql -U glvd glvd'
psql (17.2 (Debian 17.2-1.pgdg120+1))
Type "help" for help.

glvd=# \dt
              List of relations
 Schema |        Name        | Type  | Owner
--------+--------------------+-------+-------
 public | all_cve            | table | glvd
 public | cve_context        | table | glvd
.. (further entries omitted)
```

### Data Ingestion GitHub Actions workflows

There are [multiple useful workflows](https://github.com/gardenlinux/glvd-data-ingestion/actions/) to make it more simple to work with the ingestion process.

The workflows are numbered to make it more clear what depends on what.

On push, only "01 - Build and Push Data Ingestion Container" is ran automatically.
The other workflows need to be run on demand.

Those workflows exist in this repo:

#### 01 - Build and Push Data Ingestion Container

This workflow builds and pushes the container where the ingestion is running.
This container is used in the "Dump GLVD Postgres Snapshot to sql file" workflows, and in the cronjob mentioned above.

#### 02 - Dump GLVD Postgres Snapshot to sql file

This workflow runs a full ingestion job from scratch and exports a postgres dump file which can be imported.

#### 02.5 - Dump GLVD Postgres Snapshot to sql file (incremental)

This workflow is the same as "02 - Dump GLVD Postgres Snapshot to sql file", but it uses a previous dump if that exists which makes it much faster to run.
Note that this workflow fails if no current dump is available from the 02 job.

#### 03 - Build and Push Container to init GLVD Postgres DB

This workflow builds and pushes the `gardenlinux/glvd-init` container image which is used both in the local Compose setup and in the cluster setup to fill the database with the dump that was created in "02 - Dump GLVD Postgres Snapshot to sql file".

#### 03.5 - Build and Push Container to init GLVD Postgres DB (Incremental)

Same as above but makes use of "02.5 - Dump GLVD Postgres Snapshot to sql file (incremental)".

### glvd client

If an image is built with the `glvd` feature, a binary client program called `glvd` is available in the instance.

```
$ ./build kvm_dev-glvd

$ bin/start-vm .build/kvm-glvd_dev-xy.raw

root@garden:~# glvd executive-summary
This machine has 11 potential security issues
Run `glvd check` to get the full list

root@garden:~# glvd what-if vim
CVE-2008-4677       4.3 AV:N/AC:M/Au:N/C:P/I:N/A:N                     vim                  2:9.1.1113-1
CVE-2025-26603      4.2 CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L   vim                  2:9.1.1113-1
CVE-2017-1000382    5.5 CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N   vim                  2:9.1.1113-1
```
