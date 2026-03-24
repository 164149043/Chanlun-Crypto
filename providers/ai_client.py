"""
统一AI客户端 - 支持多Provider的AI调用

支持:
- DeepSeek官方API
- 硅基流动(SiliconFlow) API
- Google Gemini API
- 同步和异步调用
- 流式输出
"""

import json
import logging
import time
from typing import Any, AsyncGenerator, Dict, Optional

import httpx
import requests

logger = logging.getLogger(__name__)

# Provider配置（内联定义避免循环导入）
PROVIDER_BASE_URLS = {
    "deepseek": "https://api.deepseek.com/v1",
    "siliconflow": "https://api.siliconflow.cn/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta",  # Gemini 不使用此URL
}

PROVIDER_DEFAULT_MODELS = {
    "deepseek": "deepseek-chat",
    "siliconflow": "Qwen/Qwen2.5-72B-Instruct",
    "gemini": "gemini-3.1-flash",  # 默认使用快速版，实时预警
}

# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = "你是专业交易分析助手，请用中文回答。"


def get_api_url(provider: str, endpoint: str = "chat/completions") -> str:
    """获取完整API URL"""
    base_url = PROVIDER_BASE_URLS.get(provider, PROVIDER_BASE_URLS["deepseek"])
    return f"{base_url}/{endpoint}"


class AIClient:
    """
    统一AI客户端

    支持同步和异步调用，支持流式输出
    """

    def __init__(
        self,
        provider: str,
        api_key: str,
        timeout: int = 120,
        max_retries: int = 3,
        proxy_url: Optional[str] = None,
    ):
        """
        初始化AI客户端

        Args:
            provider: Provider名称 ("deepseek" 或 "siliconflow")
            api_key: API密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            proxy_url: 代理URL（可选）
        """
        self.provider = provider
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.proxy_url = proxy_url

        # 获取Provider配置
        self.base_url = PROVIDER_BASE_URLS.get(provider, PROVIDER_BASE_URLS["deepseek"])
        self.default_model = PROVIDER_DEFAULT_MODELS.get(provider, "deepseek-chat")

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: Optional[int] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """构建请求负载"""
        model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        return payload

    def call(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: Optional[int] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        """
        同步调用AI API

        Args:
            prompt: 提示词
            model: 模型名称（可选，使用Provider默认模型）
            temperature: 温度参数
            max_tokens: 最大输出tokens
            system_prompt: 系统提示词

        Returns:
            str: AI响应内容
        """
        # Gemini 使用单独的 SDK
        if self.provider == "gemini":
            return self._call_gemini(prompt, model, temperature, system_prompt)

        url = get_api_url(self.provider)
        headers = self._build_headers()
        payload = self._build_payload(
            prompt, model, temperature, max_tokens, system_prompt, stream=False
        )

        model_name = model or self.default_model

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"[{self.provider}] API调用 (model={model_name}, temp={temperature}) "
                    f"尝试 {attempt + 1}/{self.max_retries}"
                )

                proxies = None
                if self.proxy_url:
                    proxies = {"http": self.proxy_url, "https": self.proxy_url}

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    proxies=proxies,
                )
                response.raise_for_status()

                data = response.json()
                choices = data.get("choices", [{}])
                if choices:
                    message = choices[0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        return content

                logger.warning(f"[{self.provider}] API返回空内容")

            except requests.exceptions.Timeout:
                logger.error(f"[{self.provider}] API请求超时")
            except requests.exceptions.HTTPError as e:
                logger.error(f"[{self.provider}] API HTTP错误: {e}")
                # 尝试解析错误信息
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                    logger.error(f"[{self.provider}] 错误详情: {error_msg}")
                except Exception:
                    pass
            except requests.exceptions.RequestException as e:
                logger.error(f"[{self.provider}] API请求失败: {e}")

            # 指数退避重试
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"[{self.provider}] 等待 {wait_time}秒后重试...")
                time.sleep(wait_time)

        return ""

    def _call_gemini(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.6,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        """
        调用 Gemini API

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            system_prompt: 系统提示词

        Returns:
            str: AI响应内容
        """
        try:
            from google import genai
        except ImportError:
            logger.error("[gemini] google-genai 未安装，请运行: pip install google-genai")
            return "[错误: google-genai 未安装]"

        model_name = model or self.default_model
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"[gemini] API调用 (model={model_name}, temp={temperature}) "
                    f"尝试 {attempt + 1}/{self.max_retries}"
                )

                client = genai.Client(api_key=self.api_key)

                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config={
                        "temperature": temperature,
                    }
                )

                if response.text:
                    return response.text

                logger.warning("[gemini] API返回空内容")

            except Exception as e:
                logger.error(f"[gemini] API请求失败: {e}")

            # 指数退避重试
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"[gemini] 等待 {wait_time}秒后重试...")
                time.sleep(wait_time)

        return ""

    async def _call_gemini_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.6,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用 Gemini API

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            system_prompt: 系统提示词

        Yields:
            str: 逐字返回的AI输出
        """
        try:
            from google import genai
        except ImportError:
            yield "[错误: google-genai 未安装]"
            return

        model_name = model or self.default_model
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            logger.info(f"[gemini] 流式API调用 (model={model_name}, temp={temperature})")

            client = genai.Client(api_key=self.api_key)

            # 使用异步流式调用（aio 属性）
            async for chunk in await client.aio.models.generate_content_stream(
                model=model_name,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                }
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"[gemini] 流式调用异常: {e}")
            yield f"[错误: {str(e)}]"

    async def call_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.6,
        max_tokens: Optional[int] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用AI API

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出tokens
            system_prompt: 系统提示词

        Yields:
            str: 逐字返回的AI输出
        """
        # Gemini 流式调用
        if self.provider == "gemini":
            async for chunk in self._call_gemini_stream(prompt, model, temperature, system_prompt):
                yield chunk
            return

        url = get_api_url(self.provider)
        headers = self._build_headers()
        payload = self._build_payload(
            prompt, model, temperature, max_tokens, system_prompt, stream=True
        )

        timeout = httpx.Timeout(self.timeout, connect=30.0)
        proxy = self.proxy_url if self.proxy_url else None

        async with httpx.AsyncClient(timeout=timeout, proxy=proxy) as client:
            try:
                async with client.stream(
                    "POST", url, headers=headers, json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        if line.startswith("data: "):
                            chunk = line[6:]
                            if chunk == "[DONE]":
                                break

                            try:
                                data = json.loads(chunk)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

            except httpx.HTTPStatusError as e:
                logger.error(f"[{self.provider}] API请求失败: {e}")
                yield f"[错误: API请求失败 - {e.response.status_code}]"
            except Exception as e:
                logger.error(f"[{self.provider}] 流式调用异常: {e}")
                yield f"[错误: {str(e)}]"


def create_client(
    provider: str,
    api_key: str,
    timeout: int = 120,
    max_retries: int = 3,
    proxy_url: Optional[str] = None,
) -> AIClient:
    """
    工厂函数：创建AI客户端

    Args:
        provider: Provider名称 (deepseek, siliconflow)
        api_key: API密钥
        timeout: 超时时间
        max_retries: 最大重试次数
        proxy_url: 代理URL

    Returns:
        AIClient: AI客户端实例
    """
    return AIClient(provider, api_key, timeout, max_retries, proxy_url)


def call_ai(
    prompt: str,
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    temperature: float = 0.6,
    max_tokens: Optional[int] = None,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    timeout: int = 120,
    max_retries: int = 3,
    proxy_url: Optional[str] = None,
) -> str:
    """
    便捷函数：调用AI API

    Args:
        prompt: 提示词
        provider: Provider名称
        api_key: API密钥
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出tokens
        system_prompt: 系统提示词
        timeout: 超时时间
        max_retries: 最大重试次数
        proxy_url: 代理URL

    Returns:
        str: AI响应内容
    """
    client = create_client(provider, api_key, timeout, max_retries, proxy_url)
    return client.call(prompt, model, temperature, max_tokens, system_prompt)
