# How to release a new version of glvd

glvd consists of several components, each packaged as a separate container image.  
Before releasing glvd itself, you must release all of its components.  
Each component has its own repository and release workflow.

## Perform releases of components

Trigger the release workflow for each component repository.  
The release version is set automatically, no manual steps are needed.

```bash
gh workflow run release.yaml --repo gardenlinux/glvd-api
gh workflow run release.yaml --repo gardenlinux/glvd-postgres
gh workflow run release.yaml --repo gardenlinux/glvd-data-ingestion
```

### Check releases

Check that all component's release images exist:

```bash
./scripts/check-images-exist.sh
```

If the script succeeds, it will print only the version number. If any image is missing, an error message will be displayed.

#### Error handling

Release failures are rare, but OCI image pushes can occasionally fail.

If a release fails in any repository, follow these steps to recover:

1. If a simple re-run does not resolve the issue, apply the necessary fix to the `main` branch.
2. Delete the corresponding GitHub release.
3. Remove the associated git tag for the failed release.
4. Delete the release branch.
5. Re-run the release workflow.

This ensures a clean state before attempting the release again.

## Perform release of the main project

After all components have been successfully released, you can release the main glvd project:

```bash
gh workflow run release.yaml --repo gardenlinux/glvd
```

## Upgrade prod cluster to the new release

To perform an upgrade, run the `perform-release.sh` script with the correct kubeconfig configured.

```bash
KUBECONFIG=/path/to/prod-cluster.yaml ./scripts/perform-release.sh
```

If troubleshooting is ever required, check the individual steps performed in the script.
