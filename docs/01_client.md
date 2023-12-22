# Client

The Garden Linux Security Tracker `glvd` can be access either via a simple HTTP client or it can be access via Garden Linux own Security Tracker Client.

## HTTP Client

The Garden Linux Security Tracker provides API endpoints that can be access with every HTTP client. A user can access it via `curl` for example, which would look like this:
```bash
$ curl -s http://glvd.gardenlinux.io/<API ENDPOINT>
$ curl -s http://glvd.gardenlinux.io/v1/cves/CVE-2019-13057
```
The HTTP server will return a JSON output which could be parsed by tools like `jq` for example.
Which API endpoint exists can be read in the corresponding API specification. This can be found here: [openapi-v1.yaml](../openapi-v1.yaml)

## GLVD Client
This repository offers a lightwight `glvd` client written in Python with which a user can send request to the `glvd` API endpoints. In order to run this client, some prerequisites must be fulfilled on the client's system before executing the corresponding client.

### Prerequisites

In order to run the `glvd` client, one must ensure that the following packages are installed
```bash
$ apt update
$ apt install -y git python3-pip python3-apt
```

After that, the actual client can be installed
```bash
$ pip install git+https://github.com/gardenlinux/glvd --system-break-packages
```

### Execution

The Garden Linux Security Tracker client offers two modes:

##### CVE Mode:
```bash
$ glvd cve <CVE>
$ glvd cve CVE-2019-13057 --server http://glvd.gardenlinux.io
```
This mode allows you to get information about a given CVE as long as Garden Linux is affected by this CVE. If Garden Linux is not affected by this, the client will return the following message: 
* `CVE-2019-13058 not found`

The CVE information is returned in JSON format so the output can be parsed with tools like `jq` for example.

##### CVE APT Mode:
```bash
$ glvd cve-apt --server http://glvd.gardenlinux.io
```
This mode returns all CVEs to all packages installed on the local system. The system itself must fullfill the following criteria:
* Debian: Buster, Bullseye, Bookworm or Trixie
* Garden Linux: >= 1337.0

Thereby, the client returns a list of CVEs in JSON format. This output can then be parsed by tools like `jq` for example.