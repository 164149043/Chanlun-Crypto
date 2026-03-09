# 缠论量化分析框架

基于缠论理论的加密货币量化分析工具，集成 AI 智能策略分析。

## 功能特性

### 缠论核心计算
- K线包含处理
- 分型识别
- 笔、线段计算
- 中枢识别
- 买卖点分析

### AI 策略引擎
- 多周期缠论数据自动采集（D1/H4/H1/M15）
- 接入 DeepSeek AI 进行策略分析
- **三委员 + 裁决官机制**：多角度独立分析，综合决策
- **温度参数控制**：每个委员/裁决官可调节温度（0.1-1.0）
- **持仓感知分析**：支持输入持仓信息（多头/空头/空仓 + 入场价）
- 支持并行/串行调用

### Web 前端（Bento Grid 风格）
- 现代化 Bento Grid 布局设计
- 实时 SSE 流式响应
- 温度滑块实时调节
- 页面导航：AI 分析、模型选择、K 线图表、历史分析
- **TradingView K线图表**：集成专业级 K 线图表
- 打字机效果：AI 分析结果逐字显示
- 响应式设计，支持桌面/平板/手机

### 数据源
- 币安永续合约（BinanceAPI）
- 支持代理配置
- CSV 文件导入
- 可扩展其他数据源

---

## 文件结构

```
Chanlun-Crypto/
├── 📄 主程序
│   ├── ai_strategy_engine.py   # AI策略引擎（三委员机制）
│   ├── main.py                 # 基础分析入口
│   ├── config.py               # 全局配置
│   └── result_formatter.py     # 结果格式化
│
├── 📁 缠论核心
│   ├── Chan.py                 # 缠论主类
│   ├── ChanConfig.py           # 缠论配置
│   ├── KLine/                  # K线处理
│   │   ├── KLine.py
│   │   ├── KLine_List.py
│   │   ├── KLine_Unit.py
│   │   └── TradeInfo.py
│   ├── Bi/                     # 笔计算
│   │   ├── Bi.py
│   │   ├── BiList.py
│   │   └── BiConfig.py
│   ├── Seg/                    # 线段计算
│   │   ├── Seg.py
│   │   ├── SegListChan.py
│   │   ├── SegListComm.py
│   │   ├── Eigen.py
│   │   └── EigenFX.py
│   ├── ZS/                     # 中枢计算
│   ├── BuySellPoint/           # 买卖点
│   │   ├── BS_point.py
│   │   ├── BSPointList.py
│   │   └── BSPointConfig.py
│   ├── Combiner/               # K线合并
│   │   ├── KLine_Combiner.py
│   │   └── Combine_Item.py
│   └── ChanModel/              # 缠论模型
│       └── Features.py
│
├── 📁 AI 引擎
│   ├── engines/                # AI 分析引擎
│   │   ├── cognitive_ai.py         # 认知 AI
│   │   ├── conflict_analyzer.py    # 冲突分析
│   │   ├── decision_engine.py      # 决策引擎
│   │   ├── explanation_engine.py   # 解释引擎
│   │   ├── risk_engine.py          # 风险引擎
│   │   ├── risk_narrative.py       # 风险叙述
│   │   └── structure_engine.py     # 结构引擎
│   └── models/                 # 状态模型
│       └── state_models.py
│
├── 📁 数据源
│   └── DataAPI/
│       ├── binanceAPI.py       # 币安数据源
│       ├── csvAPI.py           # CSV 数据源
│       └── CommonStockAPI.py   # 数据源基类
│
├── 📁 公共模块
│   └── Common/
│       ├── CEnum.py            # 枚举定义
│       ├── CTime.py            # 时间处理
│       ├── func_util.py        # 工具函数
│       ├── ChanException.py    # 异常类
│       └── cache.py            # 缓存
│
├── 📁 指标计算
│   └── Math/
│       └── MACD.py             # MACD 指标
│
├── 📁 Web 后端
│   └── web_backend/
│       ├── api/
│       │   ├── routes.py           # API 路由
│       │   └── sse.py              # SSE 流式响应
│       ├── models/
│       │   └── schemas.py          # 数据模型
│       └── main.py                 # FastAPI 入口
│
├── 📁 Web 前端
│   └── web/
│       ├── src/
│       │   ├── components/
│       │   │   ├── analysis/       # 分析组件
│       │   │   │   ├── CommitteeCard.tsx   # 三委员卡片
│       │   │   │   ├── JudgeCard.tsx       # 裁决官卡片
│       │   │   │   ├── AISummaryCard.tsx   # AI 总结卡片
│       │   │   │   ├── SymbolSelector.tsx  # 交易对选择
│       │   │   │   ├── PositionInput.tsx   # 持仓输入
│       │   │   │   ├── AnalyzeButton.tsx   # 分析按钮
│       │   │   │   └── TypewriterText.tsx  # 打字机效果
│       │   │   ├── chart/          # 图表组件
│       │   │   │   ├── ChartPage.tsx       # K线图表页面
│       │   │   │   └── KLineChart.tsx      # K线图表组件
│       │   │   ├── layout/         # 布局组件
│       │   │   │   ├── BentoGrid.tsx       # Bento Grid 布局
│       │   │   │   └── Sidebar.tsx         # 左侧任务栏
│       │   │   └── ui/             # UI 组件
│       │   │       └── TemperatureSlider.tsx  # 温度滑块
│       │   ├── hooks/
│       │   │   └── useSSE.ts       # SSE Hook
│       │   ├── stores/
│       │   │   └── analysisStore.ts # Zustand 状态管理
│       │   └── App.tsx             # 主应用
│       ├── index.html
│       └── package.json
│
└── 📄 文档
    ├── README.md               # 项目说明
    └── quick_guide.md          # 快速上手指南
```

---

## 安装

```bash
# 克隆项目
git clone https://github.com/164149043/Chanlun-Crypto.git
cd Chanlun-Crypto

# 安装依赖
pip install -r requirements.txt
```

## 配置

### 后端配置（config.py）

```python
# DeepSeek API
DEEPSEEK_API_KEY = "your-api-key"

# 代理（可选）
PROXY_URL = "http://127.0.0.1:7890"

# 三委员配置
COMMITTEE_CONFIG = {
    "enabled": True,              # 是否启用
    "committee_count": 3,         # 委员数量
    "committee_model": "deepseek-chat",
    "committee_temperatures": [0.4, 0.6, 0.7],  # 各委员温度（可在前端调节）
    "committee_max_tokens": 2000, # 委员最大输出
    "judge_model": "deepseek-reasoner",
    "judge_temperature": 0.3,     # 裁决官温度（可在前端调节）
    "judge_max_tokens": 1000,
    "parallel": True,             # 并行调用
    "timeout": 120,               # 超时时间
    "fallback_on_failure": True,  # 失败降级
}
```

### 前端配置

**字体配置（推荐）：**
- 英文标题：Inter
- 中文标题：Noto Sans SC
- 代码/数字：JetBrains Mono

**温度参数说明：**
| 委员 | 默认温度 | 角色 |
|------|----------|------|
| 委员A | 0.4 | 保守派 |
| 委员B | 0.6 | 中立派 |
| 委员C | 0.7 | 激进派 |
| 裁决官 | 0.3 | 综合决策 |

温度越低输出越确定，温度越高输出越多样化。

## 使用方法

### 方式一：Web 前端（推荐）

**启动后端服务：**
```bash
cd web_backend
python main.py
```
后端运行在 http://localhost:8000

**启动前端服务：**
```bash
cd web
npm install
npm run dev
```
前端运行在 http://localhost:5173

**功能说明：**
- 左侧任务栏：页面导航（AI 分析、模型选择、K 线图表、历史分析）
- AI 分析页：选择交易对、设置持仓情况、开始分析
- K 线图表页：TradingView 专业 K 线图表，实时行情
- 温度滑块：调节每个委员/裁决官的分析温度（0.1-1.0）
- 实时流式：分析结果逐字显示

### 方式二：命令行

```bash
python ai_strategy_engine.py
```

程序会依次提示：
1. 选择交易对（如 BTCUSDT）
2. 选择持仓情况（空仓/多头/空头）
3. 如果有持仓，输入入场价格

然后自动执行：
- 获取多周期缠论数据（D1/H4/H1/M15）
- 三委员独立分析
- 裁决官综合决策
- 输出最终策略

### 运行基础缠论分析

```bash
python main.py
```

---

## 输出示例

```
============================================================
分析 BTCUSDT
============================================================

获取多周期缠论数据...
  分析 D1 ...
  分析 H4 ...
  分析 H1 ...
  分析 M15 ...

============================================================
缠论数据
============================================================
## BTCUSDT - D1
当前价格: 65000
笔方向: up
线段方向: down
中枢: [64000, 66000]
...

============================================================
三委员分析结果
============================================================

【委员A】
根据日线级别分析，当前处于下跌线段中的反弹笔...

【委员B】
多周期共振分析显示，H4与H1存在方向冲突...

【委员C】
从风险收益比角度评估，当前入场盈亏比不足...

============================================================
裁决官最终结论
============================================================
综合三份分析报告，建议当前采取观望策略...
```

---

## 核心类说明

### CChan - 缠论主类

```python
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import KL_TYPE

chan = CChan(
    code="BTCUSDT",
    data_src="custom:binanceAPI.BinanceAPI",
    begin_time="2024-01-01",
    lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_4H],
    config=CChanConfig(),
)

# 获取缠论元素
kl = chan.kl_datas[KL_TYPE.K_DAY]
bi_list = kl.bi_list        # 笔列表
seg_list = kl.seg_list      # 线段列表
zs_list = kl.zs_list        # 中枢列表
bs_list = kl.bs_point_lst   # 买卖点列表
```

### 关键属性

| 类 | 属性 | 说明 |
|---|------|------|
| CKLine | `idx`, `high`, `low`, `fx`, `dir` | 合并K线 |
| CBi | `idx`, `dir`, `is_sure`, `klc_lst` | 笔 |
| CSeg | `idx`, `dir`, `is_sure`, `bi_list` | 线段 |
| CZS | `low`, `high`, `bi_lst` | 中枢 |
| CBS_Point | `is_buy`, `type`, `klu` | 买卖点 |

---

## 三委员机制说明

```
缠论数据 + 持仓信息 → 三委员独立分析 → 裁决官综合推理 → 最终策略
```

**设计原则：**
- **第一层（委员）**：自由表达，独立推理，可参考持仓信息，使用不同温度增加分析多样性
- **第二层（裁决官）**：只能基于三份报告推理，不能重新分析原始市场数据，不看持仓信息

**持仓感知：**
- 多头持仓：委员分析时会考虑"是否需要止盈/止损/加仓"
- 空头持仓：委员分析时会考虑"是否需要平仓/继续持有"
- 空仓：委员进行客观分析，不涉及持仓决策

**优势：**
- 多视角分析，减少单一视角盲点
- 温度差异化，平衡保守与激进
- 裁决官机制，确保结论一致性
- 持仓感知，提供更有针对性的建议

---

## 依赖

### 后端
- Python >= 3.11
- requests
- FastAPI
- （其他依赖见 requirements.txt）

### 前端
- Node.js >= 18
- React 19
- TypeScript
- Vite 7
- Tailwind CSS
- Framer Motion
- Zustand
- Lightweight Charts
- （其他依赖见 web/package.json）

---

## 注意事项

- 本工具仅供学习研究，不构成投资建议
- 加密货币市场风险较高，请谨慎决策
- 使用前请确保已配置正确的 API Key
- 日线获取 120 天数据，其他周期获取 60 天

---

## 致谢

- 基于缠论理论开发
- 本项目基于 [chan.py](https://github.com/Vespa314/chan.py) 二次开发，在原缠论核心算法基础上新增了 AI 协作智能分析引擎、Web 可视化界面等功能
