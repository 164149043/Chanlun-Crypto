# Vercel 部署指南

本项目支持全栈部署到 Vercel，包括前端 React 应用和后端 FastAPI 服务。

## 架构说明

```
Chanlun-Crypto/
├── api/
│   └── index.py          # Vercel 入口点
├── web/                  # 前端 React + Vite
├── web_backend/          # 后端 FastAPI
├── vercel.json           # Vercel 配置
└── requirements.txt      # Python 依赖
```

## 部署步骤

### 1. 环境变量配置

在 Vercel 项目设置中添加以下环境变量：

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | https://platform.deepseek.com/ |
| `SILICONFLOW_API_KEY` | 硅基流动 API 密钥（可选） | https://cloud.siliconflow.cn/ |
| `PROXY_URL` | 代理 URL（可选） | 如 http://127.0.0.1:7890 |

**配置路径**: Vercel Dashboard → 项目 → Settings → Environment Variables

### 2. 导入项目

1. 登录 [Vercel](https://vercel.com)
2. 点击 "Add New Project"
3. 导入你的 GitHub 仓库
4. Vercel 会自动检测 `vercel.json` 配置

### 3. 部署

点击 "Deploy" 开始部署。首次部署可能需要几分钟。

## 注意事项

### SSE 流式输出

本项目使用 Server-Sent Events 进行 AI 分析的流式输出。Vercel Serverless Functions 支持流式响应，但需要注意：

- 函数执行时间限制：Hobby 计划最大 60 秒
- 如果 AI 分析超时，考虑升级到 Pro 计划

### API 路由

所有 `/api/*` 请求会被路由到 FastAPI 后端：

```
/api/symbols          → 获取支持的交易对
/api/kline/{symbol}   → 获取 K 线数据
/api/analyze/stream   → SSE 流式分析
```

### 前端路由

所有非 API 请求会被重写到 `index.html`，支持 SPA 路由。

## 本地测试

```bash
# 安装 Vercel CLI
npm i -g vercel

# 本地运行
vercel dev
```

## 故障排除

### 1. 函数超时

如果 AI 分析超时：
- 检查 AI API 是否响应正常
- 考虑减少分析内容或优化提示词
- 升级 Vercel 计划以获得更长的执行时间

### 2. 环境变量未生效

确保环境变量已正确添加到 Vercel 项目设置中，并重新部署。

### 3. API 路由 404

检查 `vercel.json` 中的 `rewrites` 配置是否正确。

## 配置文件说明

### vercel.json

```json
{
  "buildCommand": "cd web && npm install && npm run build",
  "outputDirectory": "web/dist",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" },
    { "source": "/((?!api/).*)", "destination": "/index.html" }
  ]
}
```

### api/index.py

Vercel 入口点，导出 FastAPI 应用：

```python
from web_backend.main import app
handler = app
```
