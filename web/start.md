# Chan.py Bento Grid Web 前端

## 快速启动指南

### 环境要求
- Python 3.8+
- Node.js 18+
- npm 或 yarn

### 安装依赖
```bash
# 后端
pip install -r web_backend/requirements.txt

# 前端
cd web && npm install
```

### 启动后端
```bash
cd web_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
访问 http://localhost:8000/docs 查看 API 文档

### 启动前端
```bash
cd web
npm run dev
```
访问 http://localhost:5173 查看前端页面

### 功能
- K线图展示 (BTC/USDT)
- 币种选择
- 开始分析按钮
- 三委员分析 + 裁决官结论
- 打字机效果输出
- 实时进度显示
