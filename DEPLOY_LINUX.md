# 条码系统 Linux 部署指南

## 部署方式一：使用 PyInstaller 打包部署（推荐）

### 1. 在开发环境打包

在 macOS/Windows 开发环境中执行：

```bash
# 进入项目目录
cd /path/to/BarcodeSystem

# 运行 Linux 打包脚本
python3 build_linux.py
```

打包完成后，会在 `dist` 目录生成：
- `BarcodeSystem` - 可执行文件
- `order_system.db` - 数据库文件
- `run_barcode_system.sh` - 启动脚本

### 2. 上传到 Linux 服务器

```bash
# 使用 scp 上传
cd dist
scp -r . user@linux-server:/opt/barcodesystem/

# 或者使用 rsync
rsync -avz . user@linux-server:/opt/barcodesystem/
```

### 3. 在 Linux 服务器上运行

```bash
# SSH 登录服务器
ssh user@linux-server

# 进入目录
cd /opt/barcodesystem

# 赋予执行权限
chmod +x BarcodeSystem run_barcode_system.sh

# 运行系统
./run_barcode_system.sh
```

---

## 部署方式二：使用 Python 直接运行

### 1. 上传源代码

```bash
# 上传整个项目目录
scp -r BarcodeSystem user@linux-server:/opt/
```

### 2. 在 Linux 服务器上配置环境

```bash
# SSH 登录服务器
ssh user@linux-server

# 进入项目目录
cd /opt/BarcodeSystem

# 安装 Python3 和 pip（如果未安装）
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 安装依赖
pip3 install -r requirements.txt
```

### 3. 运行系统

```bash
# 直接运行
python3 app.py

# 或者使用 nohup 后台运行
nohup python3 app.py > app.log 2>&1 &

# 查看日志
tail -f app.log
```

---

## 部署方式三：使用 Docker 部署（推荐生产环境）

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python3", "app.py"]
```

### 2. 构建并运行 Docker 容器

```bash
# 构建镜像
docker build -t barcodesystem .

# 运行容器
docker run -d \
  --name barcodesystem \
  -p 5001:5001 \
  -v $(pwd)/order_system.db:/app/order_system.db \
  barcodesystem

# 查看日志
docker logs -f barcodesystem
```

---

## 部署方式四：使用 systemd 服务（推荐生产环境）

### 1. 创建 systemd 服务文件

```bash
sudo nano /etc/systemd/system/barcodesystem.service
```

添加以下内容：

```ini
[Unit]
Description=Barcode System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/BarcodeSystem
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
ExecStart=/usr/bin/python3 /opt/BarcodeSystem/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 启动并启用服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start barcodesystem

# 设置开机自启
sudo systemctl enable barcodesystem

# 查看状态
sudo systemctl status barcodesystem

# 查看日志
sudo journalctl -u barcodesystem -f
```

---

## 部署方式五：使用 Nginx + Gunicorn（生产环境最佳实践）

### 1. 安装 Gunicorn

```bash
pip3 install gunicorn
```

### 2. 创建 Gunicorn 配置文件

```bash
nano /opt/BarcodeSystem/gunicorn.conf.py
```

添加：

```python
bind = "127.0.0.1:5001"
workers = 4
worker_class = "sync"
worker_connections = 1000
keepalive = 2
timeout = 30
graceful_timeout = 30
accesslog = "/var/log/barcodesystem/access.log"
errorlog = "/var/log/barcodesystem/error.log"
```

### 3. 创建 systemd 服务

```bash
sudo nano /etc/systemd/system/barcodesystem.service
```

添加：

```ini
[Unit]
Description=Barcode System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/BarcodeSystem
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
ExecStart=/usr/local/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/barcodesystem
```

添加：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/BarcodeSystem/static;
        expires 30d;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/barcodesystem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 启动服务

```bash
sudo systemctl start barcodesystem
sudo systemctl enable barcodesystem
```

---

## 常用命令

### 查看系统状态

```bash
# 查看进程
ps aux | grep barcodesystem

# 查看端口
netstat -tlnp | grep 5001

# 查看日志
tail -f /var/log/barcodesystem/error.log
```

### 重启服务

```bash
# 使用 systemd
sudo systemctl restart barcodesystem

# 使用 Docker
docker restart barcodesystem
```

### 停止服务

```bash
# 使用 systemd
sudo systemctl stop barcodesystem

# 使用 Docker
docker stop barcodesystem
```

### 备份数据库

```bash
# 备份数据库
cp /opt/BarcodeSystem/order_system.db /opt/BarcodeSystem/order_system.db.backup.$(date +%Y%m%d)

# 或者使用 SQLite 备份
sqlite3 /opt/BarcodeSystem/order_system.db ".backup '/opt/backup/order_system.db'"
```

---

## 故障排除

### 端口被占用

```bash
# 查看占用 5001 端口的进程
sudo lsof -i :5001

# 结束进程
sudo kill -9 <PID>
```

### 权限问题

```bash
# 修改目录权限
sudo chown -R www-data:www-data /opt/BarcodeSystem
sudo chmod -R 755 /opt/BarcodeSystem
```

### 防火墙设置

```bash
# 开放 5001 端口
sudo ufw allow 5001/tcp

# 或者使用 firewalld
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

---

## 系统要求

- **操作系统**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- **Python**: 3.7+
- **内存**: 最少 512MB，推荐 1GB+
- **磁盘**: 最少 1GB 可用空间
- **网络**: 需要开放 5001 端口（或配置 Nginx 使用 80/443）

---

## 联系方式

如有问题，请联系系统管理员。
