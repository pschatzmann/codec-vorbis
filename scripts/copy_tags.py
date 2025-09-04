#!/usr/bin/env python3

# 
# Main logic:
# - processes all tags from the original vorbis repo
# - checks out each tag
# - runs the setup script
# - creates and pushes the tag in the current repo
#

import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VORBIS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../original/vorbis'))
SETUP_SCRIPT = os.path.join(SCRIPT_DIR, 'setup_arduino_library.py')
TAG_SCRIPT = os.path.join(SCRIPT_DIR, 'create_and_push_tag.py')

# Get all tags in original/vorbis
def get_vorbis_tags():
    result = subprocess.run(['git', 'tag'], cwd=VORBIS_DIR, stdout=subprocess.PIPE, text=True, check=True)
    return [tag.strip() for tag in result.stdout.splitlines() if tag.strip()]

# Get all tags in current repo
def get_local_tags():
    result = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE, text=True, check=True)
    return set(tag.strip() for tag in result.stdout.splitlines() if tag.strip())

def checkout():
    original_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original'))
    vorbis_dir = os.path.join(original_dir, 'vorbis')
    if not os.path.exists(vorbis_dir):
        print(f"Cloning vorbis repository into {original_dir}...")
        subprocess.run(["git", "clone", "https://github.com/xiph/vorbis.git", vorbis_dir], check=True)

def update_library_properties_version(tag):
    """Update the version field in library.properties to the given tag."""
    lib_props_path = os.path.join(SCRIPT_DIR, '..', 'library.properties')
    if os.path.exists(lib_props_path):
        with open(lib_props_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        changed = False
        for line in lines:
            if line.startswith('version='):
                line = f'version={tag}\n'
                changed = True
            new_lines.append(line)
        if changed:
            with open(lib_props_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

def main():
    checkout()
    
    vorbis_tags = get_vorbis_tags()
    local_tags = get_local_tags()

    for tag in vorbis_tags:
        if 'beta' in tag.lower() or 'rc' in tag.lower():
            print(f"Tag '{tag}' contains 'beta' or 'rc', skipping.")
            continue
        if tag in local_tags:
            print(f"Tag '{tag}' already exists in local repo, skipping.")
            continue
        print(f"Checking out vorbis tag '{tag}'...")
        subprocess.run(['git', 'checkout', tag], cwd=VORBIS_DIR, check=True)

        update_library_properties_version(tag)
        
        print(f"Running setup_arduino_library.py for tag '{tag}'...")
        subprocess.run([sys.executable, SETUP_SCRIPT], check=True)
        print(f"Creating and pushing tag '{tag}'...")
        push_attempts = 0
        while push_attempts < 3:
            try:
                subprocess.run([sys.executable, TAG_SCRIPT, tag], check=True)
                break
            except subprocess.CalledProcessError:
                push_attempts += 1
                if push_attempts < 3:
                    print(f"Push failed for tag '{tag}', retrying in 5 seconds... (Attempt {push_attempts+1}/3)")
                    time.sleep(5)
                else:
                    print(f"Push failed for tag '{tag}' after 3 attempts. Skipping.")

if __name__ == '__main__':
    main()
    sys.exit(0)
