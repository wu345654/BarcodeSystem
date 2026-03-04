#!/usr/bin/env python3
"""
Windows版本打包脚本
在Windows系统上运行此脚本以生成可执行文件
"""
import os
import subprocess
import shutil

# 清理旧的构建文件
def clean_build():
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('BarcodeSystem_Windows.spec'):
        os.remove('BarcodeSystem_Windows.spec')
    print("✅ 清理完成")

# 安装依赖
def install_dependencies():
    print("📦 安装依赖...")
    subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'python-barcode', 'Pillow==9.5.0'], check=True)
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    print("✅ 依赖安装完成")

# 打包可执行文件
def build_executable():
    print("🚀 打包可执行文件...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=BarcodeSystem',
        '--add-data', 'templates;templates',
        '--add-data', 'static;static',
        '--icon=icon.ico',
        'start.py'
    ]
    subprocess.run(cmd, check=True)
    print("✅ 打包完成")

# 复制数据库文件
def copy_database():
    if os.path.exists('order_system.db'):
        if os.path.exists('dist'):
            shutil.copy('order_system.db', 'dist/')
            print("✅ 数据库文件复制完成")

# 主函数
def main():
    print("============================================================")
    print("📦 Windows版本打包脚本")
    print("============================================================")
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        copy_database()
        
        print("\n🎉 打包成功！")
        print("可执行文件位置: dist/BarcodeSystem.exe")
        print("\n使用方法:")
        print("1. 双击 dist/BarcodeSystem.exe 运行系统")
        print("2. 系统会自动在浏览器中打开 http://127.0.0.1:888")
    except Exception as e:
        print(f"❌ 打包失败: {e}")

if __name__ == '__main__':
    main()
