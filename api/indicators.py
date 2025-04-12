import numpy as np
import pandas as pd
from loguru import logger

class TechnicalIndicators:
    """技术指标计算类
    
    为K线数据计算各种技术指标，包括MACD和布林带
    """
    
    @staticmethod
    def calculate_macd(close_prices, fast_period=12, slow_period=26, signal_period=9):
        """计算MACD指标
        
        Args:
            close_prices: 收盘价序列
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9
            
        Returns:
            dict: 包含DIF(差离值)、DEA(信号线)和HISTOGRAM(柱状图)的字典
        """
        try:
            # 确保输入是浮点数序列
            close_prices = np.array(close_prices, dtype=float)
            
            # 计算指数移动平均线(EMA)
            def ema(prices, period):
                return pd.Series(prices).ewm(span=period, adjust=False).mean().values
            
            # 计算快线和慢线
            fast_ema = ema(close_prices, fast_period)
            slow_ema = ema(close_prices, slow_period)
            
            # 计算DIF, DEA和直方图
            dif = fast_ema - slow_ema
            dea = ema(dif, signal_period)
            histogram = dif - dea
            
            # 构造结果
            result = {
                "dif": dif.tolist(),
                "dea": dea.tolist(),
                "histogram": histogram.tolist()
            }
            
            return result
        except Exception as e:
            logger.error(f"计算MACD时出错: {e}")
            # 返回空值
            return {
                "dif": [0] * len(close_prices),
                "dea": [0] * len(close_prices),
                "histogram": [0] * len(close_prices)
            }
    
    @staticmethod
    def calculate_bollinger_bands(close_prices, period=20, num_std_dev=2):
        """计算布林带指标
        
        Args:
            close_prices: 收盘价序列
            period: 周期，默认20
            num_std_dev: 标准差倍数，默认2
            
        Returns:
            dict: 包含上轨(upper)、中轨(middle)和下轨(lower)的字典
        """
        try:
            # 确保输入是浮点数序列
            close_prices = np.array(close_prices, dtype=float)
            
            # 使用pandas计算移动平均和标准差
            df = pd.DataFrame({'close': close_prices})
            
            # 计算中轨(SMA)
            df['middle'] = df['close'].rolling(window=period).mean()
            
            # 计算标准差
            df['std'] = df['close'].rolling(window=period).std()
            
            # 计算上轨和下轨
            df['upper'] = df['middle'] + (df['std'] * num_std_dev)
            df['lower'] = df['middle'] - (df['std'] * num_std_dev)
            
            # 处理前period-1个值为NaN的情况
            df.fillna(method='bfill', inplace=True)  # 使用后面的值填充NaN
            
            # 构造结果
            result = {
                "upper": df['upper'].tolist(),
                "middle": df['middle'].tolist(),
                "lower": df['lower'].tolist()
            }
            
            return result
        except Exception as e:
            logger.error(f"计算布林带时出错: {e}")
            # 返回简单的默认值
            return {
                "upper": close_prices * 1.05,  # 上轨默认为收盘价的1.05倍
                "middle": close_prices,        # 中轨默认为收盘价
                "lower": close_prices * 0.95   # 下轨默认为收盘价的0.95倍
            }
    
    @staticmethod
    def enrich_with_indicators(bars):
        """为K线数据添加技术指标
        
        Args:
            bars: K线数据列表，每个元素应该包含open, high, low, close等属性
            
        Returns:
            list: 添加了指标数据的K线列表
        """
        try:
            # 提取收盘价序列
            close_prices = [bar.close for bar in bars]
            
            # 计算MACD
            macd_data = TechnicalIndicators.calculate_macd(close_prices)
            
            # 计算布林带
            boll_data = TechnicalIndicators.calculate_bollinger_bands(close_prices)
            
            # 将指标添加到每个K线对象中
            for i, bar in enumerate(bars):
                # 确保indicators属性存在
                if not hasattr(bar, 'indicators'):
                    bar.indicators = {}
                
                # 添加MACD数据
                bar.indicators['macd'] = {
                    'dif': macd_data['dif'][i],
                    'dea': macd_data['dea'][i],
                    'histogram': macd_data['histogram'][i]
                }
                
                # 添加布林带数据
                bar.indicators['boll'] = {
                    'upper': boll_data['upper'][i],
                    'middle': boll_data['middle'][i],
                    'lower': boll_data['lower'][i]
                }
            
            return bars
        except Exception as e:
            logger.error(f"添加技术指标时出错: {e}")
            return bars  # 返回原始数据，不做修改 