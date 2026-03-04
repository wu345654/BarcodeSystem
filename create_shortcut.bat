@echo off

REM 创建带有图标的快捷方式
REM 在 Windows 上运行此文件

cls
echo =============================================================
echo 创建运行脚本快捷方式
echo =============================================================
echo
echo [INFO] 正在创建快捷方式...
echo

REM 获取当前目录
set "current_dir=%~dp0"

REM 快捷方式名称
set "shortcut_name=运行条码系统.lnk"

REM 目标文件
set "target_file=%current_dir%run_windows.bat"

REM 图标文件
set "icon_file=%current_dir%icon.ico"

REM 创建快捷方式
powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%current_dir%%shortcut_name%'); $Shortcut.TargetPath = '%target_file%'; $Shortcut.IconLocation = '%icon_file%'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo [SUCCESS] 快捷方式创建成功！
    echo [INFO] 快捷方式位置: %current_dir%%shortcut_name%
    echo [INFO] 双击快捷方式即可运行条码系统
) else (
    echo [ERROR] 快捷方式创建失败
)

echo
echo =============================================================
pause