#!/usr/bin/env python3
import sys
import subprocess

if len(sys.argv) != 2:
    print("Usage: python create_and_push_tag.py <tag_name>")
    sys.exit(1)

tag_name = sys.argv[1]

# Commit all changes with the tag name as the commit message
push_cmd = ["git", "push", "origin", "master"]
try:
    subprocess.run(['git', 'add', '--all'], check=True)
    subprocess.run(['git', 'commit', '-m', tag_name], check=True)
    subprocess.run(push_cmd, check=True)
    print(f"Tag 'main' pushed to origin.")
except subprocess.CalledProcessError:
    print(f"Failed to push tag 'main' to origin.")
    exit(2)


# Create the tag
tag_cmd = ["git", "tag", tag_name]
try:
    subprocess.run(tag_cmd, check=True)
    print(f"Tag '{tag_name}' created.")
except subprocess.CalledProcessError:
    print(f"Failed to create tag '{tag_name}'.")
    sys.exit(2)

# Push the tag to GitHub
push_cmd = ["git", "push", "origin", tag_name]
try:
    subprocess.run(push_cmd, check=True)
    print(f"Tag '{tag_name}' pushed to origin.")
except subprocess.CalledProcessError:
    print(f"Failed to push tag '{tag_name}' to origin.")
    sys.exit(3)
