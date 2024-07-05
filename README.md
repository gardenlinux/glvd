# Garden Linux Vulnerability Database

This is the central repository of glvd (Garden Linux Vulnerability Database).

This repository holds central documentation.

Implementation is split in multiple directories:

[glvd-api](https://github.com/gardenlinux/glvd-api)

The backend component of glvd, serving the HTTP api.

[glvd-data-ingestion](https://github.com/gardenlinux/glvd-data-ingestion)

Import of data from external sources.

[glvd-postgres](https://github.com/gardenlinux/glvd-postgres)

Postgres container suitable for glvd.
glvd requires the `debversion` data type which is setup in this container image.
