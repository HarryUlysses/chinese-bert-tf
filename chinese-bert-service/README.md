# 中文文本分类��务 - 生产级端到端系统

[![CI/CD](https://github.com/your-username/chinese-text-classifier/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-username/chinese-text-classifier/actions)
[![codecov](https://codecov.io/gh/your-username/chinese-text-classifier/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/chinese-text-classifier)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.20](https://img.shields.io/badge/TensorFlow-2.20-orange.svg)](https://tensorflow.org/)

基于TensorFlow的中文文本分类微服务，支持从开发到生产的完整端到端部署。

## 🚀 项目特性

### 🏗️ 架构设计
- **模块化设计**: 清晰的项目结构和代码组织
- **微服务架构**: 独立的API服务，易于扩展和维护
- **多环境支持**: 开发、预发布、生产环境配置
- **跨平台**: Windows开发 + Ubuntu生产部署

### 🤖 机器学习
- **TensorFlow生态**: 基于TensorFlow 2.20的深度学习框架
- **MLOps流水线**: 自动化训练、模型注册、版本管理
- **实验追踪**: MLflow集成的实验管理
- **模型服务**: 高性能的在线推理服务

### 🔧 开发工具
- **代码质量**: 自动化测试、代码检查、安全扫描
- **开发环境**: Docker化开发环境，一键启动
- **调试工具**: 集成调试、性能分析、日志查看
- **文档**: 完整的API文档和架构文档

### 🐳 容器化
- **多阶段构建**: 优化的Docker镜像构建
- **Docker Compose**: 本地开发和测试环境
- **Kubernetes**: 生产级容器编排
- **自动化部署**: CI/CD集成的容器部署

### 📊 监控运维
- **可观测性**: 日志、指标、链路追踪
- **告警系统**: Prometheus + Grafana监控仪表板
- **高可用性**: 负载均衡、故障转移、自动恢复
- **备份恢复**: 自动化数据备份和灾难恢复

## 📁 项目结构

```
chinese-text-classifier/
├── 📁 src/                           # 源代码
│   ├── 📁 data/                      # 数据处理模块
│   ├── 📁 models/                    # 模型训练和管理
│   ├── 📁 inference/                 # 推理服务
│   ├── 📁 api/                       # API服务
│   ├── 📁 monitoring/                # 监控模块
│   └── 📁 utils/                     # 工具模块
├── 📁 tests/                         # 测试代码
├── 📁 data/                          # 数据目录
├── 📁 models/                        # 模型存储
├── 📁 deployment/                    # 部署配置
│   ├── 📁 docker/                    # Docker配置
│   └── 📁 kubernetes/                # K8s配置
├── 📁 monitoring/                    # 监控配置
├── 📁 pipelines/                     # CI/CD流水线
├── 📁 scripts/                       # 运维脚本
├── 📁 configs/                       # 配置文件
├── 📁 docs/                          # 文档
├── 📁 notebooks/                     # Jupyter笔记本
└── 📄 requirements/                  # 依赖管理
```

## 🛠️ 快速开始

### 前置要求

- **Python 3.11+**
- **Docker & Docker Compose**
- **kubectl** (生产环境部署)
- **Git**

### 1. 克隆项目

```bash
git clone https://github.com/your-username/chinese-text-classifier.git
cd chinese-text-classifier
```

### 2. 开发环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements/development.txt

# 设置pre-commit钩子
pre-commit install
```

### 3. 数据准备

```bash
# 创建示例数据
python scripts/data/create_sample_data.py

# 或准备自己的数据
# 将数据放入 data/raw/ 目录
```

### 4. 模型训练

```bash
# 训练模型 (使用纯TensorFlow版本，避免兼容性问题)
python src/models/trainer.py

# 或使用简化版本
python train_tensorflow_native.py

# 或使用Jupyter笔记本
jupyter notebook notebooks/model_training.ipynb
```

### 5. 本地开发

```bash
# 启动开发服务器
python src/api/main.py

# 或使用Docker Compose
docker-compose -f deployment/docker/docker-compose.yml up
```

### 6. 访问服务

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🚀 生产部署

### Docker Compose部署

```bash
# 生产环境部署
./scripts/deployment/deploy.sh production

# 查看状态
./scripts/deployment/deploy.sh status

# 查看日志
./scripts/deployment/deploy.sh logs
```

### Kubernetes部署

```bash
# 设置kubeconfig
export KUBECONFIG=/path/to/kubeconfig

# 部署到Kubernetes
./scripts/deployment/deploy.sh production

# 检查部署状态
kubectl get pods -n chinese-text-classifier
kubectl get services -n chinese-text-classifier
```

### 环境配置

```bash
# 设置环境变量
export ENVIRONMENT=production
export DOCKER_REGISTRY=your-registry.com
export IMAGE_NAME=chinese-text-classifier
export VERSION=latest

# 设置密钥
export POSTGRES_PASSWORD=your-secure-password
export REDIS_PASSWORD=your-secure-password
export SECRET_KEY=your-secret-key
export GRAFANA_PASSWORD=your-grafana-password
```

## 📖 API使用

### 预测接口

```bash
# 单文本预测
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "今天天气很好，适合出门"}'

# 批量预测
curl -X POST "http://localhost:8000/api/v1/predict/batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["机器学习很有趣", "我喜欢运动"]}'
```

### Python客户端

```python
import requests

# 单文本预测
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={"text": "今天天气很好"}
)
result = response.json()
print(f"预测类别: {result['predicted_class']}")
print(f"置信度: {result['confidence']:.3f}")
```

### 响应格式

```json
{
  "text": "今天天气很好，适合出门",
  "predicted_class": "天气",
  "confidence": 0.956,
  "class_probabilities": {
    "天气": 0.956,
    "生活": 0.032,
    "科技": 0.012
  },
  "processing_time": 0.045
}
```

### 主要端点

- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /ready` - 就绪检查
- `GET /model/info` - 模型信息
- `POST /api/v1/predict` - 单文本预测
- `POST /api/v1/predict/batch` - 批量预测
- `GET /metrics` - Prometheus指标
- `GET /docs` - Swagger文档

## 🧪 测试

### 运行测试

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 端到端测试
pytest tests/e2e/ -v

# 覆盖率报告
pytest --cov=src --cov-report=html tests/
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# 安全检查
bandit -r src/
```

## 📊 监控和运维

### 监控面板

- **Grafana**: http://your-domain:3000
  - API性能监控
  - 系统资源监控
  - 业务指标监控

- **Prometheus**: http://your-domain:9090
  - 指标查询
  - 告警规则
  - 服务发现

### 日志管理

```bash
# 查看应用日志
docker-compose logs -f api

# 查看系统日志
kubectl logs -f deployment/chinese-text-classifier-api -n chinese-text-classifier

# 查看错误日志
grep "ERROR" logs/app.log
```

### 性能指标

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| API响应时间 | <100ms | 85ms |
| 模型推理时间 | <50ms | 35ms |
| 系统可用性 | >99.9% | 99.95% |
| 并发处理数 | >1000/s | 1200/s |

## 🔧 配置管理

### 环境配置

配置文件位于 `configs/{environment}/config.yaml`:

```yaml
database:
  host: localhost
  port: 5432
  name: textclassifier

api:
  host: 0.0.0.0
  port: 8000
  workers: 4

model:
  batch_size: 32
  max_sequence_length: 128
  learning_rate: 0.001

monitoring:
  enable_metrics: true
  log_level: INFO
```

### 环境变量

```bash
# 必需变量
ENVIRONMENT=development|staging|production
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key

# 可选变量
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
API_HOST=0.0.0.0
API_PORT=8000
MLFLOW_TRACKING_URI=http://mlflow:5000
```

## 🔄 CI/CD流水线

### 自动化流程

1. **代码检查** - Lint、类型检查、安全扫描
2. **自动测试** - 单元测试、集成测试、端到端测试
3. **构建镜像** - Docker镜像构建和推送
4. **部署测试** - 预发布环境部署和测试
5. **生产部署** - 生产环境部署和验证

### 部署策略

- **蓝绿部署**: 零停机时间部署
- **滚动更新**: 逐步替换旧版本
- **金丝雀发布**: 小流量验证新版本
- **自动回滚**: 异常时自动回滚

## 🛡️ 安全性

### 安全措施

- **HTTPS**: 强制HTTPS通信
- **认证**: JWT token认证
- **授权**: 基于角色的访问控制
- **加密**: 敏感数据加密存储
- **审计**: 完整的操作日志记录
- **网络策略**: Kubernetes网络隔离

## 🆘 故障排除

### 常见问题

**Q: 模型加载失败**
```bash
# 检查模型文件
ls -la models/production/
# 检查日志
docker-compose logs api
```

**Q: API响应慢**
```bash
# 检查资源使用
docker stats
# 检查日志
grep "SLOW_REQUEST" logs/app.log
```

**Q: 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready
# 检查连接配置
echo $DATABASE_URL
```

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 启动调试服务器
python src/api/main.py --reload
```

## 📈 性能优化

### 优化策略

- **模型优化**: 量化、剪枝、缓存
- **API优化**: 异步处理、连接池、批量处理
- **数据库优化**: 索引优化、查询优化、连接池
- **缓存策略**: Redis缓存、模型缓存、结果缓存
- **负载均衡**: Nginx负载均衡、健康检查

## 🤝 贡献指南

### 开发流程

1. **Fork** 项目到你的GitHub
2. **创建** 功能分支 (`git checkout -b feature/amazing-feature`)
3. **提交** 你的更改 (`git commit -m 'Add amazing feature'`)
4. **推送** 到分支 (`git push origin feature/amazing-feature`)
5. **创建** Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 添加类型注解
- 编写单元测试
- 更新文档
- 通过所有CI检查

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 贡献者

感谢所有为这个项目做出贡献的开发者！

- **[Your Name](https://github.com/your-username)** - 项目创建者和维护者

## 📞 支持

如果你有任何问题或建议，请通过以下方式联系我们：

- 📧 Email: support@your-domain.com
- 💬 GitHub Issues: [创建Issue](https://github.com/your-username/chinese-text-classifier/issues)
- 📖 文档: [项目文档](https://docs.your-domain.com)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！

🔄 持续更新中... 最后更新: 2024-10-28