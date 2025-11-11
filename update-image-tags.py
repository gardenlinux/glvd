#!/usr/bin/env python3

import sys
import os
import re

def update_file(filepath, release_tag):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to match image lines with :latest
    new_content, count = re.subn(
        r'(image:\s*[^:]+):latest\b',
        r'\1:' + release_tag,
        content
    )

    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath} ({count} replacements")
    else:
        print(f"No changes in {filepath}")

def find_yaml_files(directory):
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith('.yaml'):
                yield os.path.join(root, name)

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <release-tag>".format(sys.argv[0]))
        sys.exit(1)

    release_tag = sys.argv[1]
    target_dir = './deployment'

    for filepath in find_yaml_files(target_dir):
        update_file(filepath, release_tag)

    deploy_script = 'deploy-k8s.sh'
    if os.path.exists(deploy_script):
        update_file(deploy_script, release_tag)

    print("Done.")

if __name__ == '__main__':
    main()
