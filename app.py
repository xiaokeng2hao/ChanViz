import os
from flask import Flask, render_template, jsonify, request
from loguru import logger
from api.data_service import get_stock_data, analyze_stock_data
from api.indicators import TechnicalIndicators
from api.test_framework import TestFramework
from api.logger_config import LoggerConfig
from api.chart_processor import ChartDataProcessor
from api.test_manager import TestManager

# 初始化日志系统
LoggerConfig.setup_logging()
LoggerConfig.suppress_czsc_logs()

# 导入默认测试类
try:
    from test import MyTest
    # 设置默认使用的测试类
    TestManager.set_default_test_class(MyTest)
except ImportError as e:
    logger.warning(f"无法导入默认测试类: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    """主页路由"""
    # 获取URL参数，如果没有则使用默认值
    stock_code = request.args.get('code', 'sh600000')
    kline_type = request.args.get('freq', '30分')
    limit = request.args.get('limit', '1000')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 1000
    
    return render_template('index.html', 
                         stock_code=stock_code, 
                         kline_type=kline_type, 
                         limit=limit)

@app.route('/api/kline')
def get_kline_data():
    """K线数据API"""
    # 获取请求参数
    stock_code = request.args.get('code', 'sh600000')
    kline_type = request.args.get('freq', '日')
    limit = request.args.get('limit', '1000')
    test_class = request.args.get('test_class', None)
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 1000
        
    # 获取和处理股票数据
    try:
        # 1. 获取原始K线数据
        bars = get_stock_data(stock_code, kline_type, limit)
        
        # 2. 添加技术指标数据 (MACD和布林带)
        bars_with_indicators = TechnicalIndicators.enrich_with_indicators(bars)
        
        # 3. 进行缠论分析
        czsc_obj = analyze_stock_data(bars_with_indicators)
        
        # 4. 将数据转换为前端可用的JSON格式
        chart_data = ChartDataProcessor.process_all_data(
            czsc_obj=czsc_obj,
            bars=bars_with_indicators,
            stock_code=stock_code,
            kline_type=kline_type
        )
        
        # 5. 创建响应
        response = {
            'success': True,
            'data': chart_data
        }
        
        # 6. 应用测试类处理数据
        response = TestManager.apply_test_class(response, test_class)
        
        # 7. 记录统计信息
        logger.debug(f"返回数据: {len(response['data']['bars'])}根K线, {len(response['data']['bi_list'])}笔, {len(response['data']['fx_list'])}个分型, {len(response['data']['zs_list'])}个中枢")
        logger.debug(f"技术指标: MACD和布林带已计算完成")
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        logger.error(f"API错误: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    try:
        logger.info("正在启动Flask应用, 端口8000...")
        app.run(debug=True, port=8000)
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc()) 