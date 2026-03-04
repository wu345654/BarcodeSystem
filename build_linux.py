#!/usr/bin/env python3
"""
Linux Build Script
Run this script on Linux to generate executable
"""

import os
import sys
import subprocess
import shutil
import platform

# Check if running on Linux
if platform.system() != 'Linux':
    print("Warning: This script is not running on Linux, compatibility issues may occur")
    print("Recommended to run this script on Linux")

def run_command(cmd, cwd=None):
    """Run command and return result"""
    print(f"Executing command: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"Error executing command: {e}")
        return None

def main():
    """Main function"""
    print("========================================")
    print("Linux Build Script")
    print("========================================")
    
    # Project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Project root: {project_root}")
    
    # Check required files
    required_files = [
        'app.py',
        'database.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        file_path = os.path.join(project_root, file)
        if not os.path.exists(file_path):
            print(f"Error: Missing required file {file}!")
            sys.exit(1)
    
    # Clean old build files
    print("\nCleaning old build files...")
    build_dir = os.path.join(project_root, 'build')
    dist_dir = os.path.join(project_root, 'dist')
    
    for dir_path in [build_dir, dist_dir]:
        if os.path.exists(dir_path):
            print(f"Removing directory: {dir_path}")
            shutil.rmtree(dir_path)
    
    # Check and install dependencies
    print("\nChecking and installing dependencies...")
    requirements_file = os.path.join(project_root, 'requirements.txt')
    
    # Install PyInstaller
    print("Installing PyInstaller...")
    run_command("pip3 install pyinstaller")
    
    # Install project dependencies
    print("Installing project dependencies...")
    run_command(f"pip3 install -r {requirements_file}")
    
    # Build with PyInstaller
    print("\nBuilding with PyInstaller...")
    
    # Build command
    pyinstaller_cmd = (
        f"pyinstaller --onefile --name BarcodeSystem "
        f"--add-data 'templates:templates' "
        f"--add-data 'static:static' "
        f"app.py"
    )
    
    result = run_command(pyinstaller_cmd, cwd=project_root)
    
    if result and result.returncode == 0:
        print("\nBuild successful!")
        
        # Copy database files
        print("Copying database files...")
        database_files = ['order_system.db']
        for db_file in database_files:
            src_db = os.path.join(project_root, db_file)
            if os.path.exists(src_db):
                dst_db = os.path.join(dist_dir, db_file)
                shutil.copy2(src_db, dst_db)
                print(f"Copied {db_file} to dist directory")
            else:
                print(f"Warning: Database file {db_file} not found")
        
        # Create Linux run script
        print("Creating Linux run script...")
        run_script_path = os.path.join(dist_dir, 'run_barcode_system.sh')
        
        with open(run_script_path, 'w') as f:
            f.write('''#!/bin/bash

# Barcode System Run Script

echo "===================================="
echo "Barcode System Startup Script"
echo "===================================="

# Check if executable exists
if [ ! -f "./BarcodeSystem" ]; then
    echo "Error: BarcodeSystem executable not found!"
    exit 1
fi

# Check if database file exists
if [ ! -f "./order_system.db" ]; then
    echo "Warning: order_system.db not found, system will create automatically"
fi

echo "Starting Barcode System..."
echo "System running at http://localhost:5001"
echo "Press Ctrl+C to stop service"
echo "===================================="

# Start system
./BarcodeSystem
''')
        
        # Set script permissions
        os.chmod(run_script_path, 0o755)
        
        print(f"\nBuild completed!")
        print(f"Executable location: {os.path.join(dist_dir, 'BarcodeSystem')}")
        print(f"Run script: {run_script_path}")
        print("\nUsage:")
        print(f"1. Enter dist directory: cd {dist_dir}")
        print("2. Run script: ./run_barcode_system.sh")
        print("3. Access in browser: http://localhost:5001")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
