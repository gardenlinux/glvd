#!/usr/bin/env python3

import sys
import re
import requests
import subprocess
import json
import os

"""
Script to check for consistency of glvd releases.
A valid release of glvd needs the exact same tag on all mentioned repos, and all mentioned container images.
"""

REPOS = [
    "gardenlinux/glvd",
    "gardenlinux/glvd-api",
    "gardenlinux/glvd-postgres",
    "gardenlinux/glvd-data-ingestion",
]

IMAGE_TEMPLATES = [
    "ghcr.io/gardenlinux/glvd-postgres:{version}",
    "ghcr.io/gardenlinux/glvd-api:{version}",
    "ghcr.io/gardenlinux/glvd-data-ingestion:{version}",
]

GITHUB_API = "https://api.github.com/repos/{repo}/tags"
DOCKER_REGISTRY_API = "https://ghcr.io/v2/{image}/manifests/{tag}"

CALVER_REGEX = re.compile(r"^\d{4}.\d{2}.\d{2}$")


def github_get(url):
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp


def get_latest_calver_tag(repo):
    url = GITHUB_API.format(repo=repo)
    resp = github_get(url)
    tags = resp.json()
    calver_tags = [tag['name'] for tag in tags if CALVER_REGEX.match(tag['name'])]
    if not calver_tags:
        return None
    # Sort descending, latest first
    calver_tags.sort(reverse=True)
    return calver_tags[0]

def all_repos_same_tag(tags):
    return all(tag == tags[0] for tag in tags)

def docker_image_tag_exists(image, tag):
    # Use oras to fetch the manifest
    try:
        result = subprocess.run(
            ["oras", "manifest", "fetch", f"{image}:{tag}"],
            capture_output=True,
            text=True,
            check=True
        )
        manifest = json.loads(result.stdout)
    except Exception as e:
        print(f"Failed to fetch manifest for {image}:{tag}: {e}")
        return False

    # Check for both amd64 and arm64 platforms in the manifest
    manifests = manifest.get("manifests", [])
    platforms = {m.get("platform", {}).get("architecture") for m in manifests if "platform" in m}
    return "amd64" in platforms and "arm64" in platforms

def main():
    version = None
    if len(sys.argv) > 1:
        version = sys.argv[1]
        if not CALVER_REGEX.match(version):
            print(f"Provided version '{version}' does not match calver format yyyy-mm-dd.")
            sys.exit(1)
    else:
        tags = []
        for repo in REPOS:
            tag = get_latest_calver_tag(repo)
            if not tag:
                print(f"No calver tag found for repo {repo}")
                sys.exit(1)
            tags.append(tag)
        if not all_repos_same_tag(tags):
            print(f"Repos have different latest calver tags: {dict(zip(REPOS, tags))}")
            sys.exit(1)
        version = tags[0]
        print(f"Using latest calver tag: {version}")

    # Check all repos have this tag
    for repo in REPOS:
        url = GITHUB_API.format(repo=repo)
        resp = github_get(url)
        tags = [tag['name'] for tag in resp.json()]
        if version not in tags:
            print(f"Repo {repo} does not have tag {version}")
            sys.exit(1)

    # Check all images exist
    all_exist = True
    for tmpl in IMAGE_TEMPLATES:
        image = tmpl.format(version=version)
        image_name, tag = image.rsplit(':', 1)
        exists = docker_image_tag_exists(image_name, tag)
        print(f"Checking image {image} ... {'OK' if exists else 'MISSING'}")
        if not exists:
            all_exist = False

    if all_exist:
        print("All checks passed.")
        sys.exit(0)
    else:
        print("Some images are missing.")
        sys.exit(2)

if __name__ == "__main__":
    main()
