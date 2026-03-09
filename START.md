# Chan.py Bento Grid Web 前端

## 快速启动

### 后端

```bash
cd web_backend
pip install fastapi uvicorn httpx
python main.py
# 或者
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/api/symbols 查看交易对列表

### 前端

```bash
cd web
npm run dev
```

前端将运行在 http://localhost:5173

## 功能

- **K 线图**: 使用 lightweight-charts，实时数据展示
- **三委员 + 裁决官机制**: 宻整实现了 AI 分析的流式输出
- **打字机效果**: 逐字显示，带光标闪烁动画
- **SSE 流式传输**: 实时显示 AI 分析进度
