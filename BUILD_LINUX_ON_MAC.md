# 在 macOS 上打包 Linux 可执行文件

## 限制说明

**PyInstaller 不支持跨平台打包**，在 macOS 上无法直接生成 Linux 可执行文件。

## 解决方案

### 方案一：在 Linux 环境中打包（推荐）

1. **使用云服务器**
   - 阿里云、腾讯云、AWS 等提供免费的 Linux 服务器
   - 上传项目代码到服务器
   - 运行打包脚本

2. **使用虚拟机**
   - 在 macOS 上安装 VirtualBox
   - 下载 Linux 镜像（Ubuntu、CentOS 等）
   - 在虚拟机中运行打包脚本

3. **使用 WSL（Windows Subsystem for Linux）**
   - 如果有 Windows 电脑，可以启用 WSL
   - 在 WSL 中运行打包脚本

### 方案二：使用 GitHub Actions 自动打包

创建 `.github/workflows/build.yml` 文件：

```yaml
name: Build Linux Executable

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
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
        pyinstaller --onefile --name BarcodeSystem \
          --add-data 'templates:templates' \
          --add-data 'static:static' \
          app.py
    
    - name: Copy database
      run: |
        if [ -f order_system.db ]; then cp order_system.db dist/; fi
    
    - name: Create run script
      run: |
        cat > dist/run_barcode_system.sh << 'EOF'
        #!/bin/bash
        echo "启动条码系统..."
        ./BarcodeSystem
        EOF
        chmod +x dist/run_barcode_system.sh
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: barcode-system-linux
        path: dist/
```

### 方案三：使用持续集成服务

- **GitHub Actions**（推荐）
- **GitLab CI**
- **CircleCI**
- **Travis CI**

这些服务提供免费的 Linux 环境，可以自动打包并下载生成的文件。

### 方案四：使用在线打包服务

一些在线服务提供跨平台打包功能：
- **PyInstaller Online**
- **Nuitka Online**

但需要注意安全性，不要上传敏感数据。

## 推荐流程

### 使用 GitHub Actions 打包

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/barcodesystem.git
   git push -u origin main
   ```

2. **创建工作流文件**
   - 在 `.github/workflows/` 目录创建 `build.yml`
   - 复制上面的 YAML 内容

3. **触发构建**
   - 推送代码到 GitHub
   - 或者在 GitHub Actions 页面手动触发

4. **下载构建产物**
   - 在 GitHub Actions 页面找到构建记录
   - 下载 `barcode-system-linux` 压缩包

### 使用 Linux 虚拟机打包

1. **安装 VirtualBox**
   ```bash
   # macOS
   brew install --cask virtualbox
   ```

2. **下载 Linux 镜像**
   - Ubuntu Desktop: https://ubuntu.com/download/desktop
   - CentOS: https://www.centos.org/download/

3. **创建虚拟机**
   - 分配至少 2GB 内存
   - 分配至少 20GB 磁盘空间

4. **在虚拟机中打包**
   ```bash
   # 上传项目到虚拟机
   scp -r BarcodeSystem user@vm-ip:/home/user/
   
   # SSH 登录虚拟机
   ssh user@vm-ip
   
   # 运行打包脚本
   cd BarcodeSystem
   python3 build_linux.py
   ```

## 快速测试

如果只是想快速测试，可以使用以下在线服务：

### 使用 Replit

1. 访问 https://replit.com
2. 创建 Python 项目
3. 上传代码
4. 运行打包命令

### 使用 Glitch

1. 访问 https://glitch.com
2. 创建项目
3. 上传代码
4. 运行打包命令

## 注意事项

1. **安全性**：不要在公共平台上上传敏感数据
2. **兼容性**：确保目标 Linux 系统与打包环境兼容
3. **依赖**：检查所有依赖是否在 Linux 上可用
4. **测试**：在目标 Linux 系统上测试生成的可执行文件

## 联系方式

如有问题，请联系系统管理员。
