# Garden Linux Vulnerability Database

This repository contains the central entrypoint to the Garden Linux Vulnerability Database (glvd) project.
It implements an application to track security vulnerabilities in Garden Linux.

> [!NOTE]  
> GLVD is work in progress and does not provide a stable api yet.

The code of glvd is located in multiple repositories inside the `gardenlinux` org on GitHub.

glvd is implemented in various components.

## [Postgres container image](https://github.com/gardenlinux/glvd-postgres)

A postgres database is the central component of glvd.
This repository contains a Containerfile to run this database.

## [Data Ingestion](https://github.com/gardenlinux/glvd-data-ingestion)

Data ingestion creates the required database schema and imports data from external sources such as NVD and the debian security tracker.

## [Backend API](https://github.com/gardenlinux/glvd-api)

The backend api exposed an HTTP API to get data out of the database.

It also contains a simple web interface.

## [Client cli tool](https://github.com/gardenlinux/package-glvd)

The client is available in the Garden Linux APT repo.
