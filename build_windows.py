#!/usr/bin/env python3
"""
Windows Build Script
Run this script on Windows to generate executable
"""
import os
import subprocess
import shutil
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist', 'windows')

if platform.system() != 'Windows' and os.name != 'nt':
    print("Warning: This script is not running on Windows, compatibility issues may occur")
    print("Recommended to run this script on Windows")

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

def install_dependencies():
    print("[INFO] Installing dependencies...")
    requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
    if os.path.exists(requirements_file):
        subprocess.run(['pip', 'install', '-r', requirements_file], check=True)
    else:
        subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'python-barcode', 'Pillow'], check=True)
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    print("[OK] Dependencies installed")

def build_executable():
    print("[INFO] Building executable...")
    print(f"[DEBUG] Base directory: {BASE_DIR}")
    print(f"[DEBUG] Dist directory: {DIST_DIR}")
    
    app_py = os.path.join(BASE_DIR, 'app.py')
    templates_dir = os.path.join(BASE_DIR, 'templates')
    static_dir = os.path.join(BASE_DIR, 'static')
    font_dir = os.path.join(BASE_DIR, 'font')
    mic_dir = os.path.join(BASE_DIR, 'mic')
    icon_file = os.path.join(BASE_DIR, 'icon.ico')
    
    print(f"[DEBUG] app.py exists: {os.path.exists(app_py)}")
    print(f"[DEBUG] templates directory exists: {os.path.exists(templates_dir)}")
    print(f"[DEBUG] static directory exists: {os.path.exists(static_dir)}")
    print(f"[DEBUG] font directory exists: {os.path.exists(font_dir)}")
    print(f"[DEBUG] mic directory exists: {os.path.exists(mic_dir)}")
    print(f"[DEBUG] icon.ico exists: {os.path.exists(icon_file)}")
    
    try:
        os.makedirs(DIST_DIR, exist_ok=True)
        print(f"[DEBUG] Created dist directory: {DIST_DIR}")
    except Exception as e:
        print(f"[ERROR] Failed to create dist directory: {e}")
        raise
    
    if platform.system() == 'Windows':
        sep = ';'
    else:
        sep = ':'
    
    cmd = f'pyinstaller --onefile --name BarcodeSystem --distpath "{DIST_DIR}" --add-data "{templates_dir}{sep}templates" --add-data "{static_dir}{sep}static" --add-data "{font_dir}{sep}font" --add-data "{mic_dir}{sep}mic" --icon "{icon_file}" --clean "{app_py}"'
    
    print(f"[DEBUG] Running command: {cmd}")
    
    try:
        print("[DEBUG] Starting PyInstaller...")
        subprocess.run(cmd, shell=True, check=True, cwd=BASE_DIR)
        print("[DEBUG] PyInstaller completed successfully")
    except Exception as e:
        print(f"[ERROR] Failed to run PyInstaller: {e}")
        fallback_cmd = f'pyinstaller --onefile --name BarcodeSystem "{app_py}"'
        print(f"[DEBUG] Fallback command: {fallback_cmd}")
        try:
            subprocess.run(fallback_cmd, shell=True, check=True, cwd=BASE_DIR)
            print("[DEBUG] Fallback command completed successfully")
        except Exception as fallback_e:
            print(f"[ERROR] Fallback command also failed: {fallback_e}")
            raise
    
    print("[OK] Build completed")

def copy_database():
    db_file = os.path.join(BASE_DIR, 'order_system.db')
    if os.path.exists(db_file):
        os.makedirs(DIST_DIR, exist_ok=True)
        dest_db = os.path.join(DIST_DIR, 'order_system.db')
        shutil.copy(db_file, dest_db)
        print(f"[OK] Database copied to: {dest_db}")
    else:
        print("[WARNING] order_system.db not found, skipping copy")

def create_run_script():
    run_script = os.path.join(DIST_DIR, 'run.bat')
    with open(run_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
chcp 65001 >nul
title 条码系统

echo ====================================
echo 条码系统启动中...
echo ====================================
echo.

REM Check if executable exists
if not exist "BarcodeSystem.exe" (
    echo [错误] BarcodeSystem.exe 不存在！
    pause
    exit /b 1
)

REM Check if database exists
if not exist "order_system.db" (
    echo [提示] 数据库文件不存在，系统将自动创建...
)

echo [信息] 正在启动系统...
echo [信息] 系统将在 http://127.0.0.1:8888 上运行
echo [信息] 按 Ctrl+C 停止服务
echo ====================================
echo.

REM Start the application
start "" http://127.0.0.1:8888
BarcodeSystem.exe

pause
''')
    print(f"[OK] Run script created: {run_script}")

def main():
    print("============================================================")
    print("Windows Build Script")
    print("============================================================")
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        copy_database()
        create_run_script()
        
        if os.path.exists(DIST_DIR):
            exe_path = os.path.join(DIST_DIR, 'BarcodeSystem.exe')
            if os.path.exists(exe_path):
                print("\n[SUCCESS] Build successful!")
                print(f"Executable location: {exe_path}")
                print(f"Executable size: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
                print("\nUsage:")
                print(f"1. Double-click run.bat to run")
                print("2. Or double-click BarcodeSystem.exe to run")
                print("3. System will open browser at http://127.0.0.1:8888")
            else:
                for item in os.listdir(DIST_DIR):
                    if item.endswith('.exe'):
                        exe_path = os.path.join(DIST_DIR, item)
                        print("\n[SUCCESS] Build successful!")
                        print(f"Executable location: {exe_path}")
                        print(f"Executable size: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
                        print("\nUsage:")
                        print(f"1. Double-click run.bat to run")
                        print("2. Or double-click BarcodeSystem.exe to run")
                        print("3. System will open browser at http://127.0.0.1:8888")
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
