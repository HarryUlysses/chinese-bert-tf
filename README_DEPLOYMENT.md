# 生产部署指南

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

## 🔒 安全配置

### 网络安全

- **HTTPS**: 配置SSL证书
- **防火墙**: 只开放必要端口 (80, 443)
- **访问控制**: 配置IP白名单

### 应用安全

- **密钥管理**: 使用强密码和安全的SECRET_KEY
- **数据加密**: 敏感数据存储加密
- **日志审计**: 启用操作日志记录

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