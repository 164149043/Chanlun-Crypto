"""
缠论结果格式化模块
将缠论计算结果格式化为可读的文本，供 AI 分析使用
"""

from typing import List


def format_chan_result(chan, symbol: str, period_name: str) -> str:
    """
    将缠论计算结果格式化为文本

    Args:
        chan: CChan 实例
        symbol: 交易对符号
        period_name: K线周期名称

    Returns:
        格式化后的文本
    """
    result = f"## {symbol} - {period_name}\n\n"

    try:
        kl_data = chan[0]
    except Exception as e:
        return f"## {symbol} - {period_name}\n\n获取数据失败: {e}\n"

    # 1. 最新K线信息 + MACD
    result += "### 最新K线\n"
    try:
        if kl_data.lst and len(kl_data.lst) > 0:
            last_klc = kl_data.lst[-1]
            if hasattr(last_klc, 'lst') and last_klc.lst and len(last_klc.lst) > 0:
                last_klu = last_klc.lst[-1]
                result += f"- 时间: {last_klu.time}\n"
                result += f"- 开盘价: {last_klu.open:.2f}\n"
                result += f"- 最高价: {last_klu.high:.2f}\n"
                result += f"- 最低价: {last_klu.low:.2f}\n"
                result += f"- 收盘价: {last_klu.close:.2f}\n"
                # 添加 MACD
                if hasattr(last_klu, 'macd') and last_klu.macd:
                    result += f"- MACD: {last_klu.macd.macd:.2f}\n"
                    result += f"- DIF: {last_klu.macd.DIF:.2f}\n"
                    result += f"- DEA: {last_klu.macd.DEA:.2f}\n"
                result += "\n"
            else:
                result += "- 暂无K线数据\n\n"
        else:
            result += "- 暂无K线数据\n\n"
    except Exception as e:
        result += f"- 获取K线信息失败: {e}\n\n"

    # 2. 笔信息 + MACD
    result += "### 笔分析\n"
    try:
        bi_list = list(kl_data.bi_list)
        if bi_list:
            # 最近3笔
            recent_count = min(3, len(bi_list))
            for i in range(recent_count):
                bi = bi_list[-(recent_count - i)]
                idx = len(bi_list) - recent_count + i
                try:
                    direction = "向上" if bi.dir.name == "UP" else "向下"
                    begin_val = bi.get_begin_val()
                    end_val = bi.get_end_val()

                    # 从笔的结束K线获取 MACD
                    macd_info = ""
                    try:
                        end_klu = bi.get_end_klu()
                        if hasattr(end_klu, 'macd') and end_klu.macd:
                            macd_info = f", MACD={end_klu.macd.macd:.2f}"
                    except:
                        pass

                    result += f"- 笔{idx}: {direction}, 起点={begin_val:.2f}, 终点={end_val:.2f}{macd_info}\n"
                except:
                    result += f"- 笔{idx}: 获取详情失败\n"

            # 当前笔状态
            last_bi = bi_list[-1]
            try:
                direction = "向上" if last_bi.dir.name == "UP" else "向下"
                result += f"\n当前笔: {direction}\n\n"
            except:
                pass
        else:
            result += "- 暂无笔数据\n\n"
    except Exception as e:
        result += f"- 获取笔信息失败: {e}\n\n"

    # 3. 线段信息
    result += "### 线段分析\n"
    try:
        seg_list = list(kl_data.seg_list)
        if seg_list:
            # 最近2个线段
            recent_count = min(2, len(seg_list))
            for i in range(recent_count):
                seg = seg_list[-(recent_count - i)]
                idx = len(seg_list) - recent_count + i
                try:
                    direction = "向上" if seg.dir.name == "UP" else "向下"
                    begin_val = seg.get_begin_val()
                    end_val = seg.get_end_val()
                    result += f"- 线段{idx}: {direction}, 起点={begin_val:.2f}, 终点={end_val:.2f}\n"
                except:
                    result += f"- 线段{idx}: 获取详情失败\n"

            # 当前线段状态
            last_seg = seg_list[-1]
            try:
                direction = "向上" if last_seg.dir.name == "UP" else "向下"
                result += f"\n当前线段: {direction}\n\n"
            except:
                pass
        else:
            result += "- 暂无线段数据\n\n"
    except Exception as e:
        result += f"- 获取线段信息失败: {e}\n\n"

    # 4. 中枢信息
    result += "### 中枢分析\n"
    try:
        zs_list = list(kl_data.zs_list)
        if zs_list:
            # 最近3个中枢
            recent_count = min(3, len(zs_list))
            for i in range(recent_count):
                zs = zs_list[-(recent_count - i)]
                idx = len(zs_list) - recent_count + i
                try:
                    result += f"- 中枢{idx}: 高={zs.high:.2f}, 低={zs.low:.2f}\n"
                except:
                    result += f"- 中枢{idx}: 获取详情失败\n"

            # 当前价格相对于最新中枢的位置
            last_zs = zs_list[-1]
            try:
                if kl_data.lst and len(kl_data.lst) > 0:
                    last_klc = kl_data.lst[-1]
                    if hasattr(last_klc, 'lst') and last_klc.lst and len(last_klc.lst) > 0:
                        last_close = last_klc.lst[-1].close
                        mid_price = (last_zs.high + last_zs.low) / 2
                        if last_close > last_zs.high:
                            position = "中枢上方（强势）"
                        elif last_close < last_zs.low:
                            position = "中枢下方（弱势）"
                        elif last_close > mid_price:
                            position = "中枢上半部分"
                        else:
                            position = "中枢下半部分"
                        result += f"\n当前价格: {last_close:.2f}, 相对中枢位置: {position}\n\n"
            except:
                pass
        else:
            result += "- 暂无中枢\n\n"
    except Exception as e:
        result += f"- 获取中枢信息失败: {e}\n\n"

    # 5. 买卖点信息
    result += "### 买卖点信号\n"
    try:
        bsp_list = chan.get_latest_bsp(number=5)
        if bsp_list and len(bsp_list) > 0:
            for bsp in bsp_list:
                try:
                    action = "买入" if bsp.is_buy else "卖出"
                    types = ", ".join([t.value for t in bsp.type])
                    time_str = str(bsp.klu.time) if bsp.klu else "未知"
                    price = bsp.klu.close if bsp.klu else 0
                    result += f"- {action}信号: 类型={types}, 时间={time_str}, 价格={price:.2f}\n"
                except:
                    result += "- 买卖点信息获取失败\n"
        else:
            result += "- 暂无买卖点信号\n"
    except Exception as e:
        result += f"- 获取买卖点信息失败: {e}\n"

    # 6. 成交量分析
    result += "\n### 成交量分析\n"
    try:
        # 收集所有K线的成交量
        volumes = []
        closes = []
        # kl_data.lst 是 CKLine 列表，每个 CKLine.lst 包含 1 个 CKLine_Unit
        for klc in kl_data.lst:
            if hasattr(klc, 'lst') and klc.lst and len(klc.lst) > 0:
                klu = klc.lst[0]  # 取第一个（也是唯一一个）K线单元
                if hasattr(klu, 'trade_info') and klu.trade_info:
                    # 成交量在 trade_info.metric['volume'] 中
                    metric = getattr(klu.trade_info, 'metric', {})
                    if metric and 'volume' in metric:
                        vol = metric['volume']
                        if vol is not None:
                            volumes.append(vol)
                            closes.append(klu.close)

        if volumes and len(volumes) >= 5:
            # 最近5根K线成交量
            recent_volumes = volumes[-5:]
            recent_closes = closes[-5:]

            # 当前成交量
            current_vol = recent_volumes[-1]
            avg_vol = sum(recent_volumes) / len(recent_volumes)

            # 成交量变化判断
            if current_vol > avg_vol * 1.5:
                vol_status = "放量（>1.5倍均量）"
            elif current_vol < avg_vol * 0.5:
                vol_status = "缩量（<0.5倍均量）"
            else:
                vol_status = "正常"

            result += f"- 当前成交量: {current_vol:.2f}\n"
            result += f"- 5周期均量: {avg_vol:.2f}\n"
            result += f"- 量能状态: {vol_status}\n"

            # 最近5根K线的量价关系
            result += "- 最近5根K线量价:\n"
            for i in range(len(recent_volumes)):
                vol = recent_volumes[i]
                close = recent_closes[i]
                if i > 0:
                    price_change = "涨" if close > recent_closes[i-1] else "跌"
                    vol_change = "放量" if vol > recent_volumes[i-1] else "缩量"
                    result += f"  K{i}: 价格{price_change}, {vol_change}\n"

            # 量价配合判断
            if len(recent_volumes) >= 2:
                last_up = recent_closes[-1] > recent_closes[-2]
                last_vol_up = recent_volumes[-1] > recent_volumes[-2]

                if last_up and last_vol_up:
                    result += "- 量价配合: 价涨量增（健康上涨）\n"
                elif last_up and not last_vol_up:
                    result += "- 量价配合: 价涨量缩（上涨乏力）\n"
                elif not last_up and last_vol_up:
                    result += "- 量价配合: 价跌量增（抛压大）\n"
                else:
                    result += "- 量价配合: 价跌量缩（下跌缩量）\n"

        else:
            result += "- 暂无成交量数据\n"
    except Exception as e:
        result += f"- 获取成交量信息失败: {e}\n"

    return result


def format_full_report(results: List[str]) -> str:
    """
    将多个分析结果合并为完整报告

    Args:
        results: 各周期分析结果列表

    Returns:
        完整的分析报告
    """
    header = """# 缠论分析报告

以下是基于缠论理论对加密货币市场的技术分析结果。
数据来源：Binance 现货市场
分析工具：缠论（笔、线段、中枢、买卖点、MACD）

---

"""
    return header + "\n---\n".join(results)
