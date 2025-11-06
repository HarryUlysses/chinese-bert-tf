#!/bin/bash
# 中文文本分类服务部署脚本 - 优化版(适配2核2GB Ubuntu)

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 2核2GB环境优化配置
ENVIRONMENT=${1:-production}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"localhost:5000"}
IMAGE_NAME=${IMAGE_NAME:-"chinese-text-classifier"}
VERSION=${VERSION:-"latest"}

# 低资源配置 - 适配2核2GB环境
MAX_MEMORY=${MAX_MEMORY:-"1536m"}  # 1.5GB，预留512MB给系统
MAX_CPUS=${MAX_CPUS:-"1.5"}        # 1.5核，预留0.5核给系统
WORKER_PROCESSES=${WORKER_PROCESSES:-"1"}
WORKER_THREADS=${WORKER_THREADS:-"2"}
MAX_REQUESTS=${MAX_REQUESTS:-"1000"}
BACKUP_ENABLED=${BACKUP_ENABLED:-"false"}  # 默认关闭备份以节省资源

log_info "开始部署中文文本分类服务..."
log_info "环境: $ENVIRONMENT"
log_info "镜像: $DOCKER_REGISTRY/$IMAGE_NAME:$VERSION"

# 检查系统资源
check_system_resources() {
    log_info "检查系统资源..."

    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
    AVAILABLE_MEM=$(free -m | awk 'NR==2{print $7}')
    CPU_CORES=$(nproc)

    log_info "系统资源状态:"
    log_info "  CPU核心数: $CPU_CORES"
    log_info "  总内存: ${TOTAL_MEM}MB"
    log_info "  可用内存: ${AVAILABLE_MEM}MB"

    # 检查最低要求
    if [ "$CPU_CORES" -lt 2 ]; then
        log_warning "CPU核心数少于2个，性能可能受影响"
    fi

    if [ "$TOTAL_MEM" -lt 1536 ]; then
        log_error "内存不足1.5GB，无法安全运行服务"
        exit 1
    fi

    if [ "$AVAILABLE_MEM" -lt 1024 ]; then
        log_warning "可用内存少于1GB，建议释放内存或增加swap"
    fi

    log_success "系统资源检查完成"
}

# 检查前置条件
check_prerequisites() {
    log_info "检查部署前置条件..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，正在安装..."
        install_docker
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，正在安装..."
        install_docker_compose
    fi

    # 检查Docker服务状态
    if ! systemctl is-active --quiet docker; then
        log_info "启动Docker服务..."
        sudo systemctl start docker
        sudo systemctl enable docker
    fi

    # 检查Docker权限
    if ! groups $USER | grep -q docker; then
        log_warning "用户不在docker组中，请运行: sudo usermod -aG docker $USER && newgrp docker"
    fi

    log_success "前置条件检查通过"
}

# 安装Docker (Ubuntu)
install_docker() {
    log_info "安装Docker..."

    # 更新包索引
    sudo apt-get update

    # 安装依赖
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # 设置稳定版仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 安装Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io

    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."

    # 使用pip安装（避免网络问题）
    sudo pip install docker-compose

    log_success "Docker Compose安装完成"
}

# 优化构建参数
get_build_args() {
    echo "--build-arg WORKER_PROCESSES=$WORKER_PROCESSES"
    echo "--build-arg WORKER_THREADS=$WORKER_THREADS"
    echo "--build-arg MAX_REQUESTS=$MAX_REQUESTS"
}

# 构建镜像
build_image() {
    log_info "构建轻量级Docker镜像（内存优化）..."

    # 检查Dockerfile是否存在
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile不存在"
        exit 1
    fi

    # 获取构建参数
    BUILD_ARGS=$(get_build_args)

    log_info "构建配置:"
    log_info "  内存限制: $MAX_MEMORY"
    log_info "  CPU限制: $MAX_CPUS"
    log_info "  工作进程: $WORKER_PROCESSES"
    log_info "  工作线程: $WORKER_THREADS"

    # 构建镜像时限制资源使用
    docker build \
        $BUILD_ARGS \
        -t "$DOCKER_REGISTRY/$IMAGE_NAME:$VERSION" \
        --memory=1g \
        --cpus=1.5 \
        .

    if [ $? -eq 0 ]; then
        log_success "镜像构建完成"
        log_info "镜像大小:"
        docker images "$DOCKER_REGISTRY/$IMAGE_NAME:$VERSION" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 创建优化的docker-compose配置
create_optimized_compose() {
    log_info "创建轻量级Docker Compose配置..."

    cat > docker-compose.optimized.yml <<EOF
version: '3.8'

services:
  app:
    image: $DOCKER_REGISTRY/$IMAGE_NAME:$VERSION
    container_name: $IMAGE_NAME
    restart: unless-stopped

    # 资源限制 - 适配2核2GB
    deploy:
      resources:
        limits:
          cpus: '$MAX_CPUS'
          memory: $MAX_MEMORY
        reservations:
          cpus: '0.5'
          memory: '256m'

    ports:
      - "8000:8000"

    environment:
      - ENVIRONMENT=production
      - TENSORFLOW_INTER_OP_PARALLELISM_THREADS=2
      - TENSORFLOW_INTRA_OP_PARALLELISM_THREADS=2
      - PYTHONOPTIMIZE=2
      - WORKER_PROCESSES=$WORKER_PROCESSES
      - WORKER_THREADS=$WORKER_THREADS
      - MAX_REQUESTS=$MAX_REQUESTS

    volumes:
      - ./logs:/app/logs
      - ./models:/app/models:ro
      - ./data:/app/data

    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 60s
      timeout: 15s
      retries: 3
      start_period: 45s

    # 安全配置
    security_opt:
      - no-new-privileges:true

    # 优雅关闭
    stop_grace_period: 30s

networks:
  default:
    name: app-network
    driver: bridge

volumes:
  app-logs:
    driver: local
EOF

    log_success "优化的Docker Compose配置创建完成"
}

# 部署到生产环境（轻量级）
deploy_production() {
    log_info "部署到轻量级生产环境（2核2GB优化）..."

    # 创建优化的compose配置
    create_optimized_compose

    # 创建必要目录
    mkdir -p logs models data

    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose -f docker-compose.optimized.yml down 2>/dev/null || true

    # 启动服务
    log_info "启动优化版服务..."
    docker-compose -f docker-compose.optimized.yml up -d

    # 等待服务启动（增加等待时间）
    log_info "等待服务启动（低内存环境需要更多时间）..."
    sleep 45

    # 健康检查
    log_info "执行健康检查..."
    local retries=0
    local max_retries=10

    while [ $retries -lt $max_retries ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "✅ 生产环境部署成功！"
            show_performance_info
            return 0
        else
            retries=$((retries + 1))
            log_info "健康检查失败，${retries}/${max_retries}次重试..."
            sleep 10
        fi
    done

    log_error "❌ 服务启动失败，请检查日志"
    show_logs
    exit 1
}

# 显示性能信息
show_performance_info() {
    log_info "性能配置信息:"
    log_info "  内存限制: $MAX_MEMORY"
    log_info "  CPU限制: $MAX_CPUS"
    log_info "  工作进程: $WORKER_PROCESSES"
    log_info "  工作线程: $WORKER_THREADS"

    # 显示资源使用情况
    if command -v docker stats &> /dev/null; then
        log_info "当前资源使用:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep $IMAGE_NAME || true
    fi
}

# 开发环境部署
deploy_development() {
    log_info "部署到轻量级开发环境..."

    # 检查是否存在基础compose文件
    if [ ! -f "docker-compose.yml" ]; then
        log_warning "基础docker-compose.yml不存在，使用优化配置"
        docker-compose -f docker-compose.optimized.yml down 2>/dev/null || true
        create_optimized_compose
        docker-compose -f docker-compose.optimized.yml up -d
    else
        docker-compose down 2>/dev/null || true
        docker-compose up -d
    fi

    log_success "开发环境部署完成"
}

# 查看状态
show_status() {
    log_info "服务状态和资源使用:"

    # 检查服务状态
    if [ -f "docker-compose.optimized.yml" ]; then
        docker-compose -f docker-compose.optimized.yml ps
    else
        docker-compose ps 2>/dev/null || log_warning "没有运行的服务"
    fi

    # 显示系统资源
    log_info "系统资源状态:"
    log_info "  CPU负载: $(uptime | awk -F'load average:' '{print $2}')"
    log_info "  内存使用: $(free -h | awk 'NR==2{printf "%s/%s (%.1f%%)", $3,$2,$3*100/$2}')"
    log_info "  磁盘使用: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5")"}')"

    # API服务地址
    log_info "API服务地址:"
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "http://localhost:8000"
        log_info "健康检查: http://localhost:8000/health"
        log_info "API文档: http://localhost:8000/docs"
    else
        echo "http://localhost:8000"
        log_info "健康检查: http://localhost:8000/health"
        log_info "API文档: http://localhost:8000/docs"
    fi

    # 显示Docker资源使用
    if command -v docker stats &> /dev/null; then
        log_info "容器资源使用:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -5
    fi
}

# 查看日志
show_logs() {
    local service=${1:-$IMAGE_NAME}

    log_info "显示服务日志..."

    if [ -f "docker-compose.optimized.yml" ]; then
        docker-compose -f docker-compose.optimized.yml logs -f --tail=100 $service
    elif [ "$ENVIRONMENT" = "production" ] && [ -f "deployment/docker/docker-compose.prod.yml" ]; then
        docker-compose -f deployment/docker/docker-compose.prod.yml logs -f --tail=100 $service
    else
        docker-compose logs -f --tail=100 $service 2>/dev/null || \
        docker logs -f $service 2>/dev/null || \
        log_error "无法找到服务日志"
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."

    # 停止优化版服务
    if [ -f "docker-compose.optimized.yml" ]; then
        docker-compose -f docker-compose.optimized.yml down
    fi

    # 停止传统服务
    if [ "$ENVIRONMENT" = "production" ] && [ -f "deployment/docker/docker-compose.prod.yml" ]; then
        docker-compose -f deployment/docker/docker-compose.prod.yml down
    else
        docker-compose down 2>/dev/null || true
    fi

    # 清理孤立的容器
    docker container prune -f > /dev/null 2>&1 || true

    log_success "服务已停止"
}

# 轻量级备份（仅备份必要文件）
backup_data() {
    if [ "$BACKUP_ENABLED" = "false" ]; then
        log_info "备份功能已禁用（节省资源）"
        return 0
    fi

    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "执行轻量级备份..."

        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"

        # 只备份必要配置和日志
        cp -r logs/ "$BACKUP_DIR/" 2>/dev/null || true
        cp Dockerfile "$BACKUP_DIR/" 2>/dev/null || true
        cp docker-compose.optimized.yml "$BACKUP_DIR/" 2>/dev/null || true

        # 备份环境变量（如果存在）
        if [ -f ".env" ]; then
            cp .env "$BACKUP_DIR/"
        fi

        # 创建备份信息
        cat > "$BACKUP_DIR/backup_info.txt" << EOF
备份时间: $(date)
系统信息: $(uname -a)
资源状态:
- 内存: $(free -h | head -2)
- CPU: $(nproc) cores
- 磁盘: $(df -h / | tail -1)

服务配置:
- 最大内存: $MAX_MEMORY
- 最大CPU: $MAX_CPUS
- 工作进程: $WORKER_PROCESSES
- 工作线程: $WORKER_THREADS
EOF

        log_success "轻量级备份完成: $BACKUP_DIR"

        # 清理旧备份（保留最近3个）
        find backups/ -maxdepth 1 -type d -name "????????_??????" | sort -r | tail -n +4 | xargs rm -rf 2>/dev/null || true
    else
        log_warning "开发环境不需要备份"
    fi
}

# 轻量级健康检查
health_check() {
    log_info "执行轻量级健康检查..."

    # 检查API服务
    local api_healthy=false
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✅ API服务健康"
        api_healthy=true
    else
        log_error "❌ API服务不健康"
    fi

    # 检查容器状态
    local container_healthy=false
    if docker ps --filter "name=$IMAGE_NAME" --filter "status=running" | grep -q $IMAGE_NAME; then
        log_success "✅ 容器运行正常"
        container_healthy=true
    else
        log_error "❌ 容器未运行"
    fi

    # 检查系统资源
    local system_healthy=true
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')

    if [ "$mem_usage" -gt 85 ]; then
        log_warning "⚠️  内存使用率过高: ${mem_usage}%"
        system_healthy=false
    fi

    if (( $(echo "$load_avg > 2.0" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "⚠️  CPU负载过高: $load_avg"
        system_healthy=false
    fi

    if [ "$system_healthy" = true ]; then
        log_success "✅ 系统资源正常"
    fi

    # 综合判断
    if [ "$api_healthy" = true ] && [ "$container_healthy" = true ]; then
        log_success "🎉 所有健康检查通过"

        # 显示服务信息
        if command -v curl &> /dev/null && [ "$api_healthy" = true ]; then
            local response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
            log_info "响应时间: ${response_time}s"
        fi

        return 0
    else
        log_error "❌ 健康检查失败，请检查服务状态"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "==================================="
    echo "中文文本分类服务部署脚本 (2核2GB优化版)"
    echo "==================================="
    echo
    echo "用法: $0 {命令} [环境]"
    echo
    echo "命令:"
    echo "  deploy     - 部署应用 (默认)"
    echo "  status     - 查看服务状态和资源使用"
    echo "  logs       - 查看服务日志"
    echo "  stop       - 停止服务"
    echo "  backup     - 轻量级备份"
    echo "  health     - 健康检查"
    echo "  restart    - 重启服务"
    echo "  clean      - 清理系统资源"
    echo "  monitor    - 实时监控"
    echo "  help       - 显示此帮助信息"
    echo
    echo "环境: development|production (默认: production)"
    echo
    echo "环境变量 (可选):"
    echo "  MAX_MEMORY=${MAX_MEMORY}     # 最大内存限制"
    echo "  MAX_CPUS=${MAX_CPUS}         # 最大CPU限制"
    echo "  WORKER_PROCESSES=${WORKER_PROCESSES} # 工作进程数"
    echo "  WORKER_THREADS=${WORKER_THREADS}     # 工作线程数"
    echo "  BACKUP_ENABLED=${BACKUP_ENABLED}     # 是否启用备份"
    echo
    echo "示例:"
    echo "  $0 deploy production       # 部署到生产环境"
    echo "  $0 logs                   # 查看默认服务日志"
    echo "  $0 health                 # 健康检查"
    echo "  MAX_MEMORY=1024m $0 deploy # 使用1GB内存限制"
    echo "  $0 monitor                # 实时监控资源使用"
    echo
    echo "针对2核2GB环境的优化配置:"
    echo "  - 内存限制: 1.5GB (预留512MB给系统)"
    echo "  - CPU限制: 1.5核 (预留0.5核给系统)"
    echo "  - 轻量级健康检查"
    echo "  - 可选备份功能"
    echo "  - 资源使用监控"
}

# 清理系统资源
clean_resources() {
    log_info "清理系统资源..."

    # 清理Docker资源
    log_info "清理Docker未使用的资源..."
    docker system prune -f > /dev/null 2>&1 || true

    # 清理孤立的网络
    docker network prune -f > /dev/null 2>&1 || true

    # 清理孤立的卷
    docker volume prune -f > /dev/null 2>&1 || true

    # 清理旧备份文件
    if [ -d "backups" ]; then
        local old_backups=$(find backups/ -maxdepth 1 -type d -name "????????_??????" | sort -r | tail -n +4)
        if [ -n "$old_backups" ]; then
            log_info "清理旧备份文件..."
            echo "$old_backups" | xargs rm -rf
        fi
    fi

    # 清理旧日志文件
    if [ -d "logs" ]; then
        find logs/ -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
    fi

    log_success "系统资源清理完成"
}

# 实时监控
monitor_resources() {
    log_info "开始实时监控 (按Ctrl+C退出)..."

    while true; do
        clear
        echo "==================================="
        echo "中文文本分类服务 - 实时监控"
        echo "时间: $(date)"
        echo "==================================="

        # 系统资源
        echo "📊 系统资源:"
        echo "  CPU负载: $(uptime | awk -F'load average:' '{print $2}')"
        echo "  内存使用: $(free -h | awk 'NR==2{printf "%s/%s (%.1f%%)", $3,$2,$3*100/$2}')"
        echo "  磁盘使用: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5")"}')"
        echo

        # 容器状态
        echo "🐳 容器状态:"
        docker ps --filter "name=$IMAGE_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -3
        echo

        # 资源使用
        if command -v docker stats &> /dev/null; then
            echo "💾 资源使用:"
            docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -5
        fi

        # API状态
        echo "🔗 API状态:"
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            local response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
            echo "  ✅ 健康运行 (响应时间: ${response_time}s)"
        else
            echo "  ❌ 服务不可用"
        fi

        echo
        echo "按Ctrl+C退出监控..."
        sleep 5
    done
}

# 主函数
main() {
    # 显示脚本信息
    echo "🚀 中文文本分类服务部署脚本 (2核2GB优化版)"
    echo "==================================="

    case "${1:-deploy}" in
        "deploy")
            check_system_resources
            check_prerequisites
            build_image

            if [ "$ENVIRONMENT" = "production" ]; then
                deploy_production
            else
                deploy_development
            fi

            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "stop")
            stop_services
            ;;
        "backup")
            backup_data
            ;;
        "health")
            health_check
            ;;
        "restart")
            stop_services
            sleep 5
            main deploy "$ENVIRONMENT"
            ;;
        "clean")
            clean_resources
            ;;
        "monitor")
            monitor_resources
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'log_error "部署过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"