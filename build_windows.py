#!/usr/bin/env python3
"""
Windows Build Script
Run this script on Windows to generate executable
"""
import os
import subprocess
import shutil
import platform

# Check if running on Windows
if platform.system() != 'Windows' and os.name != 'nt':
    print("Warning: This script is not running on Windows, compatibility issues may occur")
    print("Recommended to run this script on Windows")

# Clean old build files
def clean_build():
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('BarcodeSystem_Windows.spec'):
        os.remove('BarcodeSystem_Windows.spec')
    print("[OK] Clean completed")

# Install dependencies
def install_dependencies():
    print("[INFO] Installing dependencies...")
    if os.path.exists('requirements.txt'):
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
    else:
        subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'python-barcode', 'Pillow'], check=True)
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    print("[OK] Dependencies installed")

# Build executable
def build_executable():
    print("[INFO] Building executable...")
    # Choose correct separator based on OS
    import sys
    if sys.platform.startswith('win'):
        sep = ';'
    else:
        sep = ':'
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=BarcodeSystem',
        '--distpath', 'dist/windows',
        '--add-data', f'templates{sep}templates',
        '--add-data', f'static{sep}static',
        '--icon=icon.ico',
        'start.py'
    ]
    subprocess.run(cmd, check=True)
    print("[OK] Build completed")

# Copy database file
def copy_database():
    if os.path.exists('order_system.db'):
        if os.path.exists('dist/windows'):
            shutil.copy('order_system.db', 'dist/windows/')
            print("[OK] Database copied")

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
        
        print("\n[SUCCESS] Build successful!")
        print("Executable location: dist/windows/BarcodeSystem.exe")
        print("\nUsage:")
        print("1. Double-click dist/windows/BarcodeSystem.exe to run")
        print("2. System will open browser at http://127.0.0.1:888")
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")

if __name__ == '__main__':
    main()
