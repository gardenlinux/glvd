# Server

The Garden Linux Security Tracker `glvd` uses [Quart](https://pgjones.gitlab.io/quart/) which is a Fast Python web microframework.

## Purposes

This framework can be used for providing simple webpages as well as for hosting APIs. Garden Linux's Security Tracker is using this framework to provide both: 

#### Web App
As of now, there is no Web App implemented in `glvd`. In future, there could be a web page which allows to request vulnerability information in an easy and fast way similar to Debian's Security Tracker.

#### API

The general API is described in the following specificiation:
* [openapi-v1.yaml](../openapi-v1.yaml)

Thereby, it offers the following API endpoints:

##### Endpoint: `v1/cves/findByCpe`:
Finds CVE by CPE

Supported HTTP methods:
* GET

| Parameter | Description | 
|-----------|-------------|
| `cpeName` |  CPE name to search for, only Debian/Garden Linux related CPE can be used |
| `cvssV3SeverityMin` | The min severity that a CVE must have. |
| `debVersionEnd` | The maximum version | 

##### Endpoint `v1/cves/findBySources`:
Finds CVE by source packages

Supported HTTP methods:
* POST

| Parameter | Description | 
|-----------|-------------|
| `cvssV3SeverityMin` | The min severity that a CVE must have. |

The POST body must contain a list of source packages for which one searches the corresponding CVEs. A list item could look like this: `debian_bookworm_glibc_2.36-9+deb12u3`

##### Endpoint `v1/cves/findBySources`:
Find CVE by ID

Supported HTTP Methods:
* GET

| Parameter | Description | 
|-----------|-------------|
| `cveId` | The ID of an CVE (e.g. `CVE-1999-0250`) |