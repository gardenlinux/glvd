# Contributing to GLVD

## Project Overview

The code of glvd is located in multiple repositories inside the `gardenlinux` org on GitHub.

glvd is implemented in various components.

### [gardenlinux/glvd](https://github.com/gardenlinux/glvd)

The `gardenlinux/glvd` repo is the main entry point to GLVD.
It contains project-wide docs, and infrastructure definitions for deploying GLVD instances both locally and in cloud environments.

### [`gardenlinux/glvd-postgres`](https://github.com/gardenlinux/glvd-postgres)

A postgres database is the central component of glvd.
This repository contains a `Containerfile` to run this database.

> [!IMPORTANT]  
> This container image includes the [postgresql-debversion](https://salsa.debian.org/postgresql/postgresql-debversion) extension which is vital to GLVD.
> It allows to compare debian package version numbers.
> This is the reason why we absolutely need a postgres db to run glvd, and why this needs to run on top of a debian-based container image.

### [`gardenlinux/glvd-data-ingestion`](https://github.com/gardenlinux/glvd-data-ingestion)

Data ingestion creates the required database schema and imports data from external sources such as NVD and the debian security tracker.

### [`https://github.com/gardenlinux/glvd-api`](https://github.com/gardenlinux/glvd-api)

The backend api exposed an HTTP API to get data out of the database.

It also contains a simple web interface.

### [`https://github.com/gardenlinux/package-glvd`](https://github.com/gardenlinux/package-glvd)

The cli client is available in the Garden Linux APT repo.

## Setup a Local Dev Env

### On macOS, using podman (desktop/machine)

- Make sure [podman is setup properly](https://podman.io/docs/installation)
- Get the suitable [docker compose](https://github.com/docker/compose) binary and put it into your `PATH`
  - Running `podman compose` will use a 'provider' for working with compose files
  - By default, it makes use of https://github.com/containers/podman-compose, which does not support all features needed by GLVD as of december 2024
  - If the `docker-compose` binary is in your `PATH`, `podman compose` will use that to crate containers
  - Using this method, you can use podman to run GLVD

With this setup, inside your local clone of the `gardenlinux/glvd` repo, you should be able to run `podman compose --file deployment/compose/compose.yaml up` which will bring up a local glvd environment including a recent snapshot of the database.

You can check this using the Spring Boot Actuator endpoint:

```
$ curl http://localhost:8080/actuator/health
{"status":"UP"}
```

Congratulations, you have a running instance of GLVD.

Let's have a closer look at our running containers:

```
$ podman ps
CONTAINER ID  IMAGE                                            COMMAND               CREATED      STATUS                  PORTS                   NAMES
aaaaaaaaaaaa  ghcr.io/gardenlinux/glvd-postgres:latest         postgres              2 weeks ago  Up 3 minutes (healthy)  0.0.0.0:5432->5432/tcp  compose-glvd-postgres-1
bbbbbbbbbbbb  ghcr.io/gardenlinux/glvd-api:latest              /jre/bin/java -ja...  2 weeks ago  Up 3 minutes            0.0.0.0:8080->8080/tcp  compose-glvd-1
```

We have two long-running containers:
The postgres db, and our backend.

The db exposes the default port `5432`, which is useful for development purposes.
You may use postgres client applications to inspect, edit, backup or restore the database as needed.
In a production deployment, the database is not exposed to the outside world.

The backend exposed port `8080` as we have already seen above in our `curl` command.

### Exploring the API

Next, make yourself familiar with GLVD's HTTP API.
It is documented [here](https://gardenlinux.github.io/glvd-api/).

> [!TIP]
> For using your local instance, you'll need to use `http://localhost:8080` in all of the api urls instead of the provided urls.

After getting familiar with the API, you can have a look at the [example requests provided in the glvd-api repo](https://github.com/gardenlinux/glvd-api/tree/main/api-examples).

### Make changes to the backend and try them out

Prerequisites:
- JDK 25 (SapMachine preferred, download and install from https://sapmachine.io)
  - Be sure to install the *JDK* version, the *JRE* is not enough

Run `./gradlew bootJar` inside the `glvd-api` repo checkout to compile the backend.

Run `podman stop compose-glvd-1` to stop the backend container from running.
This allows your locally built backend to make use of the port `8080` on your machine.

Run `java -jar build/libs/glvd-dev.jar` to start the backend version you've just built.
It should start up and connect to the database automatically.

Run `curl http://localhost:8080/actuator/health` again and observe the log of your backend instance.
It should say something like `Initializing Servlet 'dispatcherServlet'`.

Congratulations, you compiled the GLVD backend on your own, and are running it on your machine.
You can now make changes to the source code, stop, rebuild and restart your instance and see if it does what you expect.

### Reading the backend source code

The backend is implemented in Java using [Spring Boot](https://docs.spring.io/spring-boot/index.html).
Some basic understanding of both Java and is therefore required to work on the backend.

The `glvd-api` project implements both the HTTP API, and a very basic web user interface.

As of January 2026, the whole backend is read-only by design.
It does not include any endpoints or ui elements for adding, updating or deleting data.

The backend needs a database instance to start.
This is already there if you followed the steps described before.

It makes use of the `JpaRepository` class provided by Spring to ease database access.
You can find the `*Repository` classes by their name.

The `GlvdService` class is the ui independent part which provides functions to be used both by the web ui and by the HTTP api.
Mostly it only bridges between the `*Repository` classes that communicate with the db and the ui/api layer.

The HTTP api is implemented as a simple `RestController`.

The web ui is built using [thymeleaf](https://www.thymeleaf.org), which is a templating language that is built into Spring Boot.
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

The data ingestion process is required to get a functioning glvd instance.

In short, it collects and combines data from various public sources:

- data from nist
- data from debian security tracker
- data from kernel.org vulns repo

Running the ingestion from scratch takes long and might fail due to rate limiting.
This is why container images with existing database dumps are published for glvd.

### Gardener Setup for GLVD

For running dev/test/prod environments, we make use of Gardener clusters.

The [manifests are in the glvd/glvd repo](https://github.com/gardenlinux/glvd/tree/main/deployment/k8s), which also includes [a shell script](https://github.com/gardenlinux/glvd/blob/main/deploy-k8s.sh) that does the deployment.

> [!NOTE]
> This setup might change in the future, for example by making use of helm

A running cluster with glvd setup will look like this:

```
$ kubectl get pods,jobs,sts,pvc
NAME                                READY   STATUS      RESTARTS   AGE
pod/glvd-5ffd969b55-cdnb8           1/1     Running     0          14h
pod/glvd-database-0                 1/1     Running     0          14h
pod/glvd-ingestion-29009250-lqqlg   0/1     Completed   0          127m

NAME                                STATUS     COMPLETIONS   DURATION   AGE
job.batch/glvd-ingestion-29006370   Complete   1/1           3m50s      2d2h
job.batch/glvd-ingestion-29007810   Complete   1/1           4m33s      26h
job.batch/glvd-ingestion-29009250   Complete   1/1           3m36s      127m

NAME                             READY   AGE
statefulset.apps/glvd-database   1/1     43d

NAME                                                     STATUS   VOLUME                          CAPACITY   ACCESS MODES   STORAGECLASS
persistentvolumeclaim/postgres-storage-glvd-database-0   Bound    pv-shoot--gardnlinux--glvd-xy   5Gi        RWO            default
```

We have two long running pods, one with the postgres db, and one with the backend.

The db is controlled by a stateful set and has a persistent volume attached.

We also have short-lived pods to update the db via the data ingestion container.
This is controlled via a cronjob that runs daily.

Note that the container images are automatically updated via github actions ([glvd-api](https://github.com/gardenlinux/glvd-api/blob/497ce994f97fc241be063cecb7bbb837b6413714/.github/workflows/ci.yaml#L155), [glvd-postgres](https://github.com/gardenlinux/glvd-postgres/blob/85042bd6e413bd0df265ab80568d484dd9ebbefa/.github/workflows/build-postgres-container.yml#L89)), so the cluster is always running the very latest version of glvd.

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
