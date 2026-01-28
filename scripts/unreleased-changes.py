#!/usr/bin/env python3

import urllib.request
import os
from datetime import datetime
import sys
import json

"""
This script checks which commits in the 'main' branch of glvd repositories
have not yet been included in the latest release tag. It queries the GitHub API
to determine the latest release tag for each repository, then lists all commits on 'main'
that are newer than that tag. This helps maintainers decide when a new release is warranted
by showing unreleased changes since the last release.
"""

REPOS = [
    "gardenlinux/glvd",
    "gardenlinux/glvd-api",
    "gardenlinux/glvd-postgres",
    "gardenlinux/glvd-data-ingestion",
]

GITHUB_API = "https://api.github.com"


def github_get(url):
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                raise Exception(f"HTTP {resp.status}")
            return resp.read().decode()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        sys.exit(1)


def get_latest_release_tag(repo):
    url = f"{GITHUB_API}/repos/{repo}/tags"
    resp = github_get(url)
    tags = [tag["name"] for tag in json.loads(resp)]
    # Filter tags that look like CalVer (YYYY.MM.DD)
    calver_tags = [t for t in tags if len(t) == 10 and t[:4].isdigit() and t[5:7].isdigit() and t[8:10].isdigit()]
    if not calver_tags:
        return None
    # Sort by date
    calver_tags.sort(key=lambda s: datetime.strptime(s, "%Y.%m.%d"))
    return calver_tags[-1]

def get_unreleased_commits(repo, latest_tag):
    # Get the SHA of the latest tag
    if latest_tag:
        tag_url = f"{GITHUB_API}/repos/{repo}/git/refs/tags/{latest_tag}"
        tag_resp = github_get(tag_url)
        tag_obj = json.loads(tag_resp)["object"]
        # If tag is annotated, dereference to the commit
        if tag_obj['type'] == 'tag':
            annotated_tag_url = tag_obj['url']
            annotated_tag_resp = github_get(annotated_tag_url)
            tag_sha = json.loads(annotated_tag_resp)["object"]["sha"]
        else:
            tag_sha = tag_obj['sha']
        # Get parent commit of the tag commit
        commit_url = f"{GITHUB_API}/repos/{repo}/commits/{tag_sha}"
        commit_resp = github_get(commit_url)
        parents = json.loads(commit_resp).get("parents", [])
        if parents:
            tag_parent_sha = parents[0]['sha']
        else:
            tag_parent_sha = None
    else:
        tag_parent_sha = None

    # Get commits on main
    commits_url = f"{GITHUB_API}/repos/{repo}/commits?sha=main"
    commits_resp = github_get(commits_url)
    commits = json.loads(commits_resp)

    unreleased = []
    for commit in commits:
        if tag_parent_sha and commit['sha'] == tag_parent_sha:
            break
        unreleased.append(f"{commit['sha'][:7]} {commit['commit']['message'].splitlines()[0]}")
    return "\n".join(unreleased)

def main():
    for repo in REPOS:
        print(f"\nChecking {repo}...")
        latest_tag = get_latest_release_tag(repo)
        if latest_tag:
            print(f"Latest release tag: {latest_tag}")
        else:
            print("No release tags found.")
        commits = get_unreleased_commits(repo, latest_tag)
        if commits:
            print("Unreleased commits on main:")
            print(commits)
        else:
            print("No unreleased commits found.")

if __name__ == "__main__":
    main()
