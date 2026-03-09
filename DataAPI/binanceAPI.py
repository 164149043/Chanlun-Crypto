"""
Binance 数据源接口
使用 requests 直接访问 Binance 现货 API（不需要代理）
"""

from typing import Iterable
from datetime import datetime, timezone
import time

import requests

from Common.CEnum import KL_TYPE, DATA_FIELD
from Common.CTime import CTime
from KLine.KLine_Unit import CKLine_Unit


class BinanceAPI:
    """Binance 数据源 API"""

    # K线类型映射到 Binance interval
    KL_TYPE_MAP = {
        KL_TYPE.K_1M: '1m',
        KL_TYPE.K_3M: '3m',
        KL_TYPE.K_5M: '5m',
        KL_TYPE.K_15M: '15m',
        KL_TYPE.K_30M: '30m',
        KL_TYPE.K_60M: '1h',
        KL_TYPE.K_4H: '4h',
        KL_TYPE.K_DAY: '1d',
        KL_TYPE.K_WEEK: '1w',
        KL_TYPE.K_MON: '1M',
    }

    # Binance API 地址
    BASE_URL = "https://api.binance.com"
    KLINES_PATH = "/api/v3/klines"

    # 代理配置
    _proxies = None

    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=None):
        """
        初始化 Binance API

        Args:
            code: 交易对代码，如 "BTCUSDT"
            k_type: K线类型
            begin_date: 开始日期
            end_date: 结束日期
            autype: 复权类型（加密货币不需要）
        """
        self.code = code
        self.k_type = k_type
        self.begin_date = begin_date
        self.end_date = end_date
        self.autype = autype

    @classmethod
    def set_proxy(cls, proxy_url: str):
        """
        设置代理（可选）

        Args:
            proxy_url: 代理地址，如 "http://127.0.0.1:7890"
                       传空字符串则不使用代理
        """
        if proxy_url and proxy_url.strip():
            cls._proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            print(f"[INFO] 已设置代理: {proxy_url}")
        else:
            cls._proxies = None
            print("[INFO] 已取消代理")

    def _fetch_klines(self, symbol: str, interval: str, limit: int = 1000) -> list:
        """
        获取 K线数据

        Args:
            symbol: 交易对
            interval: 周期
            limit: 数量限制

        Returns:
            K线数据列表
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        # 重试机制
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                print(f"[INFO] 正在获取 {symbol} {interval} 数据...")

                resp = requests.get(
                    self.BASE_URL + self.KLINES_PATH,
                    params=params,
                    proxies=self._proxies,
                    timeout=15,
                )

                if not resp.ok:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

                data = resp.json()

                if not isinstance(data, list):
                    raise RuntimeError(f"返回格式异常: {data}")

                print(f"[INFO] 成功获取 {len(data)} 根 K线")
                return data

            except requests.exceptions.SSLError as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"[ERROR] SSL错误: {e}")
                print("[提示] 可以在 config.py 中设置 PROXY_URL")

            except requests.RequestException as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"[ERROR] 网络错误: {e}")
                print("[提示] 可以在 config.py 中设置 PROXY_URL")

        return []

    def get_kl_data(self) -> Iterable[CKLine_Unit]:
        """获取 K线数据生成器"""
        interval = self.KL_TYPE_MAP.get(self.k_type)
        if interval is None:
            print(f"[ERROR] 不支持的 K线类型: {self.k_type}")
            return

        # 获取数据
        klines = self._fetch_klines(self.code, interval, limit=1000)

        for item in klines:
            if not isinstance(item, (list, tuple)) or len(item) < 7:
                continue

            # Binance K线格式: [open_time, open, high, low, close, volume, close_time, ...]
            open_time_ms = int(item[0])
            open_price = float(item[1])
            high = float(item[2])
            low = float(item[3])
            close = float(item[4])
            volume = float(item[5])

            # 转换时间戳
            dt = datetime.fromtimestamp(open_time_ms / 1000.0, tz=timezone.utc)

            # 创建 CTime，设置 auto=False 避免时间自动调整
            item_dict = {
                DATA_FIELD.FIELD_TIME: CTime(
                    dt.year, dt.month, dt.day, dt.hour, dt.minute,
                    auto=False  # 关键修复：不自动调整时间
                ),
                DATA_FIELD.FIELD_OPEN: open_price,
                DATA_FIELD.FIELD_HIGH: high,
                DATA_FIELD.FIELD_LOW: low,
                DATA_FIELD.FIELD_CLOSE: close,
                DATA_FIELD.FIELD_VOLUME: volume,
            }

            yield CKLine_Unit(item_dict)

    @classmethod
    def do_init(cls):
        """初始化数据源（类方法）"""
        pass

    @classmethod
    def do_close(cls):
        """关闭数据源（类方法）"""
        pass