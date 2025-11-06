#!/bin/bash
# 生产环境启动脚本

set -e

# 等待数据库和Redis就绪 (如果配置了)
if [ ! -z "$DATABASE_URL" ]; then
    echo "等待数据库连接..."
    while ! nc -z ${DATABASE_HOST:-localhost} ${DATABASE_PORT:-5432}; do
        echo "数据库未就绪，等待1秒..."
        sleep 1
    done
    echo "数据库连接成功"
fi

if [ ! -z "$REDIS_URL" ]; then
    echo "等待Redis连接..."
    while ! nc -z ${REDIS_HOST:-localhost} ${REDIS_PORT:-6379}; do
        echo "Redis未就绪，等待1秒..."
        sleep 1
    done
    echo "Redis连接成功"
fi

# 检查环境变量
echo "检查环境配置..."
echo "ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "API_HOST: ${API_HOST:-0.0.0.0}"
echo "API_PORT: ${API_PORT:-8000}"

# 创建必要目录
mkdir -p /app/logs /app/models /app/data

# 设置权限
chown -R app:app /app/logs /app/models /app/data

# 启动应用
echo "启动应用..."
exec "$@"