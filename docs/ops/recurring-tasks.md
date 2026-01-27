# Recurring Tasks in GLVD

## Import new Triage Data



## Import Source Packages for New Garden Linux Release

This is needed for the [List CVEs by Image](https://gardenlinux.github.io/glvd-api/#_list_cves_by_image) feature.

1. Run the [source manifests workflow](https://github.com/gardenlinux/glvd-data-ingestion/actions/workflows/97-source-manifests.yaml).
2. Merge the created PR.
3. The dev cluster will update itself the next day.
4. The prod cluster requires a new release to be updated.

---

## Update Kernel Version When a New Kernel Version Is Introduced

1. Update the kernel [in this commit](https://github.com/gardenlinux/glvd-data-ingestion/commit/78abaecd45efef1a22b52d8376a9fa911743b87d).
2. The dev cluster will update automatically the next day.
3. The prod cluster needs a new release.

---

## Upgrade Postgres version

See [Upgrade Postgres](./UpgradePostgres.md) for hints on how to upgrade Postgres once a new major version is out.

---

## Upgrade Java version

Once a new LTS Java version is out, we should upgrade the version in glvd-api.

See [this commit](https://github.com/gardenlinux/glvd-api/commit/65398debb1548bb00bb41317e19a2923c2c365b0) as an example.

---

## Upgrade Gradle

New Java versions might require new version of the Gradle build tool.
You'll need to update the Gradle wrapper and commit the new version.
See [Gradle docs](https://gradle.org/releases/) on information for how to upgrade to the latest version.

---

## Upgrade Garden Linux container in glvd-api

See [this commit](https://github.com/gardenlinux/glvd-api/commit/41f5a72ded059f11460255c48068d7acd01a5401) as an example.

---

## Release new versions

Even if now new features are developed, new releases should be created and rolled out from time to time to keep the container images updated.
See [perform-release.md](./perform-release.md) for instructions on creating a new release.
