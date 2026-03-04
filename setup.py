from cx_Freeze import setup, Executable
import os

# 定义包含的文件和目录
include_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('order_system.db', 'order_system.db')
]

# 定义依赖项
packages = [
    'flask',
    'flask_cors',
    'barcode',
    'PIL',
    'sqlite3'
]

# 配置打包选项
setup(
    name="BarcodeSystem",
    version="1.0",
    description="订单条码管理系统",
    author="System",
    options={
        "build_exe": {
            "packages": packages,
            "include_files": include_files,
            "excludes": ["tkinter"],
            "build_exe": "./build"
        }
    },
    executables=[
        Executable(
            "start.py",
            base=None,  # 使用控制台模式
            target_name="BarcodeSystem",
            shortcut_name="订单条码管理系统",
            shortcut_dir="DesktopFolder"
        )
    ]
)
