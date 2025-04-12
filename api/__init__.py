"""
API模块包
含有数据处理、图表处理、测试框架等功能
"""

from api.data_service import get_stock_data, analyze_stock_data
from api.indicators import TechnicalIndicators
from api.test_framework import TestFramework
from api.chart_processor import ChartDataProcessor
from api.test_manager import TestManager
from api.logger_config import LoggerConfig

__all__ = [
    'get_stock_data', 
    'analyze_stock_data',
    'TechnicalIndicators',
    'TestFramework',
    'ChartDataProcessor',
    'TestManager',
    'LoggerConfig'
]

# API模块初始化文件
import os

# 确保日志目录存在
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True) 