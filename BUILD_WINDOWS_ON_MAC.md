# 在 macOS 上打包 Windows EXE 文件

## 限制说明

**PyInstaller 不支持跨平台打包**，在 macOS 上无法直接生成 Windows 可执行文件（.exe）。

## 解决方案

### 方案一：使用 GitHub Actions 自动打包（推荐）

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/barcodesystem.git
   git push -u origin main
   ```

2. **创建工作流文件**
   
   创建 `.github/workflows/build.yml` 文件：

   ```yaml
   name: Build Windows EXE

   on:
     push:
       branches: [ main ]
     workflow_dispatch:

   jobs:
     build:
       runs-on: windows-latest
       
       steps:
       - uses: actions/checkout@v2
       
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.9'
       
       - name: Install dependencies
         run: |
           pip install pyinstaller
           pip install -r requirements.txt
       
       - name: Build with PyInstaller
         run: |
           pyinstaller --onefile --windowed --name BarcodeSystem `
             --add-data 'templates;templates' `
             --add-data 'static;static' `
             --icon=icon.ico `
             app.py
       
       - name: Copy database
         run: |
           if (Test-Path order_system.db) { Copy-Item order_system.db dist/ }
       
       - name: Create run script
         run: |
           @"
           @echo off
           echo ====================================
           echo 条码系统启动脚本
           echo ====================================
           echo 正在启动条码系统...
           echo 系统将在 http://localhost:5001 上运行
           echo 按 Ctrl+C 停止服务
           echo ====================================
           BarcodeSystem.exe
           pause
           "@ | Out-File -Encoding ASCII dist/run_barcode_system.bat
       
       - name: Create README
         run: |
           @"
           # 条码系统 Windows 版本
           
           ## 使用方法
           
           1. 双击 `run_barcode_system.bat` 启动系统
           2. 在浏览器中访问: http://localhost:5001
           
           ## 注意事项
           
           - 首次运行可能需要防火墙允许
           - 确保端口 5001 未被占用
           - 数据库文件：order_system.db
           "@ | Out-File -Encoding UTF8 dist/README.txt
       
       - name: Upload artifacts
         uses: actions/upload-artifact@v2
         with:
           name: barcode-system-windows
           path: dist/
   ```

3. **触发构建**
   - 推送代码到 GitHub
   - 或者在 GitHub Actions 页面手动触发

4. **下载构建产物**
   - 在 GitHub Actions 页面找到构建记录
   - 下载 `barcode-system-windows` 压缩包

### 方案二：使用 Windows 虚拟机

1. **安装虚拟机软件**
   - VMware Fusion: https://www.vmware.com/products/fusion
   - VirtualBox: https://www.virtualbox.org

2. **下载 Windows 镜像**
   - Windows 10/11 评估版: https://www.microsoft.com/evalcenter

3. **创建虚拟机**
   - 分配至少 4GB 内存
   - 分配至少 40GB 磁盘空间

4. **在虚拟机中打包**
   ```powershell
   # 上传项目到虚拟机
   # 使用共享文件夹或网络共享
   
   # 进入项目目录
   cd C:\path\to\BarcodeSystem
   
   # 安装依赖
   pip install pyinstaller
   pip install -r requirements.txt
   
   # 运行打包脚本
   python build_windows.py
   ```

### 方案三：使用云服务器

1. **使用 Azure Windows 虚拟机**
   - 提供免费的 Windows 服务器
   - 上传项目代码
   - 运行打包脚本

2. **使用 AWS EC2**
   - 选择 Windows 实例
   - 远程桌面连接
   - 运行打包脚本

### 方案四：使用在线打包服务

一些在线服务提供跨平台打包功能：
- **PyInstaller Online**
- **Nuitka Online**

但需要注意安全性，不要上传敏感数据。

## 推荐流程（GitHub Actions）

### 详细步骤

1. **准备代码**
   ```bash
   # 确保项目结构正确
   BarcodeSystem/
   ├── app.py
   ├── database.py
   ├── requirements.txt
   ├── templates/
   ├── static/
   └── .github/
       └── workflows/
           └── build.yml
   ```

2. **创建图标文件**
   - 准备一个 256x256 的 PNG 图片
   - 使用在线工具转换为 ICO 格式：https://convertico.com
   - 保存为 `icon.ico`

3. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Add Windows build workflow"
   git push
   ```

4. **查看构建状态**
   - 访问 https://github.com/your-username/barcodesystem/actions
   - 等待构建完成（通常 2-5 分钟）

5. **下载构建产物**
   - 点击构建记录
   - 在 "Artifacts" 部分下载 `barcode-system-windows`
   - 解压后得到 `BarcodeSystem.exe`

## 本地测试（使用 Parallels Desktop）

如果需要在本地测试：

1. **安装 Parallels Desktop**
   - macOS 上最流行的虚拟机软件
   - 下载地址：https://www.parallels.com/products/desktop

2. **安装 Windows**
   - 使用 Parallels 的快速安装功能
   - 自动下载并安装 Windows 10/11

3. **在 Windows 中打包**
   ```powershell
   # 将项目文件夹拖入 Windows 虚拟机
   # 打开命令提示符
   cd Desktop\BarcodeSystem
   pip install pyinstaller
   pip install -r requirements.txt
   python build_windows.py
   ```

## 使用打包好的 EXE 文件

### 在 Windows 上运行

1. **解压文件**
   - 将下载的压缩包解压到任意目录

2. **运行系统**
   - 双击 `run_barcode_system.bat`
   - 或直接双击 `BarcodeSystem.exe`

3. **访问系统**
   - 打开浏览器
   - 访问 http://localhost:5001

### 分发给其他用户

1. **打包成 ZIP**
   ```powershell
   Compress-Archive -Path dist\* -DestinationPath BarcodeSystem-Windows.zip
   ```

2. **创建安装说明**
   - 包含系统要求
   - 包含使用方法
   - 包含故障排除

## 注意事项

1. **安全性**
   - 不要在公共平台上上传敏感数据
   - 使用私有 GitHub 仓库

2. **兼容性**
   - Windows 10/11 (64位)
   - 需要 .NET Framework 4.0+（通常已安装）

3. **防火墙**
   - 首次运行可能需要允许防火墙
   - 确保端口 5001 未被阻止

4. **杀毒软件**
   - 某些杀毒软件可能误报
   - 添加到信任列表

5. **数字签名**
   - 未签名的 EXE 可能被警告
   - 购买代码签名证书进行签名

## 故障排除

### 构建失败

- 检查 `requirements.txt` 是否完整
- 检查 Python 版本是否兼容
- 查看 GitHub Actions 日志

### 运行失败

- 检查端口 5001 是否被占用
- 检查防火墙设置
- 检查杀毒软件是否阻止

### 打包文件过大

- 使用 `--onefile` 选项（已使用）
- 清理不必要的依赖
- 使用 UPX 压缩

## 联系方式

如有问题，请联系系统管理员。
