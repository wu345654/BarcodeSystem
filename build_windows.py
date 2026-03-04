#!/usr/bin/env python3
"""
Windows Build Script
Run this script on Windows to generate executable
"""
import os
import subprocess
import shutil
import platform

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist', 'windows')
BARCODE_DIR = os.path.join(DIST_DIR, 'BarcodeSystem')

# Check if running on Windows
if platform.system() != 'Windows' and os.name != 'nt':
    print("Warning: This script is not running on Windows, compatibility issues may occur")
    print("Recommended to run this script on Windows")

# Clean old build files
def clean_build():
    build_dir = os.path.join(BASE_DIR, 'build')
    dist_dir = os.path.join(BASE_DIR, 'dist')
    spec_file = os.path.join(BASE_DIR, 'BarcodeSystem.spec')
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    print("[OK] Clean completed")

# Install dependencies
def install_dependencies():
    print("[INFO] Installing dependencies...")
    requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
    if os.path.exists(requirements_file):
        subprocess.run(['pip', 'install', '-r', requirements_file], check=True)
    else:
        subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'python-barcode', 'Pillow'], check=True)
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    print("[OK] Dependencies installed")

# Build executable
def build_executable():
    print("[INFO] Building executable...")
    print(f"[DEBUG] Base directory: {BASE_DIR}")
    print(f"[DEBUG] Dist directory: {DIST_DIR}")
    
    # Check if required files exist
    start_py = os.path.join(BASE_DIR, 'start.py')
    templates_dir = os.path.join(BASE_DIR, 'templates')
    static_dir = os.path.join(BASE_DIR, 'static')
    icon_file = os.path.join(BASE_DIR, 'icon.ico')
    
    print(f"[DEBUG] start.py exists: {os.path.exists(start_py)}")
    print(f"[DEBUG] templates directory exists: {os.path.exists(templates_dir)}")
    print(f"[DEBUG] static directory exists: {os.path.exists(static_dir)}")
    print(f"[DEBUG] icon.ico exists: {os.path.exists(icon_file)}")
    
    # Create output directories
    try:
        os.makedirs(DIST_DIR, exist_ok=True)
        print(f"[DEBUG] Created dist directory: {DIST_DIR}")
        print(f"[DEBUG] Dist directory exists after creation: {os.path.exists(DIST_DIR)}")
    except Exception as e:
        print(f"[ERROR] Failed to create dist directory: {e}")
        raise
    
    # Choose correct separator based on OS
    if platform.system() == 'Windows':
        sep = ';'
    else:
        sep = ':'
    
    # Build command with absolute paths
    cmd = [
        'pyinstaller',
        '--name=BarcodeSystem',
        '--distpath', DIST_DIR,
        '--add-data', f'{templates_dir}{sep}templates',
        '--add-data', f'{static_dir}{sep}static',
        '--icon', icon_file,
        '--clean',
        start_py
    ]
    
    print(f"[DEBUG] Running command: {' '.join(cmd)}")
    
    # Run with shell=True for Windows compatibility
    try:
        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True, cwd=BASE_DIR)
        print(f"[DEBUG] Command exit code: {result.returncode}")
        if result.stdout:
            print(f"[DEBUG] Command stdout: {result.stdout[:500]}...")  # Limit output
        if result.stderr:
            print(f"[DEBUG] Command stderr: {result.stderr[:500]}...")  # Limit output
        if result.returncode != 0:
            raise Exception(f"PyInstaller failed with exit code {result.returncode}")
    except Exception as e:
        print(f"[ERROR] Failed to run PyInstaller: {e}")
        raise
    
    # Check build results
    print(f"[DEBUG] After build - dist directory exists: {os.path.exists(DIST_DIR)}")
    if os.path.exists(DIST_DIR):
        print(f"[DEBUG] Contents of dist directory: {os.listdir(DIST_DIR)}")
        # Check if BarcodeSystem directory was created
        if os.path.exists(BARCODE_DIR):
            print(f"[DEBUG] BarcodeSystem directory exists: {os.path.exists(BARCODE_DIR)}")
            print(f"[DEBUG] Contents: {os.listdir(BARCODE_DIR)}")
        else:
            # Check if executable was created directly in dist/windows
            print(f"[DEBUG] Checking direct contents of dist/windows")
            for item in os.listdir(DIST_DIR):
                item_path = os.path.join(DIST_DIR, item)
                if os.path.isfile(item_path) and item.endswith('.exe'):
                    print(f"[DEBUG] Found executable: {item}")
    else:
        print(f"[ERROR] Dist directory does not exist after build")
    print("[OK] Build completed")

# Copy database file
def copy_database():
    db_file = os.path.join(BASE_DIR, 'order_system.db')
    if os.path.exists(db_file):
        # Ensure target directory exists
        os.makedirs(BARCODE_DIR, exist_ok=True)
        dest_db = os.path.join(BARCODE_DIR, 'order_system.db')
        shutil.copy(db_file, dest_db)
        print(f"[OK] Database copied to: {dest_db}")
    else:
        print("[WARNING] order_system.db not found, skipping copy")

# Main function
def main():
    print("============================================================")
    print("Windows Build Script")
    print("============================================================")
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        copy_database()
        
        # Check final result
        if os.path.exists(BARCODE_DIR):
            exe_path = os.path.join(BARCODE_DIR, 'BarcodeSystem.exe')
            if os.path.exists(exe_path):
                print("\n[SUCCESS] Build successful!")
                print(f"Executable location: {exe_path}")
                print("\nUsage:")
                print(f"1. Double-click {exe_path} to run")
                print("2. System will open browser at http://127.0.0.1:888")
            else:
                print("\n[WARNING] Executable not found in expected location")
                print(f"Contents of {BARCODE_DIR}: {os.listdir(BARCODE_DIR)}")
        else:
            # Check if executable is in dist/windows directly
            if os.path.exists(DIST_DIR):
                for item in os.listdir(DIST_DIR):
                    if item.endswith('.exe'):
                        exe_path = os.path.join(DIST_DIR, item)
                        print("\n[SUCCESS] Build successful!")
                        print(f"Executable location: {exe_path}")
                        print("\nUsage:")
                        print(f"1. Double-click {exe_path} to run")
                        print("2. System will open browser at http://127.0.0.1:888")
                        break
                else:
                    print("\n[ERROR] Executable not found")
                    print(f"Contents of {DIST_DIR}: {os.listdir(DIST_DIR)}")
            else:
                print("\n[ERROR] Dist directory not found")
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
