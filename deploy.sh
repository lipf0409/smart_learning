#!/bin/bash

# 智能学习系统快速部署脚本
# 使用方法: ./deploy.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker未安装，请先安装Docker"
    fi
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose未安装，请先安装Docker Compose"
    fi
    success "Docker环境检查通过"
}

# 检查环境变量
check_env() {
    if [ ! -f .env ]; then
        warn ".env文件不存在，从模板创建..."
        cp .env.example .env
        error "请编辑.env文件配置讯飞星火API后重新运行"
    fi
    success "环境变量配置检查通过"
}

# 构建镜像
build() {
    info "开始构建Docker镜像..."
    docker-compose build --no-cache
    success "镜像构建完成"
}

# 启动服务
start() {
    info "启动服务..."
    docker-compose up -d
    success "服务启动完成"
    info "服务地址:"
    echo "  - 前端: http://localhost"
    echo "  - 后端: http://localhost:8080"
    echo "  - AI服务: http://localhost:8000"
}

# 停止服务
stop() {
    info "停止服务..."
    docker-compose down
    success "服务已停止"
}

# 重启服务
restart() {
    stop
    start
}

# 查看日志
logs() {
    docker-compose logs -f $1
}

# 查看状态
status() {
    info "服务状态:"
    docker-compose ps
}

# 清理
clean() {
    warn "这将删除所有容器、镜像和数据卷!"
    read -p "确认继续? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker-compose down -v --rmi all
        success "清理完成"
    else
        info "已取消"
    fi
}

# 备份数据库
backup() {
    BACKUP_DIR="./backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    mkdir -p $BACKUP_DIR

    info "备份数据库..."
    docker exec smartlearning-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} smart_learning > $BACKUP_DIR/db_$DATE.sql
    gzip $BACKUP_DIR/db_$DATE.sql
    success "备份完成: $BACKUP_DIR/db_$DATE.sql.gz"
}

# 更新服务
update() {
    info "拉取最新代码..."
    git pull

    info "重新构建并启动..."
    docker-compose up -d --build
    success "更新完成"
}

# 帮助信息
help() {
    echo "智能学习系统部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  check     检查环境"
    echo "  build     构建镜像"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志 (可选: 服务名)"
    echo "  status    查看状态"
    echo "  clean     清理所有数据"
    echo "  backup    备份数据库"
    echo "  update    更新服务"
    echo "  help      显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 start          # 启动所有服务"
    echo "  $0 logs backend   # 查看后端日志"
}

# 主函数
main() {
    case "$1" in
        check)
            check_docker
            check_env
            ;;
        build)
            check_docker
            build
            ;;
        start)
            check_docker
            check_env
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs $2
            ;;
        status)
            status
            ;;
        clean)
            clean
            ;;
        backup)
            backup
            ;;
        update)
            update
            ;;
        help|--help|-h|"")
            help
            ;;
        *)
            error "未知命令: $1"
            help
            ;;
    esac
}

main "$@"
