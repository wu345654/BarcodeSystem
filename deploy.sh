#!/bin/bash
# 条码系统 Linux 快速部署脚本

set -e

echo "========================================"
echo "条码系统 Linux 快速部署脚本"
echo "========================================"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 配置变量
APP_NAME="barcodesystem"
APP_DIR="/opt/BarcodeSystem"
APP_USER="www-data"
APP_PORT="5001"

# 安装依赖
echo "安装系统依赖..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx sqlite3

# 创建应用目录
echo "创建应用目录..."
mkdir -p $APP_DIR
mkdir -p /var/log/$APP_NAME

# 复制项目文件
echo "复制项目文件..."
cp -r . $APP_DIR/

# 设置权限
echo "设置权限..."
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /var/log/$APP_NAME
chmod -R 755 $APP_DIR

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 创建 systemd 服务文件
echo "创建 systemd 服务..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=Barcode System
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=$APP_DIR/venv/bin/gunicorn -b 127.0.0.1:$APP_PORT -w 4 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建 Nginx 配置
echo "配置 Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }
}
EOF

# 启用 Nginx 配置
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 启动服务
echo "启动服务..."
systemctl daemon-reload
systemctl start $APP_NAME
systemctl enable $APP_NAME
systemctl restart nginx

# 开放防火墙端口
echo "配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
fi

# 显示状态
echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "系统信息："
echo "  - 应用目录: $APP_DIR"
echo "  - 服务名称: $APP_NAME"
echo "  - 访问地址: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "常用命令："
echo "  - 查看状态: sudo systemctl status $APP_NAME"
echo "  - 重启服务: sudo systemctl restart $APP_NAME"
echo "  - 查看日志: sudo journalctl -u $APP_NAME -f"
echo "  - 停止服务: sudo systemctl stop $APP_NAME"
echo ""
echo "数据库备份："
echo "  sqlite3 $APP_DIR/order_system.db \".backup '$APP_DIR/order_system.db.backup'\""
echo ""
echo "========================================"
