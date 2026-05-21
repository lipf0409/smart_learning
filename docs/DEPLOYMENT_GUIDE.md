# 智能学习系统部署文档

## 目录

1. [环境准备](#环境准备)
2. [本地开发部署](#本地开发部署)
3. [Docker容器化部署](#docker容器化部署)
4. [阿里云服务器部署](#阿里云服务器部署)
5. [生产环境配置](#生产环境配置)
6. [常见问题](#常见问题)

---

## 环境准备

### 服务器要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 硬盘 | 40GB | 100GB+ SSD |
| 带宽 | 1Mbps | 5Mbps+ |

### 软件环境

| 软件 | 版本 | 用途 |
|------|------|------|
| Docker | 24.0+ | 容器运行 |
| Docker Compose | 2.0+ | 容器编排 |
| Git | 2.0+ | 代码管理 |

---

## 本地开发部署

### 1. 克隆项目

```bash
git clone <项目地址>
cd smart_learning
```

### 2. 数据库配置

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE smart_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户（可选）
CREATE USER 'smartlearning'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smart_learning.* TO 'smartlearning'@'%';
FLUSH PRIVILEGES;
```

### 3. 后端服务启动

```bash
cd backend

# 修改配置
vim src/main/resources/application.yml
# 修改数据库连接信息

# 启动服务
mvn spring-boot:run
```

### 4. AI服务启动

```bash
cd ai-service

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env
# 填写讯飞星火API配置

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 前端服务启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

---

## Docker容器化部署

### 1. 项目根目录创建 Docker Compose 配置

在项目根目录创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: smartlearning-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-SmartLearning@2024}
      MYSQL_DATABASE: smart_learning
      MYSQL_CHARACTER_SET_SERVER: utf8mb4
      MYSQL_COLLATION_SERVER: utf8mb4_unicode_ci
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./docker/mysql/init:/docker-entrypoint-initdb.d
    command: --default-authentication-plugin=mysql_native_password
    networks:
      - smartlearning-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: smartlearning-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - smartlearning-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: smartlearning-backend
    restart: always
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/smart_learning?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
      SPRING_DATASOURCE_USERNAME: root
      SPRING_DATASOURCE_PASSWORD: ${MYSQL_ROOT_PASSWORD:-SmartLearning@2024}
      AI_SERVICE_URL: http://ai-service:8000
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - smartlearning-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # AI服务
  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    container_name: smartlearning-ai
    restart: always
    environment:
      SPARK_APP_ID: ${SPARK_APP_ID}
      SPARK_API_KEY: ${SPARK_API_KEY}
      SPARK_API_SECRET: ${SPARK_API_SECRET}
      SPARK_MODEL_VERSION: ${SPARK_MODEL_VERSION:-v3.5}
      DATABASE_URL: mysql+aiomysql://root:${MYSQL_ROOT_PASSWORD:-SmartLearning@2024}@mysql:3306/smart_learning
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    volumes:
      - ./ai-service/weights:/app/weights
      - ./ai-service/pose_landmarker.task:/app/pose_landmarker.task
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - smartlearning-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 前端服务 (Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: smartlearning-frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - ai-service
    networks:
      - smartlearning-network

networks:
  smartlearning-network:
    driver: bridge

volumes:
  mysql_data:
  redis_data:
```

### 2. 创建环境变量文件

在项目根目录创建 `.env`:

```env
# MySQL配置
MYSQL_ROOT_PASSWORD=SmartLearning@2024

# 讯飞星火API配置
SPARK_APP_ID=你的APPID
SPARK_API_KEY=你的APIKey
SPARK_API_SECRET=你的APISecret
SPARK_MODEL_VERSION=v3.5
```

### 3. 创建各服务 Dockerfile

#### 后端 Dockerfile (`backend/Dockerfile`)

```dockerfile
# 构建阶段
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

# 运行阶段
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
RUN apk add --no-cache curl
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "-Xms256m", "-Xmx512m", "app.jar"]
```

#### AI服务 Dockerfile (`ai-service/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端 Dockerfile (`frontend/Dockerfile`)

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Nginx 配置 (`docker/nginx/nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log  /var/log/nginx/error.log warn;

    sendfile        on;
    keepalive_timeout  65;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 上传文件大小限制
    client_max_body_size 20M;

    upstream backend {
        server backend:8080;
    }

    upstream ai_service {
        server ai-service:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # 后端API代理
        location /api/auth/ {
            proxy_pass http://backend/api/auth/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/admin/ {
            proxy_pass http://backend/api/admin/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # AI服务API代理
        location /api/posture/ {
            proxy_pass http://ai_service/api/posture/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        location /api/question/ {
            proxy_pass http://ai_service/api/question/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/learning/ {
            proxy_pass http://ai_service/api/learning/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/rag/ {
            proxy_pass http://ai_service/api/rag/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # HTTPS配置（生产环境启用）
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # 其他location配置同上
    # }
}
```

### 5. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 阿里云服务器部署

### 1. 服务器准备

```bash
# 连接服务器
ssh root@your-server-ip

# 更新系统
yum update -y  # CentOS
# 或
apt update && apt upgrade -y  # Ubuntu

# 安装Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
systemctl start docker
systemctl enable docker

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 安装Git
yum install git -y  # CentOS
# 或
apt install git -y  # Ubuntu
```

### 2. 配置阿里云镜像加速

```bash
# 编辑Docker配置
mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://mirror.ccs.tencentyun.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 重启Docker
systemctl daemon-reload
systemctl restart docker
```

### 3. 配置防火墙

```bash
# 开放端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload

# 或使用iptables
iptables -I INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
service iptables save
```

### 4. 阿里云安全组配置

在阿里云控制台配置安全组规则：

| 端口 | 协议 | 授权对象 | 说明 |
|------|------|----------|------|
| 22 | TCP | 0.0.0.0/0 | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |
| 3306 | TCP | 内网IP | MySQL |
| 6379 | TCP | 内网IP | Redis |

### 5. 部署项目

```bash
# 创建项目目录
mkdir -p /opt/smart_learning
cd /opt/smart_learning

# 克隆代码
git clone <项目地址> .

# 创建环境变量文件
cat > .env << EOF
MYSQL_ROOT_PASSWORD=你的强密码
SPARK_APP_ID=你的APPID
SPARK_API_KEY=你的APIKey
SPARK_API_SECRET=你的APISecret
SPARK_MODEL_VERSION=v3.5
EOF

# 创建必要目录
mkdir -p docker/nginx/ssl
mkdir -p docker/mysql/init

# 启动服务
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f
```

### 6. 配置域名和SSL（可选）

```bash
# 安装certbot
yum install certbot -y

# 申请证书
certbot certonly --webroot -w /usr/share/nginx/html -d your-domain.com

# 复制证书到Nginx目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem

# 修改nginx.conf启用HTTPS
# 重启服务
docker-compose restart frontend
```

---

## 生产环境配置

### 1. 数据库优化

```sql
-- MySQL配置优化 (my.cnf)
[mysqld]
# 缓冲池大小（物理内存的50-70%）
innodb_buffer_pool_size = 2G

# 日志配置
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M

# 连接配置
max_connections = 500
wait_timeout = 600

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

### 2. JVM参数优化

```bash
# 后端服务JVM参数
JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### 3. Redis配置

```bash
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 4. 定时备份

```bash
# 创建备份脚本
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/opt/backups
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份MySQL
docker exec smartlearning-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} smart_learning > $BACKUP_DIR/db_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/db_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# 添加定时任务
crontab -e
# 每天凌晨2点备份
0 2 * * * /opt/backup.sh
```

---

## 常见问题

### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose logs backend

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose up -d --build --force-recreate
```

### 2. 数据库连接失败

```bash
# 检查MySQL容器状态
docker exec -it smartlearning-mysql mysql -u root -p

# 检查网络连接
docker network inspect smartlearning-network
```

### 3. AI服务无法启动

```bash
# 检查环境变量
docker exec smartlearning-ai env | grep SPARK

# 检查模型文件
docker exec smartlearning-ai ls -la /app/weights/
```

### 4. 前端无法访问后端

```bash
# 检查Nginx配置
docker exec smartlearning-frontend nginx -t

# 检查后端健康状态
curl http://localhost:8080/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"ll","password":"040920Lp.."}'
```

### 5. WebSocket连接失败

确保Nginx配置了WebSocket代理：
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_read_timeout 86400;
```

---

## 运维命令速查

```bash
# 查看所有容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启单个服务
docker-compose restart backend

# 进入容器
docker exec -it smartlearning-backend /bin/sh

# 查看资源使用
docker stats

# 清理无用镜像
docker image prune -a

# 备份数据卷
docker run --rm -v smart_learning_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup.tar.gz /data
```

---

## 联系支持

如遇到问题，请查看：
- 项目文档: `docs/TECHNICAL_DOCUMENTATION.md`
- AI服务配置: `ai-service/CONFIG.md`
- 日志文件: `/var/log/docker/`
