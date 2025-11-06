# 多阶段构建的生产级Dockerfile - Python 3.12优化版
FROM python:3.12-slim as base

# 设置标签
LABEL maintainer="chinese-text-classifier-team" \
      version="2.0.0" \
      description="Chinese Text Classification API with Python 3.12" \
      python.version="3.12"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60 \
    PYTHONHASHSEED=random \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖（优化版本）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    wget \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoclean

# 升级pip到最新版本以支持Python 3.12优化
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 创建应用用户（安全优化）
RUN groupadd -r appuser && \
    useradd -r -g appuser --home-dir /app --shell /bin/bash appuser

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt requirements/
COPY requirements/ requirements/
# 如果存在requirements目录

# 安装Python依赖（Python 3.12优化）
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel && \
    pip install --no-cache-dir -r requirements/production.txt

# 开发阶段
FROM base as development
# 安装开发依赖
RUN pip install --no-cache-dir -r requirements/development.txt

# 生产阶段
FROM base as production

# 设置生产环境变量
ENV ENVIRONMENT=production \
    TENSORFLOW_INTER_OP_PARALLELISM_THREADS=4 \
    TENSORFLOW_INTRA_OP_PARALLELISM_THREADS=4 \
    CUDA_VISIBLE_DEVICES=-1 \
    TF_ENABLE_ONEDNN_OPTS=1

# 复制应用代码
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser deployment/docker/entrypoint.sh deployment/docker/
COPY --chown=appuser:appuser serve.py ./

# 创建必要目录并设置权限
RUN mkdir -p logs models data tmp && \
    chmod 755 /app && \
    chmod +x deployment/docker/entrypoint.sh && \
    chown -R appuser:appuser /app

# 切换到应用用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查（优化版）
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# 设置入口点
ENTRYPOINT ["deployment/docker/entrypoint.sh"]

# 启动命令（生产优化）
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]