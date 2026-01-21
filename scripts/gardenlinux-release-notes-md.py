#!/usr/bin/env python3 -I

import argparse
import urllib.request
import urllib.error
import json


"""
Generates a markdown-formatted list of closed CVEs from Garden Linux Vulnerability Database (GLVD) data.
This script replicates the release notes generation used in the Garden Linux release pipeline.
It can be used to manually create or update the CVE list for patch releases when needed.
"""


def fetch_patch_release_notes(hostname, version):
    url = f"{hostname}/v1/releaseNotes/{version}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"No release notes found for version {version}.")
            exit(1)
        else:
            raise
    except urllib.error.URLError as e:
        print(f"Failed to connect: {e}")
        exit(1)


def generate_formatted_output(data):
    output = [
        "The following packages have been upgraded, to address the mentioned CVEs:"
    ]
    for package in data["packageList"]:
        upgrade_line = (
            f"- upgrade '{package['sourcePackageName']}' from `{package['oldVersion']}` "
            f"to `{package['newVersion']}`"
        )
        output.append(upgrade_line)

        if package["fixedCves"]:
            for c in package["fixedCves"]:
                output.append(f"  - {c}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Print information about fixed CVEs in Garden Linux patch releases."
    )
    parser.add_argument(
        "--hostname",
        type=str,
        required=False,
        default="https://security.gardenlinux.org",
        help="The hostname of the API endpoint.",
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="The version number for the patch release notes.",
    )

    args = parser.parse_args()

    data = fetch_patch_release_notes(args.hostname, args.version)
    formatted_output = generate_formatted_output(data)
    print(formatted_output)


if __name__ == "__main__":
    main()
