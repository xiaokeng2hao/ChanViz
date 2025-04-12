from stock_data_reader import StockDataReader
import pandas as pd

def main():
    # 初始化股票数据读取器
    reader = StockDataReader()
    
    # 选择一个股票代码
    stock_code = 'sh600000'
    
    # 获取该股票可用的K线类型
    kline_types = reader.get_available_kline_types(stock_code)
    print(f"{stock_code} 可用的K线类型: {kline_types}")
    
    # 获取股票基本信息
    stock_info = reader.get_stock_info(stock_code)
    print(f"\n股票信息:")
    for key, value in stock_info.items():
        print(f"  {key}: {value}")
    
    # 获取最近30天的日K线数据
    daily_data = reader.get_stock_data(
        stock_code=stock_code,
        kline_type='日',
        start_date='2023-01-01',
        end_date='2025-03-31'
    )
    
    print(f"\n2020年1月日K线数据 (共{len(daily_data)}条记录):")
    print(daily_data)
 

if __name__ == "__main__":
    main() 