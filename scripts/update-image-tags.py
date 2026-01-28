#!/usr/bin/env python3

import sys
import os
import re


def update_file(filepath, release_tag):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to match image lines with :latest
    new_content, count = re.subn(
        r"(image:\s*[^:]+):latest\b", r"\1:" + release_tag, content
    )

    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {filepath} ({count} replacements")
    else:
        print(f"No changes in {filepath}")


def find_yaml_files(directory):
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith(".yaml"):
                yield os.path.join(root, name)


def update_deployment_script(release_tag, deploy_script):
    if os.path.exists(deploy_script):
        # Custom regex for --image=...:latest
        with open(deploy_script, "r", encoding="utf-8") as f:
            content = f.read()
        new_content, count = re.subn(
            r"(--image=[^:]+):latest\b", r"\1:" + release_tag, content
        )
        if count > 0:
            with open(deploy_script, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {deploy_script} ({count} replacements)")
        else:
            print(f"No changes in {deploy_script}")


def update_start_glvd_script(release_tag, script_path):
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Replace :latest with :<release_tag> in image references
        new_content, count = re.subn(
            r"(ghcr\.io/gardenlinux/[^:]+):latest\b", r"\1:" + release_tag, content
        )
        if count > 0:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {script_path} ({count} replacements)")
        else:
            print(f"No changes in {script_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <release-tag>".format(sys.argv[0]))
        sys.exit(1)

    release_tag = sys.argv[1]
    target_dir = "./deployment"

    for filepath in find_yaml_files(target_dir):
        update_file(filepath, release_tag)

    deploy_script = "deploy-k8s.sh"
    update_deployment_script(release_tag, deploy_script)

    # Update the podman start script as well
    start_glvd_script = os.path.join("deployment", "podman", "start-glvd.sh")
    update_start_glvd_script(release_tag, start_glvd_script)

    print("Done.")


if __name__ == "__main__":
    main()
