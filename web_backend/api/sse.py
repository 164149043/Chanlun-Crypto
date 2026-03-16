"""
SSE 流式处理 - 改造 AI 策略引擎支持流式输出
支持多Provider（DeepSeek、硅基流动等）
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, List

import httpx

# 导入配置
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    DEEPSEEK_API_KEY,
    SILICONFLOW_API_KEY,
    COMMITTEE_CONFIG,
    PROXY_URL,
    DEFAULT_AI_PROVIDER,
)
from ai_strategy_engine import (
    get_multi_cycle_data,
    build_analysis_prompt,
    build_judge_prompt,
    get_committee_config,
    get_api_key,
)

logger = logging.getLogger(__name__)

# 导入统一AI客户端
from providers import create_client


def format_sse_event(data: dict) -> str:
    """格式化 SSE 事件"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_ai_call(
    prompt: str,
    provider: str = None,
    model: str = None,
    temperature: float = 0.6,
    max_tokens: int = None,
    api_key: str = None,  # 保留向后兼容
) -> AsyncGenerator[str, None]:
    """
    流式调用 AI API (支持多Provider)

    Args:
        prompt: 提示词
        provider: Provider名称 ("deepseek" 或 "siliconflow")
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出 tokens
        api_key: API密钥（向后兼容）

    Yields:
        str: 逐字返回的 AI 输出
    """
    # 确定Provider
    provider = provider or DEFAULT_AI_PROVIDER

    # 获取API Key
    if not api_key:
        api_key = get_api_key(provider)

    if not api_key:
        yield "[错误: 未配置API密钥]"
        return

    # 创建客户端并流式调用
    client = create_client(provider, api_key, proxy_url=PROXY_URL)

    try:
        async for chunk in client.call_stream(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk
    except Exception as e:
        logger.error(f"[{provider}] 流式调用异常: {e}")
        yield f"[错误: {str(e)}]"


async def stream_committee_parallel(
    prompt: str,
    queue: asyncio.Queue,
):
    """
    并行流式调用单个委员 (支持多Provider)

    Args:
        prompt: 提示词
        queue: 用于传递输出的队列
    """
    committee_ids = ["committee_a", "committee_b", "committee_c"]
    committee_names = ["委员A", "委员B", "委员C"]

    async def run_single_committee(index: int):
        """运行单个委员分析"""
        committee_id = committee_ids[index]
        name = committee_names[index]

        # 获取该委员的独立配置
        role_config = get_committee_config(committee_id)
        provider = role_config["provider"]
        model = role_config["model"]
        temperature = role_config["temperature"]
        max_tokens = role_config.get("max_tokens")

        content = ""
        try:
            async for chunk in stream_ai_call(
                prompt,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                content += chunk
                await queue.put({
                    "committee_id": committee_id,
                    "name": name,
                    "content": content,
                    "done": False,
                })
        except Exception as e:
            logger.error(f"{name} 分析失败: {e}")
            content = f"[{name} 分析失败]"

        # 标记完成
        await queue.put({
            "committee_id": committee_id,
            "name": name,
            "content": content,
            "done": True,
        })
        return content

    # 并行启动三个委员
    tasks = [
        asyncio.create_task(run_single_committee(i))
        for i in range(3)
    ]

    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def stream_analyze_symbol(
    symbol: str,
    api_key: str = None,
    position = None,  # PositionInfo 类型（从 schemas 导入）
) -> AsyncGenerator[str, None]:
    """
    流式分析交易对

    Args:
        symbol: 交易对 (BTCUSDT / ETHUSDT)
        api_key: API 密钥（可选，默认使用配置文件中的）
        position: 持仓信息（可选，包含持仓类型和开仓均价）

    Yields:
        str: SSE 格式的事件字符串
    """
    if not api_key:
        api_key = DEEPSEEK_API_KEY

    if not api_key:
        yield format_sse_event({
            "stage": "error",
            "message": "未配置 DEEPSEEK_API_KEY",
            "progress": 0,
        })
        return

    config = COMMITTEE_CONFIG

    try:
        # 阶段 1: 获取缠论数据
        yield format_sse_event({
            "stage": "fetching",
            "message": f"正在获取 {symbol} 缠论数据...",
            "progress": 0.05,
        })

        # 在线程池中运行同步函数
        loop = asyncio.get_event_loop()
        chanlun_data = await loop.run_in_executor(None, get_multi_cycle_data, symbol)

        # 将持仓信息合并到缠论数据中（如果有持仓且不是 NONE）
        position_dict = None
        if position and position.position_type != "NONE":
            position_dict = {
                "type": position.position_type,
                "entry_price": position.entry_price,
            }
            chanlun_data["position"] = position_dict

        yield format_sse_event({
            "stage": "fetching",
            "message": f"缠论数据获取完成，开始 AI 分析...",
            "progress": 0.1,
        })

        # 检查是否启用三委员机制
        if not config.get("enabled", False):
            # 单次调用模式
            prompt = build_analysis_prompt(chanlun_data)
            content = ""
            async for chunk in stream_ai_call(prompt, api_key, temperature=0.6):
                content += chunk
                yield format_sse_event({
                    "stage": "single_analysis",
                    "message": "AI 分析中...",
                    "content": content,
                    "progress": 0.5,
                })

            yield format_sse_event({
                "stage": "complete",
                "message": "分析完成",
                "progress": 1.0,
            })
            return

        # 三委员并行模式
        prompt = build_analysis_prompt(chanlun_data, independent=True)

        # 初始化三个委员的状态
        committee_contents = {"committee_a": "", "committee_b": "", "committee_c": ""}
        committee_done = {"committee_a": False, "committee_b": False, "committee_c": False}

        # 通知前端开始三委员分析
        yield format_sse_event({
            "stage": "committees",
            "message": "三委员并行分析中...",
            "progress": 0.15,
        })

        # 创建队列用于接收并行输出
        queue = asyncio.Queue()

        # 启动并行分析任务（使用新的多Provider配置）
        analysis_task = asyncio.create_task(
            stream_committee_parallel(
                prompt,
                queue,
            )
        )

        # 实时处理队列中的输出
        while not all(committee_done.values()):
            try:
                # 设置超时，避免无限等待
                item = await asyncio.wait_for(queue.get(), timeout=180.0)
                committee_id = item["committee_id"]
                content = item["content"]
                done = item["done"]

                committee_contents[committee_id] = content
                committee_done[committee_id] = done

                # 计算进度
                done_count = sum(committee_done.values())
                progress = 0.15 + (done_count / 3) * 0.55

                # 发送更新
                yield format_sse_event({
                    "stage": committee_id,
                    "message": item["name"],
                    "content": content,
                    "progress": progress,
                })

            except asyncio.TimeoutError:
                logger.warning("委员分析超时")
                break

        # 确保任务完成
        try:
            await asyncio.wait_for(analysis_task, timeout=10.0)
        except asyncio.TimeoutError:
            analysis_task.cancel()

        # 获取最终分析结果
        analyses = [
            committee_contents["committee_a"],
            committee_contents["committee_b"],
            committee_contents["committee_c"],
        ]

        # 补齐到3份（如果有失败的情况）
        while len(analyses) < 3:
            analyses.append(analyses[0] if analyses else "")

        # 裁决官分析
        judge_config = get_committee_config("judge")
        yield format_sse_event({
            "stage": "judge",
            "message": f"裁决官分析中 ({judge_config['provider']}/{judge_config['model']})...",
            "progress": 0.75,
        })

        judge_prompt = build_judge_prompt(*analyses[:3], position=position_dict)
        judge_content = ""

        async for chunk in stream_ai_call(
            judge_prompt,
            provider=judge_config["provider"],
            model=judge_config["model"],
            temperature=judge_config["temperature"],
            max_tokens=judge_config.get("max_tokens"),
        ):
            judge_content += chunk
            yield format_sse_event({
                "stage": "judge",
                "message": "裁决官",
                "content": judge_content,
                "progress": 0.85,
            })

        # 完成
        yield format_sse_event({
            "stage": "complete",
            "message": "分析完成",
            "progress": 1.0,
        })

    except Exception as e:
        logger.error(f"分析失败: {e}")
        yield format_sse_event({
            "stage": "error",
            "message": str(e),
            "progress": 0,
        })