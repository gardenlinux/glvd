# GLVD API Structure

The GLVD HTTP API is implemented in `GlvdController.java` in the `glvd-api` repo.

This listing shows a hierarchical view of the GLVD HTTP api.
For a user-oriented documentation, refer to https://gardenlinux.github.io/glvd-api/

```
/v1
├── cves Get a list of CVEs for the given Garden Linux version or Image or List of Packages
│   ├── {gardenlinuxVersion} [GET]
│   ├── {gardenlinuxVersion}/image/{gardenlinuxImage} [GET]
│   ├── {gardenlinuxVersion}/packages/{packageList} [GET]
│   └── {gardenlinuxVersion}/packages [PUT]
├── packages Get a list of CVEs for the given Package
│   ├── {sourcePackage} [GET]
│   └── {sourcePackage}/{sourcePackageVersion} [GET]
├── distro
│   ├── {gardenlinuxVersion} [GET] Retrieve a list of packages for a given distribution.
│   ├── {gardenlinuxVersion}/{cveId} [GET] Retrieve a list of packages affected by a specific vulnerability.
│   │
│   │ // Internal API, undocumented on purpose
│   │ // This is needed for the triage implementation
│   │ // No external consumers should use this endpoint
│   └── {gardenlinuxVersion}/distId [GET, produces text/plain]
├── gardenlinuxVersions [GET] List of all Garden Linux versions known and supported by GLVD
├── cveDetails
│   └── {cveId} [GET] All information known in GLVD for this specific CVE, aggregated from all our data sources
├── patchReleaseNotes
│   └── {gardenlinuxVersion} [GET] (Deprecated) Old api used for Release Notes page, replaced by new three digit-capable API
├── releaseNotes
│   └── {gardenlinuxVersion} [GET] Used in Release Notes generation, compares the given Garden Linux minor version to the previous minor version to list resolved CVEs
├── kernel/gardenlinux/{gardenlinuxVersion} [GET] Get only the kernel-related CVEs for this Garden Linux version. Not intended for end-users
└── triage
    ├── gardenlinux/{gardenlinuxVersion} [GET] Get triage data for the given Garden Linux version
    ├── cve/{cveId} [GET] Get triage data for the given CVE
    ├── sourcePackage/{sourcePackage} [GET] Get triage data for the given source package
    └── [GET] Get all triage data known to glvd
```
