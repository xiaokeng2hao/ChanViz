from typing import List, Optional
from czsc import RawBar, CZSC
from gp_data.stock_data_reader import StockDataReader
from loguru import logger
import os
import sys

# # 确保日志目录存在 (删除或注释掉)
# log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
# os.makedirs(log_dir, exist_ok=True)

# # 设置日志 (删除或注释掉)
# logger.remove()  # 移除默认处理器
# logger.add(
#     os.path.join(log_dir, "data_service.log"), 
#     rotation="1 day", 
#     encoding="utf-8", 
#     level="INFO"
# )
# logger.add(sys.stderr, level="INFO")  # 同时输出到控制台

# 禁用czsc库的日志输出
import logging
import czsc.analyze

# 保存原始的debug和info方法，以便在需要时可以恢复
original_debug = czsc.analyze.logger.debug
original_info = czsc.analyze.logger.info

# 创建空函数替换原始的debug和info方法
def no_op(*args, **kwargs):
    pass

# 替换czsc.analyze模块的logger的debug和info方法
czsc.analyze.logger.debug = no_op
czsc.analyze.logger.info = no_op

def get_stock_data(stock_code: str, kline_type: str = "日", limit: int = 1000) -> List[RawBar]:
    """获取股票数据
    
    Args:
        stock_code: 股票代码，如'sh600000'
        kline_type: K线类型，如"日"、"周"、"月"
        limit: 获取的K线数量，默认1000根
        
    Returns:
        List[RawBar]: 转换后的K线数据列表
    """
    try:
        logger.info(f"开始加载股票数据: {stock_code}, 级别: {kline_type}, 数量: {limit}")
        
        # 初始化数据读取器
        reader = StockDataReader(base_dir='gp_data/csv')
        
        # 加载数据
        df = reader.get_stock_data(
            stock_code=stock_code,
            kline_type=kline_type
        )
        
        logger.info(f"成功读取原始数据: {len(df)} 条记录")
        
        # 获取最新的limit条数据
        if len(df) > limit:
            df = df.tail(limit)
        
        # 将DataFrame转换为RawBar列表
        bars = []
        symbol = "600000.SH" if stock_code == "sh600000" else stock_code.upper()
        
        for idx, row in df.iterrows():
            try:
                bar = RawBar(
                    symbol=symbol,
                    dt=row['日期'],
                    open=float(row['今开']),
                    close=float(row['现收']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    vol=float(row['总手']),
                    amount=float(row['金额']) if '金额' in row else 0.0,
                    id=idx,
                    freq=kline_type_to_freq(kline_type)
                )
                bars.append(bar)
            except Exception as e:
                logger.error(f"处理行数据失败: {e}, 行: {row}")
        
        logger.info(f"成功转换 {len(bars)} 根K线数据")
        return bars
    except Exception as e:
        import traceback
        logger.error(f"加载数据失败: {e}")
        logger.error(traceback.format_exc())
        raise e

def analyze_stock_data(bars: List[RawBar]) -> Optional[CZSC]:
    """对K线数据进行缠中说禅分析
    
    Args:
        bars: RawBar列表
        
    Returns:
        CZSC: 分析结果对象
    """
    if not bars:
        logger.error("没有数据可供分析")
        return None

    try:
        logger.info(f"开始分析 {len(bars)} 根K线数据")
        
        # 创建CZSC对象 - 增加max_bi_num参数，不限制笔的数量
        czsc_obj = CZSC(bars, max_bi_num=1000000)  # 设置一个很大的值，实际上不限制笔的数量
        
        logger.info(f"分析成功: 共识别出 {len(czsc_obj.bi_list)} 笔")
        return czsc_obj
    except Exception as e:
        import traceback
        logger.error(f"分析失败: {e}")
        logger.error(traceback.format_exc())
        return None

def kline_type_to_freq(kline_type: str):
    """将K线类型转换为CZSC频率枚举"""
    from czsc import Freq
    
    kline_map = {
        "1分": Freq.F1,
        "5分": Freq.F5,
        "15分": Freq.F15,
        "30分": Freq.F30,
        "小时": Freq.F60,
        "时": Freq.F60,
        "日": Freq.D,
        "周": Freq.W,
        "月": Freq.M
    }
    
    # 如果未找到映射，返回日K默认值并记录警告
    if kline_type not in kline_map:
        logger.warning(f"未知的K线类型: {kline_type}，使用默认值: 日K")
        return Freq.D
    
    return kline_map.get(kline_type) 