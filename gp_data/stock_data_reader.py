import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple

class StockDataReader:
    """股票数据读取类，用于读取和处理CSV文件夹中的股票数据"""
    
    # K线类型常量
    KLINE_TYPES = {
        '1分': '1分K线.csv',
        '5分': '5分K线.csv',
        '15分': '15分K线.csv',
        '30分': '30分K线.csv',
        '时': '时K线.csv',
        '日': '日K线.csv',
        '周': '周K线.csv',
        '月': '月K线.csv',
        '季': '季K线.csv',
        '年': '年K线.csv'
    }
    
    def __init__(self, base_dir: str = 'csv'):
        """
        初始化股票数据读取器
        
        Args:
            base_dir: CSV文件的基础目录，默认为'csv'
        """
        self.base_dir = base_dir
        self.stock_codes = self._get_available_stock_codes()
        
    def _get_available_stock_codes(self) -> List[str]:
        """
        获取可用的股票代码列表
        
        Returns:
            股票代码列表
        """
        if not os.path.exists(self.base_dir):
            return []
        
        return [d for d in os.listdir(self.base_dir) 
                if os.path.isdir(os.path.join(self.base_dir, d))]
    
    def get_stock_data(self, 
                      stock_code: str, 
                      kline_type: str = '日',
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取指定股票的K线数据
        
        Args:
            stock_code: 股票代码，如'sh600000'
            kline_type: K线类型，可选值为'1分', '5分', '15分', '30分', '时', '日', '周', '月', '季', '年'
            start_date: 开始日期，格式为'YYYY-MM-DD'，如'2020-01-01'
            end_date: 结束日期，格式为'YYYY-MM-DD'，如'2020-12-31'
            
        Returns:
            包含股票数据的DataFrame
        
        Raises:
            ValueError: 如果股票代码不存在或K线类型无效
        """
        if stock_code not in self.stock_codes:
            raise ValueError(f"股票代码 '{stock_code}' 不存在")
        
        if kline_type not in self.KLINE_TYPES:
            raise ValueError(f"无效的K线类型 '{kline_type}'，可用类型: {list(self.KLINE_TYPES.keys())}")
        
        file_path = os.path.join(self.base_dir, stock_code, self.KLINE_TYPES[kline_type])
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 将日期列转换为datetime类型
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 按日期筛选数据
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['日期'] >= start_date]
            
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['日期'] <= end_date]
        
        return df
    
    def get_latest_data(self, stock_code: str, kline_type: str = '日', n: int = 1) -> pd.DataFrame:
        """
        获取最新的n条K线数据
        
        Args:
            stock_code: 股票代码
            kline_type: K线类型
            n: 获取的记录数量
            
        Returns:
            包含最新n条数据的DataFrame
        """
        df = self.get_stock_data(stock_code, kline_type)
        return df.sort_values('日期', ascending=False).head(n)
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """
        获取股票的基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            包含股票信息的字典
        """
        if stock_code not in self.stock_codes:
            raise ValueError(f"股票代码 '{stock_code}' 不存在")
        
        # 获取日K线数据的最新一条记录
        latest_data = self.get_latest_data(stock_code, '日', 1)
        
        if latest_data.empty:
            return {'code': stock_code, 'name': '未知', 'last_update': None}
        
        return {
            'code': stock_code,
            'name': latest_data['名称'].iloc[0],
            'last_price': latest_data['现收'].iloc[0],
            'last_update': latest_data['日期'].iloc[0].strftime('%Y-%m-%d'),
            'change_percent': latest_data['涨幅比'].iloc[0]
        }
    
    def get_available_kline_types(self, stock_code: str) -> List[str]:
        """
        获取指定股票可用的K线类型
        
        Args:
            stock_code: 股票代码
            
        Returns:
            可用的K线类型列表
        """
        if stock_code not in self.stock_codes:
            raise ValueError(f"股票代码 '{stock_code}' 不存在")
        
        stock_dir = os.path.join(self.base_dir, stock_code)
        available_files = os.listdir(stock_dir)
        
        available_types = []
        for k_type, file_name in self.KLINE_TYPES.items():
            if file_name in available_files:
                available_types.append(k_type)
                
        return available_types
    
    def calculate_ma(self, 
                    stock_code: str, 
                    kline_type: str = '日', 
                    ma_periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        计算移动平均线
        
        Args:
            stock_code: 股票代码
            kline_type: K线类型
            ma_periods: 移动平均周期列表
            
        Returns:
            包含原始数据和移动平均线的DataFrame
        """
        df = self.get_stock_data(stock_code, kline_type)
        
        # 计算各周期的移动平均线
        for period in ma_periods:
            df[f'MA{period}'] = df['现收'].rolling(window=period).mean()
            
        return df
    
    def get_all_stocks_latest_data(self, kline_type: str = '日') -> pd.DataFrame:
        """
        获取所有股票的最新数据
        
        Args:
            kline_type: K线类型
            
        Returns:
            包含所有股票最新数据的DataFrame
        """
        all_data = []
        
        for stock_code in self.stock_codes:
            try:
                latest = self.get_latest_data(stock_code, kline_type, 1)
                if not latest.empty:
                    all_data.append(latest)
            except Exception as e:
                print(f"获取 {stock_code} 数据时出错: {e}")
                
        if not all_data:
            return pd.DataFrame()
            
        return pd.concat(all_data, ignore_index=True) 