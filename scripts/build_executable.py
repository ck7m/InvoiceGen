#!/usr/bin/env python3
"""
Packaging script for Sai Krishna Networks GST Invoice Generator (Task 11).
Builds standalone executable / app bundle using PyInstaller and Flet assets.
"""

import os
import sys
import subprocess
import shutil

def build():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    print(f"Building SKN GST Invoice Generator in: {root_dir}")

    spec_file = os.path.join(root_dir, "SKN_Invoice_Generator.spec")
    if not os.path.exists(spec_file):
        print(f"Error: spec file not found at {spec_file}")
        sys.exit(1)

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", spec_file]
    print(f"Running command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n==========================================")
        print("Build completed successfully!")
        print("Outputs located in:")
        print(f" - Dist directory: {os.path.join(root_dir, 'dist')}")
        print("==========================================\n")
    else:
        print(f"Build failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
