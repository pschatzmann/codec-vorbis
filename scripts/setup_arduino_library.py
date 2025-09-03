#!/usr/bin/env python3

# 
# Creates/Updates the Arduino library from the original source code
#
import os
import shutil
import subprocess
import sys

def setup_vorbis():

    # Source directories
    include_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/vorbis/include'))
    lib_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/vorbis/lib'))

    # Destination directory
    # Now set to 'src/vorbis' directory in the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dest_dir = os.path.join(project_root, 'src', 'vorbis')

    # Ensure dest_dir exists before any file operations
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Copy all .h files from modes directory into src/vorbis/modes
    modes_src = os.path.join(lib_src, 'modes')
    modes_dest = os.path.join(dest_dir, 'modes')
    if os.path.exists(modes_src):
        if not os.path.exists(modes_dest):
            os.makedirs(modes_dest)
        for file in os.listdir(modes_src):
            if file.endswith('.h'):
                src_file = os.path.join(modes_src, file)
                dst_file = os.path.join(modes_dest, file)
                shutil.copy2(src_file, dst_file)

    # Recursively copy all subdirectories and .h files from books
    books_src = os.path.join(lib_src, 'books')
    books_dest = os.path.join(dest_dir, 'books')
    if os.path.exists(books_src):
        for root, dirs, files in os.walk(books_src):
            rel_path = os.path.relpath(root, books_src)
            dest_subdir = os.path.join(books_dest, rel_path) if rel_path != '.' else books_dest
            if not os.path.exists(dest_subdir):
                os.makedirs(dest_subdir)
            for file in files:
                if file.endswith('.h'):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_subdir, file)
                    shutil.copy2(src_file, dst_file)

    # ...existing code...

    # File lists from CMakeLists.txt
    vorbis_headers = [
        "envelope.h", "lpc.h", "lsp.h", "codebook.h", "misc.h", "psy.h", "masking.h", "os.h",
        "mdct.h", "smallft.h", "highlevel.h", "registry.h", "scales.h", "window.h", "lookup.h",
        "lookup_data.h", "codec_internal.h", "backends.h", "bitrate.h"
    ]

    vorbis_sources = [
        "mdct.c", "smallft.c", "block.c", "envelope.c", "window.c", "lsp.c", "lpc.c",
        "analysis.c", "synthesis.c", "psy.c", "info.c", "floor1.c", "floor0.c",
        "res0.c", "mapping0.c", "registry.c", "codebook.c", "sharedbook.c",
        "lookup.c", "bitrate.c", "vorbisfile.c", 
    ]

    # Copy vorbis public headers directly into src/vorbis
    public_headers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/vorbis/include/vorbis'))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for header in ["codec.h", "vorbisenc.h", "vorbisfile.h"]:
        src_file = os.path.join(public_headers_dir, header)
        dst_file = os.path.join(dest_dir, header)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
        else:
            print(f"Warning: {src_file} not found.")

    # Copy vorbis header files
    for fname in vorbis_headers:
        src_file = os.path.join(lib_src, fname)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_dir)
        else:
            print(f"Warning: {src_file} not found.")

    # Copy vorbis source files
    for fname in vorbis_sources:
        src_file = os.path.join(lib_src, fname)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_dir)
        else:
            print(f"Warning: {src_file} not found.")


    print("Copy complete.")

def patch_includes(dest_dir):
    """Patch #include statements in .c and .h files in dest_dir."""
    # Build a map of all .h file locations (filename -> relative path from src)
    header_locations = {}
    src_root = os.path.dirname(dest_dir)
    for root, dirs, files in os.walk(src_root):
        for file in files:
            if file.endswith('.h'):
                rel_dir = os.path.relpath(root, src_root)
                rel_path = os.path.join(rel_dir, file) if rel_dir != '.' else file
                header_locations[file] = rel_path.replace('\\', '/')

    # Patch all .c and .h files recursively in dest_dir
    for root, dirs, files in os.walk(dest_dir):
        for fname in files:
            if fname.endswith('.c') or fname.endswith('.h'):
                file_path = os.path.join(root, fname)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                new_lines = []
                changed = False
                for line in lines:
                    if line.strip().startswith('#include "'):
                        start = line.find('"') + 1
                        end = line.find('"', start)
                        inc_file = line[start:end]
                        inc_base = os.path.basename(inc_file)
                        # Check if inc_file is in the same directory as the including file
                        inc_path = os.path.join(root, inc_file)
                        if os.path.exists(inc_path):
                            # File exists in current directory, do not patch
                            pass
                        elif inc_base in header_locations:
                            new_path = header_locations[inc_base]
                            if inc_file != new_path:
                                line = line.replace(inc_file, new_path)
                                changed = True
                    new_lines.append(line)
                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)


if __name__ == "__main__":
    setup_vorbis()
    # Patch includes for both vorbis and ogg
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    patch_includes(os.path.join(project_root, 'src', 'vorbis'))

    sys.exit(0)
