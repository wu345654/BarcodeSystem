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
    # 打印当前工作目录
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    # Choose correct separator based on OS
    import sys
    if sys.platform.startswith('win'):
        sep = ';'
    else:
        sep = ':'
    # 创建输出目录
    os.makedirs('dist/windows', exist_ok=True)
    print(f"[DEBUG] Created directory: dist/windows")
    print(f"[DEBUG] Directory exists: {os.path.exists('dist/windows')}")
    # 使用更保守的配置，避免 --onefile 可能的问题
    cmd = [
        'pyinstaller',
        '--name=BarcodeSystem',
        '--distpath', 'dist/windows',
        '--add-data', f'templates{sep}templates',
        '--add-data', f'static{sep}static',
        '--icon=icon.ico',
        '--clean',
        '--log-level', 'DEBUG',
        'start.py'
    ]
    print(f"[DEBUG] Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    # 检查构建结果
    print(f"[DEBUG] After build - dist/windows exists: {os.path.exists('dist/windows')}")
    if os.path.exists('dist/windows'):
        print(f"[DEBUG] Contents of dist/windows: {os.listdir('dist/windows')}")
        if os.path.exists('dist/windows/BarcodeSystem'):
            print(f"[DEBUG] Contents of dist/windows/BarcodeSystem: {os.listdir('dist/windows/BarcodeSystem')}")
    print("[OK] Build completed")

# Copy database file
def copy_database():
    if os.path.exists('order_system.db'):
        # 确保目标目录存在
        os.makedirs('dist/windows/BarcodeSystem', exist_ok=True)
        shutil.copy('order_system.db', 'dist/windows/BarcodeSystem/')
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
        print("Executable location: dist/windows/BarcodeSystem/BarcodeSystem.exe")
        print("\nUsage:")
        print("1. Double-click dist/windows/BarcodeSystem/BarcodeSystem.exe to run")
        print("2. System will open browser at http://127.0.0.1:888")
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")

if __name__ == '__main__':
    main()
