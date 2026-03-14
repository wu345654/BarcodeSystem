#!/usr/bin/env python3
"""
macOS Build Script
Run this script on macOS to generate executable
"""

import os
import sys
import subprocess
import shutil
import platform

# Check if running on macOS
if platform.system() != 'Darwin':
    print("Warning: This script is not running on macOS, compatibility issues may occur")
    print("Recommended to run this script on macOS")

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
    print("macOS Build Script")
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
    spec_file = os.path.join(project_root, 'BarcodeSystem.spec')
    
    for path in [build_dir, dist_dir]:
        if os.path.exists(path):
            print(f"Removing directory: {path}")
            shutil.rmtree(path)
    
    if os.path.exists(spec_file):
        print(f"Removing file: {spec_file}")
        os.remove(spec_file)
    
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
    
    # 创建输出目录
    os.makedirs('dist/macos', exist_ok=True)
    # Build command
    pyinstaller_cmd = (
        f"pyinstaller --windowed --name BarcodeSystem "
        f"--distpath dist/macos "
        f"--add-data 'templates:templates' "
        f"--add-data 'static:static' "
        f"--clean "
        f"app.py"
    )
    
    result = run_command(pyinstaller_cmd, cwd=project_root)
    
    if result and result.returncode == 0:
        print("\nBuild successful!")
        
        # Copy database files
        print("Copying database files...")
        macos_dist_dir = os.path.join(project_root, 'dist', 'macos', 'BarcodeSystem')
        database_files = ['order_system.db']
        for db_file in database_files:
            src_db = os.path.join(project_root, db_file)
            if os.path.exists(src_db):
                # 确保目标目录存在
                os.makedirs(macos_dist_dir, exist_ok=True)
                dst_db = os.path.join(macos_dist_dir, db_file)
                shutil.copy2(src_db, dst_db)
                print(f"Copied {db_file} to dist/macos/BarcodeSystem directory")
            else:
                print(f"Warning: Database file {db_file} not found")
        
        # Create macOS run script
        print("Creating macOS run script...")
        run_script_path = os.path.join(macos_dist_dir, 'run_barcode_system.sh')
        
        with open(run_script_path, 'w') as f:
            f.write('''#!/bin/bash

# Barcode System Run Script (macOS)

echo "===================================="
echo "Barcode System Startup Script"
echo "===================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if executable exists
if [ ! -f "$SCRIPT_DIR/BarcodeSystem" ]; then
    echo "Error: BarcodeSystem executable not found!"
    exit 1
fi

# Check if database file exists
if [ ! -f "$SCRIPT_DIR/order_system.db" ]; then
    echo "Warning: order_system.db not found, system will create automatically"
fi

echo "Starting Barcode System..."
echo "System running at http://localhost:8888"
echo "Press Ctrl+C to stop service"
echo "===================================="

# Enter app directory
cd "$SCRIPT_DIR"

# Start system
./BarcodeSystem
''')
        
        # Set script permissions
        os.chmod(run_script_path, 0o755)
        
        # Create DMG package script (optional)
        print("Creating DMG package script...")
        dmg_script_path = os.path.join(macos_dist_dir, 'create_dmg.sh')
        
        with open(dmg_script_path, 'w') as f:
            f.write('''#!/bin/bash

# Create DMG installer script

echo "Creating DMG installer..."

# Set variables
APP_NAME="BarcodeSystem"
DMG_NAME="BarcodeSystem-macOS"
VOLUME_NAME="Barcode System"

# Create temp directory
TMP_DIR=$(mktemp -d)
mkdir -p "$TMP_DIR/$VOLUME_NAME"

# Copy files
cp -r "$APP_NAME" "$TMP_DIR/$VOLUME_NAME/"
cp "order_system.db" "$TMP_DIR/$VOLUME_NAME/"
cp "run_barcode_system.sh" "$TMP_DIR/$VOLUME_NAME/"

# Create DMG
hdiutil create -volname "$VOLUME_NAME" \\
    -srcfolder "$TMP_DIR/$VOLUME_NAME" \\
    -ov -format UDZO \\
    "$DMG_NAME.dmg"

# Clean temp directory
rm -rf "$TMP_DIR"

echo "DMG installer created: $DMG_NAME.dmg"
''')
        
        os.chmod(dmg_script_path, 0o755)
        
        print(f"\nBuild completed!")
        print(f"Executable location: {macos_dist_dir}/BarcodeSystem")
        print(f"Run script: {run_script_path}")
        print(f"DMG script: {dmg_script_path}")
        print("\nUsage:")
        print(f"1. Enter dist/macos/BarcodeSystem directory: cd {macos_dist_dir}")
        print("2. Run script: ./run_barcode_system.sh")
        print("3. Access in browser: http://localhost:8888")
        print("\nCreate DMG installer:")
        print("  ./create_dmg.sh")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
