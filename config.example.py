"""
配置文件模板 - 复制为 config.py 并填入真实值
"""

# ============================================
# DeepSeek API（用于 AI 分析）
# ============================================
# 获取密钥: https://platform.deepseek.com/
# 留空则只输出缠论数据，不进行 AI 分析
DEEPSEEK_API_KEY = "your-api-key-here"

# ============================================
# 代理设置（可选）
# ============================================
# 如果网络无法访问 Binance，可以设置代理
# 格式: "http://127.0.0.1:7890" 或留空不使用
PROXY_URL = ""  # 留空 = 不使用代理

# ============================================
# 交易对选择
# ============================================
# 只支持 BTCUSDT 和 ETHUSDT
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# 周期名称
PERIOD_NAMES = {
    "K_15M": "15分钟",
    "K_60M": "1小时",
    "K_4H": "4小时",
    "K_DAY": "日线",
}

# ============================================
# 输出配置
# ============================================
PRINT_RAW_DATA = True   # 打印缠论原始数据
SAVE_TO_FILE = False    # 保存到文件
OUTPUT_FILE = "analysis_result.md"

# ============================================
# 引擎配置（4层引擎架构）
# ============================================
ENGINE_CONFIG = {
    # 结构引擎
    "structure": {
        "dominant_cycle_priority": ["日线", "4小时", "1小时"],  # 周期优先级
        "trend_threshold": 0.3,  # 趋势判断阈值
    },

    # 风控引擎
    "risk": {
        "max_position_size": 0.5,     # 最大仓位 50%
        "min_position_size": 0.1,     # 最小仓位 10%
        "min_reward_ratio": 2.0,      # 最小盈亏比
        "atr_period": 14,             # ATR周期
        "stop_loss_atr_multiplier": 1.5,  # 止损ATR倍数
    },

    # 决策引擎
    "decision": {
        "min_confidence": 0.6,        # 最小置信度
        "wait_threshold": 2.0,        # WAIT阈值（加权分数）
        "high_prob_threshold": 0.65,  # 高概率阈值
    },

    # 解释引擎
    "explanation": {
        "use_ai": False,              # 是否使用AI生成解释（当前使用规则）
        "language": "zh-CN",          # 输出语言
    }
}

# ============================================
# 系统评分配置
# ============================================
MIN_SYSTEM_SCORE = 6.5  # 最低系统评分阈值

# ============================================
# 认知AI配置（AI认知增强层）
# ============================================
# AI只做认知增强，不改决策
# 提供：风险提醒、结构演化路径、情景分析
COGNITIVE_AI_CONFIG = {
    "enabled": True,                 # 是否启用AI认知增强
    "model": "deepseek-reasoner",    # 使用的模型
    "timeout": 120,                  # API超时时间（秒）
    "max_retries": 3,                # 最大重试次数
}

# ============================================
# 三委员机制配置（AI策略引擎）
# ============================================
# 三委员 + 裁决官的多轮推理机制
# 委员：独立分析，各自使用不同温度以增加多样性
# 裁决官：基于三份报告进行二级推理，temperature=0.3（稳定性）
# 核心约束：裁决官不看原始市场数据，只看三份报告
COMMITTEE_CONFIG = {
    "enabled": True,                    # 是否启用三委员机制
    "committee_count": 3,               # 委员数量
    # 每个委员独立设置温度（温度越高越随机/创意，越低越稳定/保守）
    "committee_temperatures": [0.4, 0.7, 0.8],  # 委员A保守, B中性, C激进
    "judge_temperature": 0.3,           # 裁决官温度（稳定性）
    "committee_model": "deepseek-chat", # 委员使用的模型（快速）
    "judge_model": "deepseek-reasoner", # 裁决官使用的模型（深度）
    "committee_max_tokens": 2000,       # 委员最大输出 tokens（详细分析）
    "judge_max_tokens": 2000,           # 裁决官最大输出 tokens（简洁结论）
    "parallel": True,                   # 是否并行调用委员
    "timeout": 120,                     # 单次调用超时（秒）
    "fallback_on_failure": True,        # 委员失败时是否降级到单次调用
}
