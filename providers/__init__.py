"""
AI Provider 配置模块 - 支持多AI服务提供商

支持的Provider:
- DeepSeek: 官方DeepSeek API
- SiliconFlow: 硅基流动（支持Qwen、DeepSeek、GLM、Llama等多种模型）
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# 尝试导入 ai_client，如果失败则定义占位符
try:
    from .ai_client import call_ai, create_client, AIClient
except ImportError as e:
    import logging
    logging.warning(f"providers: 无法导入 ai_client: {e}")
    # 定义占位符函数，避免导入错误
    def call_ai(*args, **kwargs):
        raise RuntimeError("ai_client 模块未正确加载")
    def create_client(*args, **kwargs):
        raise RuntimeError("ai_client 模块未正确加载")
    class AIClient:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("ai_client 模块未正确加载")


class ProviderType(Enum):
    """AI服务提供商类型"""
    DEEPSEEK = "deepseek"
    SILICONFLOW = "siliconflow"


@dataclass
class ProviderConfig:
    """Provider配置"""
    name: str                                    # Provider名称
    provider_type: ProviderType                  # Provider类型
    base_url: str                                # API基础URL
    default_model: str                           # 默认模型
    api_key_env: str = ""                        # API Key环境变量名
    supports_streaming: bool = True              # 是否支持流式输出
    supports_reasoning: bool = False             # 是否支持推理模型
    models: List[str] = field(default_factory=list)  # 支持的模型列表


# ============================================
# Provider模板定义
# ============================================
PROVIDER_TEMPLATES: Dict[str, ProviderConfig] = {
    "deepseek": ProviderConfig(
        name="DeepSeek",
        provider_type=ProviderType.DEEPSEEK,
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        supports_streaming=True,
        supports_reasoning=True,
        models=[
            "deepseek-chat",        # 通用对话模型
            "deepseek-reasoner",    # 深度推理模型
        ],
    ),

    "siliconflow": ProviderConfig(
        name="SiliconFlow (硅基流动)",
        provider_type=ProviderType.SILICONFLOW,
        base_url="https://api.siliconflow.cn/v1",
        default_model="Qwen/Qwen2.5-72B-Instruct",
        api_key_env="SILICONFLOW_API_KEY",
        supports_streaming=True,
        supports_reasoning=True,  # DeepSeek-R1支持推理
        models=[
            # Qwen系列（通义千问）
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2-7B-Instruct",
            # DeepSeek系列
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",      # 推理模型
            "Pro/deepseek-ai/DeepSeek-R1",  # Pro版推理模型
            # GLM系列（智谱ChatGLM）
            "THUDM/glm-4-9b-chat",
            "THUDM/chatglm-4-9b-chat",
            # Llama系列
            "meta-llama/Llama-3.3-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            # 其他
            "Pro/Qwen/Qwen2.5-72B-Instruct",
        ],
    ),
}


def get_provider_config(provider_name: str) -> ProviderConfig:
    """
    获取Provider配置

    Args:
        provider_name: Provider名称 ("deepseek" 或 "siliconflow")

    Returns:
        ProviderConfig: Provider配置对象

    Raises:
        ValueError: 未知的Provider名称
    """
    if provider_name not in PROVIDER_TEMPLATES:
        available = ", ".join(PROVIDER_TEMPLATES.keys())
        raise ValueError(f"未知的Provider: {provider_name}。可用: {available}")

    return PROVIDER_TEMPLATES[provider_name]


def get_api_url(provider_name: str, endpoint: str = "chat/completions") -> str:
    """
    获取完整API URL

    Args:
        provider_name: Provider名称
        endpoint: API端点 (默认: chat/completions)

    Returns:
        str: 完整的API URL
    """
    config = get_provider_config(provider_name)
    return f"{config.base_url}/{endpoint}"


def get_available_providers() -> List[str]:
    """获取所有可用的Provider名称列表"""
    return list(PROVIDER_TEMPLATES.keys())


def get_available_models(provider_name: str) -> List[str]:
    """
    获取指定Provider支持的模型列表

    Args:
        provider_name: Provider名称

    Returns:
        List[str]: 模型名称列表
    """
    config = get_provider_config(provider_name)
    return config.models.copy()


def is_reasoning_model(provider_name: str, model: str) -> bool:
    """
    判断是否为推理模型

    Args:
        provider_name: Provider名称
        model: 模型名称

    Returns:
        bool: 是否为推理模型
    """
    # 根据模型名称判断
    reasoning_keywords = ["reasoner", "r1", "-r1", "reasoning"]
    model_lower = model.lower()
    return any(kw in model_lower for kw in reasoning_keywords)
