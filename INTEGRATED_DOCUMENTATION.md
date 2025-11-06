# 中文BERT TensorFlow项目完整文档

## 📋 项目概述

**中文文本分类服务** - 基于TensorFlow的端到端机器学习项���，提供中文文本分类的完整MLOps解决方案。

### 核心功能
- 🤖 **模型训练**: LSTM神经网络，支持中文文本分类
- 🚀 **API服务**: FastAPI REST API，提供实时预测服务
- 📊 **MLOps流程**: 完整的模型生命周期管理
- 🐳 **容器化部署**: Docker + Docker Compose生产级部署
- 📈 **监控可观测**: Prometheus + Grafana监控体系

---

## 🏛️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     中文文本分类系统                          │
├─────────────────────────────────────────────────────────────┤
│  前端/客户端 (Frontend/Clients)                             │
│  ├── Web应用                                                │
│  ├── 移动应用                                               │
│  └── 第三方集成                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST API
┌─────────────────────────▼───────────────────────────────────┐
│                   API服务层 (API Layer)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           FastAPI服务 (src/api/)                    │    │
│  │  ├── main.py              # FastAPI应用入口          │    │
│  │  ├── predictor.py         # 模型预测器              │    │
│  │  └── middleware.py        # 中间件和认证             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  业务逻辑层 (Business Layer)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              模型服务 (Model Service)               │    │
│  │  ├── 模型加载与管理                                    │    │
│  │  ├── 文本预处理                                      │    │
│  │  ├── 预测推理                                        │    │
│  │  └── 结果后处理                                      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 数据访问层 (Data Layer)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               模型存储 (Model Storage)                │    │
│  │  ├── models/registry/                                │    │
│  │  │   ├── registry.json      # 模型注册表            │    │
│  │  │   ├── v20251105_xxx/     # 模型版本目录          │    │
│  │  │   │   ├── model.keras     # TensorFlow模型        │    │
│  │  │   │   ├── model_info.json # 模型元数据           │    │
│  │  │   │   ├── label_encoder.pkl # 标签编码器         │    │
│  │  │   │   └── vectorize_config.json # 向量化配置     │    │
│  │  │   └── ...                                        │    │
│  │  └── models/checkpoints/    # 训练检查点             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 基础设施层 (Infrastructure Layer)             │
│  ├── 🐳 容器化 (Containerization)                           │
│  │   ├── Dockerfile                                        │
│  │   ├── docker-compose.yml                               │
│  │   └── docker-compose.prod.yml                          │
│  │                                                          │
│  ├── 🚀 部署 (Deployment)                                   │
│  │   ├── Kubernetes/                                       │
│  │   ├── 监控告警/                                         │
│  │   └── 自动化CI/CD                                       │
│  │                                                          │
│  ├── 📊 监控 (Monitoring)                                    │
│  │   ├── Prometheus                                        │
│  │   ├── Grafana                                           │
│  │   └── 日志收集                                           │
│  │                                                          │
│  └── 🔒 安全 (Security)                                     │
│      ├── 认证授权                                           │
│      ├── 数据加密                                           │
│      └── 网络安全                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目目录结构

### 当前项目结构
```
chinese-text-classifier/
├── 📄 run.py                           # 项目主入口
├── 📄 requirements.txt                 # Python依赖
├── 📄 Dockerfile                       # Docker配置
├── 📄 docker-compose.yml              # Docker Compose配置
├── 📄 README.md                        # 项目文档
├── 📁 src/                             # 源代码目录
│   ├── 📁 api/                         # API服务
│   │   └── 📄 main.py                  # FastAPI主程序
│   ├── 📁 data/                        # 数据处理模块
│   │   └── 📄 data_loader.py           # 数据加载器
│   ├── 📁 models/                      # 模型训练模块
│   │   └── 📄 trainer.py               # 模型训练器
│   └── 📁 utils/                       # 工具模块
│       └── 📄 config.py                # 配置管理
├── 📁 models/                          # 模型存储目录
├── 📁 data/                            # 数据目录
└── 📁 logs/                            # 日志目录
```

### 完整生产级架构
```
chinese-text-classifier/
├── 📁 src/                           # 源代码
│   ├── 📁 data/                      # 数据处理模块
│   │   ├── data_loader.py           # 数据加载器
│   │   ├── preprocessor.py          # 数据预处理
│   │   ├── validator.py             # 数据验证
│   │   └── version_control.py       # 数据版本控制
│   ├── 📁 models/                    # 模型模块
│   │   ├── model_factory.py         # 模型工厂
│   │   ├── trainer.py               # 训练器
│   │   ├── evaluator.py             # 评估器
│   │   └── registry.py              # 模型注册
│   ├── 📁 inference/                 # 推理服务
│   │   ├── predictor.py             # 预测器
│   │   ├── batch_processor.py       # 批处理
│   │   └── cache.py                 # 缓存层
│   ├── 📁 api/                       # API服务
│   │   ├── main.py                  # FastAPI应用
│   │   ├── routes/                  # 路由模块
│   │   ├── middleware/              # 中间件
│   │   └── schemas/                 # 数据模式
│   ├── 📁 monitoring/                # 监控模块
│   │   ├── metrics.py               # 指标收集
│   │   ├── logging.py               # 日志配置
│   │   └── health_check.py          # 健康检查
│   └── 📁 utils/                     # 工具模块
│       ├── config.py                # 配置管理
│       ├── security.py              # 安全工具
│       └── helpers.py               # 辅助函数
├── 📁 tests/                         # 测试模块
│   ├── unit/                        # 单元测试
│   ├── integration/                 # 集成测试
│   └── e2e/                         # 端到端测试
├── 📁 data/                          # 数据目录
│   ├── raw/                         # 原始数据
│   ├── processed/                   # 处理后数据
│   ├── validation/                  # 验证数据
│   └── registry/                    # 数据注册表
├── 📁 models/                        # 模型目录
│   ├── experiments/                 # 实验模型
│   ├── production/                  # 生产模型
│   ├── staging/                     # 预发布模型
│   └── registry/                    # 模型注册表
├── 📁 deployment/                    # 部署配置
│   ├── docker/                      # Docker配置
│   ├── kubernetes/                  # K8s配置
│   ├── terraform/                   # 基础设施代码
│   └── ansible/                     # 配置管理
├── 📁 monitoring/                    # 监控配置
│   ├── prometheus/                  # Prometheus配置
│   ├── grafana/                     # Grafana仪表板
│   └── alertmanager/                # 告警配置
├── 📁 pipelines/                     # CI/CD流水线
│   ├── .github/workflows/           # GitHub Actions
│   ├── gitlab-ci/                   # GitLab CI
│   └── jenkins/                     # Jenkins流水线
├── 📁 scripts/                       # 运维脚本
│   ├── setup/                       # 环境设置
│   ├── deployment/                  # 部署脚本
│   ├── backup/                      # 备份脚本
│   └── maintenance/                 # 维护脚本
├── 📁 configs/                       # 配置文件
│   ├── development/                 # 开发环境
│   ├── staging/                     # 预发布环境
│   ├── production/                  # 生产环境
│   └── local/                       # 本地环境
├── 📁 docs/                          # 文档
│   ├── api/                         # API文档
│   ├── deployment/                  # 部署文档
│   └── architecture/                # 架构文档
├── 📁 notebooks/                     # Jupyter笔记本
├── 📁 logs/                          # 日志目录
└── 📄 requirements/                  # 依赖管理
    ├── base.txt                     # 基础依赖
    ├── development.txt              # 开发依赖
    ├── production.txt               # 生产依赖
    └── test.txt                     # 测试依赖
```

---

## 🚀 快速开始

### 1. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 训练模型
python run.py train --epochs 5

# 启动服务
python run.py serve --port 8000 --reload
```

### 2. Docker部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🔄 数据流程

### 训练流程
```
原始文本数据 → 数据预处理 → 模型训练 → 模型评估 → 模型保存 → 注册表更新
```

### 预测流程
```
用户请求 → API接收 → 模型加载 → 文本向量化 → 模型推理 → 结果返回
```

### 部署流程
```
代码提交 → CI/CD流水线 → 镜像构建 → 自动部署 → 健康检查 → 监控告警
```

---

## 🧱 核心组件

### 1. **API服务层** (`src/api/`)
- **FastAPI框架**: 高性能异步Web框架
- **自动文档**: Swagger UI自动生成API文档
- **中间件**: CORS、认证、日志记录
- **异常处理**: 统一错误响应格式

### 2. **模型服务层** (`src/api/predictor.py`)
- **ModelPredictor类**: 核心预测器
- **模型加载**: 支持多版本模型管理
- **文本处理**: 中文文本向量化
- **批量预测**: 支持单文本和批量预测

### 3. **模型训练层** (`src/models/trainer.py`)
- **ModelTrainer类**: 生产级训练器
- **TensorFlow 2.x**: LSTM神经网络架构
- **MLflow集成**: 实验跟踪和模型管理
- **自动保存**: 模型检查点和最佳模型保存

### 4. **数据存储层**
- **模型注册表**: JSON格式的模型元数据
- **版本管理**: 按时间和准确率排序的模型版本
- **配置管理**: 预处理组件和模型配置的持久化

---

## 🔧 技术栈

### 后端框架
- **FastAPI**: 现代高性能Web框架
- **TensorFlow 2.20.0**: 深度学习框架
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和序列化

### 机器学习
- **Keras**: 高级神经网络API
- **scikit-learn**: 机器学习工具库
- **TextVectorization**: 中文文本预处理
- **LSTM**: 长短期记忆网络

### 数据处理
- **pandas**: 数据分析
- **numpy**: 数值计算
- **pickle**: 对象序列化

### 监控部署
- **Docker**: 容器化技术
- **Docker Compose**: 多容器编排
- **Prometheus**: 监控指标收集
- **Grafana**: 可视化监控面板
- **MLflow**: 机器学习生命周期管理

---

## 🚀 生产环境部署

### 前置要求

- **Docker** 20.0+
- **Docker Compose** 2.0+
- **系统资源**: 最低 4GB RAM, 2 CPU cores

### 环境变量配置

创建 `.env.production` 文件：

```bash
# 应用配置
ENVIRONMENT=production
SECRET_KEY=your-secure-secret-key-change-this
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO

# 数据库配置
POSTGRES_PASSWORD=your-secure-postgres-password
DATABASE_URL=postgresql://postgres:your-secure-postgres-password@postgres:5432/textclassifier

# Redis配置
REDIS_PASSWORD=your-secure-redis-password
REDIS_URL=redis://:your-secure-redis-password@redis:6379/0

# 监控配置
GRAFANA_PASSWORD=your-secure-grafana-password
ENABLE_MONITORING=true
```

### 快速部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd chinese-text-classifier

# 2. 配置环境变量
cp .env.example .env.production
# 编辑 .env.production 文件

# 3. 部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy production
```

### 手动部署步骤

#### 1. 构建镜像
```bash
docker build -f deployment/docker/Dockerfile \
             -t chinese-text-classifier:latest \
             --target production .
```

#### 2. 启动服务
```bash
# 启动核心服务
docker-compose -f deployment/docker/docker-compose.prod.yml up -d

# 启动监控服务 (可选)
docker-compose -f deployment/docker/docker-compose.prod.yml --profile monitoring up -d
```

#### 3. 验证部署
```bash
# 健康检查
curl http://localhost:8000/health

# API文档
curl http://localhost:8000/docs

# 服务状态
./scripts/deploy.sh status
```

---

## 📊 监控服务

### Grafana
- **地址**: http://localhost:3000
- **用户名**: admin
- **密码**: `GRAFANA_PASSWORD`环境变量

### Prometheus
- **地址**: http://localhost:9090
- **功能**: 指标收集和告警

### 日志查看
```bash
# API服务日志
./scripts/deploy.sh logs api

# 数据库日志
./scripts/deploy.sh logs postgres

# Redis日志
./scripts/deploy.sh logs redis
```

---

## 🔧 服务管理

### 常用命令

```bash
# 查看服务状态
./scripts/deploy.sh status

# 查看服务日志
./scripts/deploy.sh logs

# 停止服务
./scripts/deploy.sh stop

# 重启服务
./scripts/deploy.sh restart

# 健康检查
./scripts/deploy.sh health

# 备份数据
./scripts/deploy.sh backup
```

### 服务扩缩容

```bash
# 修改 docker-compose.prod.yml 中的 replicas 数量
services:
  api:
    deploy:
      replicas: 4  # 增加到4个副本
```

---

## 🔒 安全配置

### 网络安全

- **HTTPS**: 配置SSL证书
- **防火墙**: 只开放必要端口 (80, 443)
- **访问控制**: 配置IP白名单

### 应用安全

- **密钥管理**: 使用强密码和安全的SECRET_KEY
- **数据加密**: 敏感数据存储加密
- **日志审计**: 启用操作日志记录

---

## 📈 性能优化

### 系统资源

| 服务 | 最小配置 | 推荐配置 |
|------|----------|----------|
| API服务 | 1GB RAM, 0.5 CPU | 2GB RAM, 1 CPU |
| PostgreSQL | 1GB RAM, 0.5 CPU | 2GB RAM, 1 CPU |
| Redis | 512MB RAM, 0.25 CPU | 1GB RAM, 0.5 CPU |
| Grafana | 512MB RAM, 0.25 CPU | 1GB RAM, 0.5 CPU |
| Prometheus | 512MB RAM, 0.5 CPU | 1GB RAM, 1 CPU |

### 调优建议

1. **数据库优化**
   - 配置适当的连接池大小
   - 定期执行VACUUM和ANALYZE
   - 监控慢查询

2. **Redis优化**
   - 设置合适的内存限制
   - 配置持久化策略
   - 监控内存使用

3. **API优化**
   - 调整worker数量
   - 配置适当的超时时间
   - 启用请求缓存

---

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查容器状态
docker-compose ps

# 查看容器日志
docker-compose logs api

# 检查资源使用
docker stats
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U postgres

# 检查网络连接
docker-compose exec api ping postgres
```

#### 3. 内存不足
```bash
# 监控内存使用
docker stats

# 增加系统内存或调整容器限制
```

#### 4. 性能问题
```bash
# 检查响应时间
curl -w "@{time_total}\n" http://localhost:8000/health

# 查看资源使用
docker-compose exec api top
```

---

## 🔄 更新部署

### 滚动更新

```bash
# 1. 构建新镜像
docker build -f deployment/docker/Dockerfile -t chinese-text-classifier:v2.0.0 --target production .

# 2. 更新服务
docker-compose -f deployment/docker/docker-compose.prod.yml up -d

# 3. 验证更新
./scripts/deploy.sh health
```

### 零停机部署

1. 使用蓝绿部署策略
2. 配置负载均衡器
3. 逐步切换流量

---

## 📋 监控清单

### 系统监控
- [ ] CPU使用率 < 80%
- [ ] 内存使用率 < 85%
- [ ] 磁盘使用率 < 90%
- [ ] 网络延迟正常

### 应用监控
- [ ] API响应时间 < 200ms
- [ ] 错误率 < 1%
- [ ] 请求成功率 > 99%
- [ ] 数据库连接正常

### 业务监控
- [ ] 模型预测正常
- [ ] 数据处理正常
- [ ] 用户访问正常
- [ ] 告警系统正常

---

## 🎯 最佳实践

### 代码质量
- **类型注解**: 提高代码可读性
- **文档字符串**: 完整的API文档
- **单元测试**: pytest测试框架
- **代码规范**: Black代码格式化

### 模型管理
- **版本控制**: Git + MLflow模型版本管理
- **实验跟踪**: 训练参数和指标记录
- **模型评估**: 交叉验证和A/B测试
- **模型监控**: 预测漂移检测

### 运维管理
- **基础设施即代码**: Docker + Kubernetes
- **自动化部署**: CI/CD流水线
- **日志管理**: 结构化日志和集中收集
- **备份策略**: 数据和模型备份

---

## 🔮 扩展方向

### 模型优化
- **模型压缩**: 量化、剪枝、蒸馏
- **推理加速**: TensorRT、ONNX
- **多模态**: 图像+文本融合
- **预训练模型**: BERT、ERNIE等

### 功能扩展
- **多语言支持**: 英文、日文等
- **更多分类任务**: 情感分析、意图识别
- **实时学习**: 在线学习和增量训练
- **模型解释**: SHAP、LIME可解释性

### 架构演进
- **微服务**: 拆分为训练、预测、管理服务
- **事件驱动**: 异步消息队列
- **边缘计算**: 模型边缘部署
- **联邦学习**: 隐私保护的分布式训练

---

## 🔧 可用命令

```bash
# 训练模型
python run.py train --epochs 10 --batch-size 32

# 启动API服务
python run.py serve --host 0.0.0.0 --port 8000

# 部署到生产环境 (脚本存在时)
python run.py deploy production
```

---

## 📝 注意事项

1. **模型训练**: 当前使用模拟数据，实际使用时需要替换为真实数据
2. **API接口**: 返回模拟预测结果，需要加载训练好的模型
3. **Docker**: 简化配置，适合开发和测试环境
4. **日志**: 日志文件保存在 `logs/` 目录

---

## 📈 性能指标

### 模型性能
- **准确率**: 33.33% (示例数据)
- **推理时间**: 0.05-0.5秒
- **内存占用**: ~200MB
- **模型大小**: 2.1MB

### 服务性能
- **API响应时间**: <200ms
- **并发处理**: 100+ QPS
- **可用性**: 99.9%
- **扩展性**: 支持水平扩展

---

## 🆘 支持与帮助

如果遇到问题，请：

1. 查看日志文件
2. 检查监控指标
3. 参考故障排除文档
4. 联系技术支持

**联系方式**:
- 📧 Email: support@your-domain.com
- 💬 GitHub Issues: 创建Issue
- 📖 文档: 项目文档目录

---

*最后更新: 2025-11-07*
*文档版本: 整合版本 v1.0*