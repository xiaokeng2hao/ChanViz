"""
图表数据处理模块

此模块负责将原始数据转换为前端图表格式的转换，将app.py中的数据处理逻辑抽取出来
"""
import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from czsc import CZSC
from czsc.objects import RawBar, ZS

class ChartDataProcessor:
    """
    图表数据处理器
    将缠论分析结果转换为前端可用的格式
    """
    
    @staticmethod
    def to_timestamp(dt_obj):
        """将各种日期格式转换为时间戳
        
        Args:
            dt_obj: 日期对象或字符串
            
        Returns:
            float: 时间戳
        """
        if hasattr(dt_obj, 'timestamp'):
            return dt_obj.timestamp()
        elif isinstance(dt_obj, str):
            try:
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        return datetime.datetime.strptime(dt_obj, fmt).timestamp()
                    except ValueError:
                        continue
                # 如果都失败，返回一个基于字符串顺序的数字
                return hash(dt_obj) % (10**10)
            except Exception:
                return 0
        return 0
    
    @staticmethod
    def process_k_line_data(bars: List[RawBar]) -> List[Dict[str, Any]]:
        """将K线数据转换为前端格式
        
        Args:
            bars: 带有指标的K线数据列表
            
        Returns:
            List[Dict]: 处理后的K线数据列表
        """
        bars_data = []
        for bar in bars:
            bar_data = {
                'dt': bar.dt.strftime('%Y-%m-%d %H:%M') if hasattr(bar.dt, 'strftime') else str(bar.dt),
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'vol': bar.vol,
                'amount': bar.amount,
                'indicators': {}
            }
            
            # 添加指标数据
            if hasattr(bar, 'indicators'):
                # 添加MACD
                if 'macd' in bar.indicators:
                    bar_data['indicators']['macd'] = bar.indicators['macd']
                
                # 添加布林带
                if 'boll' in bar.indicators:
                    bar_data['indicators']['boll'] = bar.indicators['boll']
            
            bars_data.append(bar_data)
        
        return bars_data
    
    @staticmethod
    def process_bi_data(czsc_obj: CZSC, bars: List[RawBar]) -> List[Dict[str, Any]]:
        """处理笔数据
        
        Args:
            czsc_obj: 缠论分析对象
            bars: 原始K线数据
            
        Returns:
            List[Dict]: 处理后的笔数据列表
        """
        bi_list_data = []
        
        for bi in czsc_obj.bi_list:
            # 找出笔覆盖的K线
            start_time = ChartDataProcessor.to_timestamp(bi.fx_a.dt)
            end_time = ChartDataProcessor.to_timestamp(bi.fx_b.dt)
            bars_in_bi = [bar for bar in bars 
                         if ChartDataProcessor.to_timestamp(bar.dt) >= start_time and ChartDataProcessor.to_timestamp(bar.dt) <= end_time]
            
            # 根据笔的方向计算MACD面积
            macd_area = 0
            direction = bi.direction.value if hasattr(bi.direction, 'value') else str(bi.direction)
            is_up_bi = direction == 'Up' or direction == 'up'
            
            for bar in bars_in_bi:
                if hasattr(bar, 'indicators') and 'macd' in bar.indicators:
                    hist_value = bar.indicators['macd']['histogram']
                    # 对向上笔，只计算0轴以上的面积
                    if is_up_bi and hist_value > 0:
                        macd_area += hist_value
                    # 对向下笔，只计算0轴以下的面积（取绝对值累加）
                    elif not is_up_bi and hist_value < 0:
                        macd_area += abs(hist_value)
            
            # 将MACD面积放大1000倍并取整，使其成为整数
            macd_area = int(round(macd_area * 1000))
            
            bi_list_data.append({
                'fx_a': {
                    'dt': bi.fx_a.dt.strftime('%Y-%m-%d %H:%M') if hasattr(bi.fx_a.dt, 'strftime') else str(bi.fx_a.dt),
                    'fx': bi.fx_a.fx,
                    'mark': bi.fx_a.mark.value if hasattr(bi.fx_a.mark, 'value') else str(bi.fx_a.mark)
                },
                'fx_b': {
                    'dt': bi.fx_b.dt.strftime('%Y-%m-%d %H:%M') if hasattr(bi.fx_b.dt, 'strftime') else str(bi.fx_b.dt),
                    'fx': bi.fx_b.fx,
                    'mark': bi.fx_b.mark.value if hasattr(bi.fx_b.mark, 'value') else str(bi.fx_b.mark)
                },
                'direction': direction,
                'macd_area': macd_area  # 已经是整数，不需要保留小数位
            })
        
        return bi_list_data

    @staticmethod
    def process_fx_data(czsc_obj: CZSC) -> List[Dict[str, Any]]:
        """处理分型数据
        
        Args:
            czsc_obj: 缠论分析对象
            
        Returns:
            List[Dict]: 处理后的分型数据列表
        """
        fx_list_data = []
        
        for fx in czsc_obj.fx_list:
            fx_list_data.append({
                'dt': fx.dt.strftime('%Y-%m-%d %H:%M') if hasattr(fx.dt, 'strftime') else str(fx.dt),
                'fx': fx.fx,
                'mark': fx.mark.value if hasattr(fx.mark, 'value') else str(fx.mark)
            })
        
        return fx_list_data
    
    @staticmethod
    def process_zs_data(czsc_obj: CZSC) -> List[Dict[str, Any]]:
        """处理中枢数据
        
        Args:
            czsc_obj: 缠论分析对象
            
        Returns:
            List[Dict]: 处理后的中枢数据列表
        """
        raw_zs_list = []  # 存储所有中枢，稍后过滤
        
        for i in range(len(czsc_obj.bi_list) - 4):  # 至少需要5笔形成中枢
            segment = czsc_obj.bi_list[i:i+5]
            zs = ZS(segment)
            
            if zs.is_valid:
                # 准备好日期字符串
                start_dt_str = zs.sdt.strftime('%Y-%m-%d %H:%M') if hasattr(zs.sdt, 'strftime') else str(zs.sdt)
                end_dt_str = zs.edt.strftime('%Y-%m-%d %H:%M') if hasattr(zs.edt, 'strftime') else str(zs.edt)
                
                # 计算时间戳
                start_timestamp = ChartDataProcessor.to_timestamp(zs.sdt)
                end_timestamp = ChartDataProcessor.to_timestamp(zs.edt)
                
                raw_zs_list.append({
                    'start_dt': start_dt_str,
                    'end_dt': end_dt_str,
                    'start_time': start_timestamp,  # 用于排序和比较
                    'end_time': end_timestamp,      # 用于排序和比较
                    'zg': zs.zg,  # 中枢上沿
                    'zd': zs.zd,  # 中枢下沿
                    'zz': zs.zz   # 中枢中轴
                })
        
        # 过滤重叠中枢
        # 1. 按开始时间排序
        raw_zs_list.sort(key=lambda x: x['start_time'])
        
        # 2. 过滤重叠的中枢
        filtered_zs_list = []
        for zs in raw_zs_list:
            # 检查当前中枢是否与已保留的中枢重叠
            overlapped = False
            for kept_zs in filtered_zs_list:
                # 检查是否有时间重叠
                if not (zs['end_time'] < kept_zs['start_time'] or zs['start_time'] > kept_zs['end_time']):
                    overlapped = True
                    logger.debug(f"中枢重叠，丢弃: {zs['start_dt']} 到 {zs['end_dt']}")
                    break
            
            # 如果没有重叠，则保留此中枢
            if not overlapped:
                filtered_zs_list.append(zs)
        
        # 清理临时字段并构建最终中枢列表
        zs_list_data = []
        for zs in filtered_zs_list:
            zs_data = {k: v for k, v in zs.items() if k not in ['start_time', 'end_time']}
            zs_list_data.append(zs_data)
        
        logger.debug(f"中枢处理: 共发现 {len(raw_zs_list)} 个中枢，过滤后保留 {len(zs_list_data)} 个")
        return zs_list_data
    
    @staticmethod
    def process_all_data(czsc_obj: Optional[CZSC], bars: List[RawBar], stock_code: str, kline_type: str) -> Dict[str, Any]:
        """处理所有数据
        
        Args:
            czsc_obj: 缠论分析对象
            bars: 带有指标的K线数据列表
            stock_code: 股票代码
            kline_type: K线类型
            
        Returns:
            Dict: 包含所有图表数据的字典
        """
        # 处理K线数据
        bars_data = ChartDataProcessor.process_k_line_data(bars)
        
        # 初始化其他数据
        bi_list_data = []
        fx_list_data = []
        zs_list_data = []
        
        # 如果有缠论分析对象，处理其他数据
        if czsc_obj:
            bi_list_data = ChartDataProcessor.process_bi_data(czsc_obj, bars)
            fx_list_data = ChartDataProcessor.process_fx_data(czsc_obj)
            zs_list_data = ChartDataProcessor.process_zs_data(czsc_obj)
        
        # 构建结果
        return {
            'stock_code': stock_code,
            'kline_type': kline_type,
            'bars': bars_data,
            'bi_list': bi_list_data,
            'fx_list': fx_list_data,
            'zs_list': zs_list_data
        } 