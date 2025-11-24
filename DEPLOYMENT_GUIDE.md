# TrendForge 部署指南

## 部署架构概览

TrendForge MVP采用现代化的自动化部署架构：

```
GitLab/GitHub → CI/CD Pipeline → Vercel/Cloudflare
     ↓                ↓              ↓
  代码托管      内容生成Pipeline    前端托管
```

## 1. 前端部署 - Vercel（推荐）

### 快速部署（5分钟）

1. **安装Vercel CLI**
```bash
npm i -g vercel
```

2. **在frontend目录执行部署**
```bash
cd /mnt/d/gitlab_deepwisdom/trendforge/frontend
vercel
```

3. **首次部署配置**
```
? Set up and deploy "~/trendforge/frontend"? [Y/n] Y
? Which scope do you want to deploy to? (选择你的账号)
? Link to existing project? [y/N] n
? What's your project's name? trendforge
? In which directory is your code located? ./
? Want to modify these settings? [y/N] n
```

4. **环境变量配置**（如需要）
```bash
vercel env add NEXT_PUBLIC_API_URL
# 输入后端API地址（如果有的话）
```

5. **生产环境部署**
```bash
vercel --prod
```

部署完成后，你会得到一个URL：`https://trendforge-xxx.vercel.app`

### Vercel项目配置（已准备好）

`frontend/vercel.json`已配置：
- 静态导出优化
- 安全响应头
- 路由重写规则

## 2. 后端Pipeline自动化部署

### GitLab CI部署（推荐）

1. **配置GitLab CI变量**

进入GitLab项目 → Settings → CI/CD → Variables，添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NEWS_API_KEY` | `你的API密钥` | News API密钥（可选） |
| `METAGPT_CONFIG` | `配置内容` | MetaGPT配置 |
| `GITLAB_TOKEN` | `你的Token` | GitLab访问令牌 |
| `NOTIFICATION_WEBHOOK` | `Webhook URL` | 成功通知地址 |
| `ALERT_WEBHOOK` | `Webhook URL` | 失败告警地址 |

2. **设置定时Pipeline**

进入 CI/CD → Schedules → New Schedule：
- Description: `Daily Content Generation`
- Interval Pattern: `0 6 * * *` (每天早上6点)
- Target Branch: `master`
- Variables: 可添加额外变量

3. **手动触发Pipeline**
```bash
# 使用GitLab CLI
glab ci run

# 或在GitLab网页
CI/CD → Pipelines → Run Pipeline
```

### GitHub Actions部署（备选）

1. **配置GitHub Secrets**

进入Settings → Secrets → Actions，添加：
```
NEWS_API_KEY
TAVILY_API_KEY
OPENAI_API_KEY
```

2. **启用Actions**

确保 `.github/workflows/daily-pipeline.yml` 已激活

3. **手动触发**

Actions → Daily Pipeline → Run workflow

## 3. 本地开发环境

### 前端开发服务器
```bash
cd frontend
npm run dev
# 访问 http://localhost:3001
```

### 后端Pipeline测试
```bash
cd backend
# Mock模式测试
python3 test_pipeline.py

# 真实模式（需要MetaGPT DR）
python3 pipeline.py full
```

## 4. Docker部署（可选）

### 创建Docker镜像
```bash
# 前端镜像
cd frontend
docker build -t trendforge-frontend .

# 运行容器
docker run -p 3001:3001 trendforge-frontend
```

### Docker Compose部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production

  pipeline:
    build: ./backend
    volumes:
      - ./content:/app/content
    environment:
      - METAGPT_CONFIG=/app/config/metagpt_config.yaml
```

## 5. 云服务器部署

### 阿里云/腾讯云ECS部署

1. **服务器准备**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装Python 3.10+
sudo apt install python3.10 python3-pip -y

# 安装nginx
sudo apt install nginx -y
```

2. **克隆项目**
```bash
git clone https://gitlab.com/your-username/trendforge.git
cd trendforge
```

3. **配置Nginx反向代理**
```nginx
# /etc/nginx/sites-available/trendforge
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

4. **使用PM2管理进程**
```bash
# 安装PM2
npm install -g pm2

# 启动前端
cd frontend
npm run build
pm2 start npm --name "trendforge-frontend" -- start

# 保存PM2配置
pm2 save
pm2 startup
```

## 6. CDN加速配置

### Cloudflare配置（推荐）

1. 添加网站到Cloudflare
2. 配置DNS指向你的服务器
3. 启用以下功能：
   - Auto Minify（JS/CSS/HTML）
   - Brotli压缩
   - HTTP/3 QUIC
   - 缓存级别：Standard
   - 浏览器缓存TTL：4小时

### 静态资源优化
```javascript
// next.config.js 添加CDN配置
module.exports = {
  images: {
    domains: ['cdn.your-domain.com'],
  },
  assetPrefix: process.env.NODE_ENV === 'production'
    ? 'https://cdn.your-domain.com'
    : '',
}
```

## 7. 监控与维护

### 健康检查脚本
```bash
# 运行健康检查
python3 scripts/health-check.py

# 设置定时检查（crontab）
*/5 * * * * /usr/bin/python3 /path/to/health-check.py
```

### 日志监控
```bash
# 查看前端日志
pm2 logs trendforge-frontend

# 查看Pipeline日志
tail -f backend/logs/pipeline.log
```

### 数据备份
```bash
# 备份生成的内容
tar -czf backup-$(date +%Y%m%d).tar.gz content/

# 定时备份（每天凌晨3点）
0 3 * * * tar -czf /backups/content-$(date +\%Y\%m\%d).tar.gz /path/to/content/
```

## 8. 故障排查

### 常见问题

**Q: 部署后页面显示404**
```bash
# 检查build输出
npm run build
# 确保out目录存在
ls -la out/
```

**Q: MetaGPT DR无法运行**
```bash
# 检查安装
pip show metagpt
# 重新安装
pip install git+ssh://git@gitlab.deepwisdomai.com/pub/MetaGPT.git@dr4run
```

**Q: Pipeline执行失败**
```bash
# 查看错误日志
cat backend/logs/error.log
# 测试配置
python3 backend/test_config.py
```

### 紧急回滚
```bash
# 使用回滚脚本
./scripts/rollback.sh

# 手动回滚
git revert HEAD
git push origin master
```

## 9. 成本优化建议

### 免费部署方案
- **前端**: Vercel免费层（100GB带宽/月）
- **Pipeline**: GitHub Actions（2000分钟/月）
- **存储**: GitHub仓库（免费）

### 低成本方案（~¥50/月）
- **前端**: Cloudflare Pages（无限带宽）
- **Pipeline**: 腾讯云函数（100万次/月免费）
- **存储**: OSS（40GB约¥9/月）

### 生产方案（~¥500/月）
- **前端**: 阿里云CDN + ECS
- **Pipeline**: 专用服务器运行
- **存储**: RDS + OSS
- **监控**: 云监控 + 日志服务

## 10. 快速部署检查清单

- [ ] 前端构建成功：`npm run build`
- [ ] 环境变量配置完成
- [ ] API密钥已设置
- [ ] Pipeline测试通过
- [ ] 域名DNS配置（如有）
- [ ] SSL证书配置（如有）
- [ ] 监控告警设置
- [ ] 备份策略确定

## 部署支持

遇到问题时：
1. 查看日志文件
2. 运行健康检查脚本
3. 检查环境变量配置
4. 确认网络连接正常

---

**祝贺！** 按照以上步骤，TrendForge将成功部署到生产环境。

推荐从Vercel免费部署开始，逐步迁移到更复杂的架构。