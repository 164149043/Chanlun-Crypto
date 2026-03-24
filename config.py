"""
配置文件 - 缠论量化分析框架
API Key 从环境变量读取，此文件可以安全上传到 GitHub
"""
import os

# ============================================
# AI Provider 配置（支持多AI服务提供商）
# ============================================
# 可选值: "deepseek", "siliconflow", "gemini"
# 设置默认使用的Provider
DEFAULT_AI_PROVIDER = "deepseek"

# DeepSeek API配置
# 获取密钥: https://platform.deepseek.com/
# 本地开发: 在 config.local.py 中设置，或设置环境变量 DEEPSEEK_API_KEY
# Vercel部署: 在 Vercel Dashboard → Settings → Environment Variables 中设置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 硅基流动 API配置
# 获取密钥: https://cloud.siliconflow.cn/
# 本地开发: 在 config.local.py 中设置，或设置环境变量 SILICONFLOW_API_KEY
# Vercel部署: 在 Vercel Dashboard → Settings → Environment Variables 中设置
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")

# Google Gemini API配置
# 获取密钥: https://aistudio.google.com/apikey
# 本地开发: 在 config.local.py 中设置，或设置环境变量 GEMINI_API_KEY
# Vercel部署: 在 Vercel Dashboard → Settings → Environment Variables 中设置
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ============================================
# 代理设置（可选）
# ============================================
# 如果网络无法访问 Binance，可以设置代理
# 格式: "http://127.0.0.1:7890" 或留空不使用
PROXY_URL = os.environ.get("PROXY_URL", "")  # 留空 = 不使用代理

# ============================================
# 本地开发覆盖（可选）
# ============================================
# 如果存在 config.local.py，则导入并覆盖上面的配置
# 这样本地开发时可以把敏感信息放在 config.local.py（不提交到git）
try:
    from config_local import *  # noqa: F401, F403
except ImportError:
    pass

# ============================================
# 交易对选择
# ============================================
# 支持的交易对列表
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT"]

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
    "provider": DEFAULT_AI_PROVIDER,  # 使用哪个Provider
    "model": None,                    # None表示使用Provider默认模型
    "timeout": 120,                  # API超时时间（秒）
    "max_retries": 3,                # 最大重试次数
}

# ============================================
# 三委员机制配置（AI策略引擎）
# ============================================
# 三委员 + 裁决官的多轮推理机制
# 每个角色可以独立选择Provider和模型
# 巔员：独立分析，各自使用不同温度以增加多样性
# 裁决官：基于三份报告进行二级推理
# 核心约束：裁决官不看原始市场数据，只看三份报告
COMMITTEE_CONFIG = {
    "enabled": True,                    # 是否启用三委员机制
    "committee_count": 3,               # 委员数量
    "parallel": True,                   # 是否并行调用委员
    "timeout": 120,                     # 单次调用超时（秒）
    "fallback_on_failure": True,        # 委员失败时是否降级到单次调用

    # ----------------------------------------
    # 寏个角色独立配置（支持跨Provider）
    # ----------------------------------------
    # 委员A配置
    "committee_a": {
        "provider": "deepseek",                   # 可选: deepseek, siliconflow, gemini
    #   "model": "Qwen/Qwen3-30B-A3B-Thinking-2507",
        "model": "deepseek-chat",                  # DeepSeek对话模型
        "temperature": 0.4,                        # 保守
        "max_tokens": 1000,
    },
    # 委员B配置
    "committee_b": {
        "provider": "gemini",                     # Gemini官方API
        "model": "gemini-3-flash-preview",              # Gemini快速模型
        "temperature": 0.5,                         # 中性
        "max_tokens": 2200,
    },
    # 委员C配置
    "committee_c": {
        "provider": "gemini",                   # Gemini官方API
        "model": "gemini-3.1-flash-lite-preview",          # Gemini轻量模型
        "temperature": 0.7,                         # 激进
        "max_tokens": 2200,
    },
    # 裁决官配置
    "judge": {
        "provider": "gemini",                     # Gemini官方API
        "model": "gemini-3.1-pro-preview",                # Gemini推理模型
        "temperature": 0.3,                         # 稳定性
        "max_tokens": 2000,
    },
}
