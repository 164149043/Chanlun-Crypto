# 快速上手指南

## 项目简介

基于缠论理论的加密货币量化分析工具，集成 AI 智能策略分析。

**核心功能：**
- 缠论元素计算（K线、笔、线段、中枢、买卖点）
- 多周期数据分析（D1/H4/H1/M15）
- AI 策略引擎（三委员 + 裁决官机制）
- 币安永续合约数据源

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.py`：

```python
# DeepSeek API 密钥
DEEPSEEK_API_KEY = "your-api-key"

# 代理（可选）
PROXY_URL = "http://127.0.0.1:7890"

# 三委员配置
COMMITTEE_CONFIG = {
    "enabled": True,
    "committee_count": 3,
    "committee_model": "deepseek-chat",
    "committee_temperatures": [0.4, 0.6, 0.8],
    "judge_model": "deepseek-reasoner",
    "judge_temperature": 0.3,
    "parallel": True,
}
```

### 3. 运行

```bash
# AI 策略分析（推荐）
python ai_strategy_engine.py

# 基础缠论分析
python main.py
```

---

## 目录结构

```
chan.py/
├── Chan.py              # 缠论核心类
├── ChanConfig.py        # 缠论配置
├── ai_strategy_engine.py # AI策略引擎（三委员机制）
├── main.py              # 基础分析入口
├── config.py            # 全局配置
├── result_formatter.py  # 结果格式化
├── KLine/               # K线处理
├── Bi/                  # 笔计算
├── Seg/                 # 线段计算
├── ZS/                  # 中枢计算
├── BuySellPoint/        # 买卖点
├── DataAPI/             # 数据源
│   └── binanceAPI.py    # 币安数据源
└── Common/              # 公共工具
```

---

## AI 策略引擎

### 三委员 + 裁决官机制

```
缠论数据 → 三委员独立分析 → 裁决官综合推理 → 最终策略
```

**设计原则：**
- 第一层（委员）：自由表达，独立推理，不同温度增加多样性
- 第二层（裁决官）：只能基于三份报告推理，不能看原始数据

### 配置说明

| 参数 | 说明 |
|------|------|
| `enabled` | 是否启用三委员机制 |
| `committee_count` | 委员数量（默认3） |
| `committee_model` | 委员使用的模型 |
| `committee_temperatures` | 各委员的温度参数 |
| `judge_model` | 裁决官使用的模型 |
| `judge_temperature` | 裁决官温度 |
| `parallel` | 是否并行调用委员 |

---

## 缠论核心类

### CChan 使用

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
```

### 取出缠论元素

```python
kl_datas = chan.kl_datas
kl = kl_datas[KL_TYPE.K_DAY]

# 合并K线
klines = kl.lst

# 笔列表
bi_list = kl.bi_list

# 线段列表
seg_list = kl.seg_list

# 中枢列表
zs_list = kl.zs_list

# 买卖点列表
bs_point_lst = kl.bs_point_lst
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

## 数据源接入

### 自定义数据源

继承 `CCommonStockApi` 并实现 `get_kl_data` 方法：

```python
from DataAPI.CommonStockAPI import CCommonStockApi
from KLine.KLine_Unit import CKLine_Unit
from Common.CEnum import KL_TYPE

class MyDataAPI(CCommonStockApi):
    def __init__(self, code, k_type, begin_date, end_date):
        super().__init__(code, k_type, begin_date, end_date)

    def get_kl_data(self):
        # 获取数据逻辑
        for item in my_data:
            yield CKLine_Unit({
                DATA_FIELD.FIELD_TIME: time,
                DATA_FIELD.FIELD_OPEN: open,
                DATA_FIELD.FIELD_CLOSE: close,
                DATA_FIELD.FIELD_HIGH: high,
                DATA_FIELD.FIELD_LOW: low,
            })
```

使用：`data_src="custom:my_file.MyDataAPI"`

---

## 常见问题

### Q: 买卖点信号为什么会消失？

框架计算的是"当前帧"下的缠论元素。随着K线增加，原有买卖点可能被证明不成立而消失。

### Q: is_sure 标记是什么？

- `is_sure=True`：已确定的元素，后续不会再变更
- `is_sure=False`：未确定的元素（虚笔/虚段），可能随新K线变化

### Q: 报 K线时间错误？

如果数据级别为天级别以下且K线时间可能出现0点0分，在数据源类中将 CTime 的 `auto` 设置为 False。

---

## 注意事项

- 本工具仅供学习研究，不构成投资建议
- 加密货币市场风险较高，请谨慎决策
- 使用前请确保已配置正确的 API Key
- 依赖 Python >= 3.11
