class TestFramework:
    """
    测试框架基类，用于修改传递给前端的数据
    
    继承这个类并覆盖需要的方法来修改数据
    """
    
    @classmethod
    def process_data(cls, data):
        """
        处理完整的数据对象
        
        Args:
            data: 包含所有数据的字典，将发送给前端
        
        Returns:
            处理后的数据字典
        """
        if not data.get('success', False):
            return data
        
        result_data = data['data']
        
        # 处理K线数据
        if 'bars' in result_data:
            result_data['bars'] = cls.process_bars(result_data['bars'])
        
        # 处理笔数据
        if 'bi_list' in result_data:
            result_data['bi_list'] = cls.process_bi_list(result_data['bi_list'])
        
        # 处理分型数据
        if 'fx_list' in result_data:
            result_data['fx_list'] = cls.process_fx_list(result_data['fx_list'])
        
        # 处理中枢数据
        if 'zs_list' in result_data:
            result_data['zs_list'] = cls.process_zs_list(result_data['zs_list'])
        
        # 生成K线标记数据
        if 'bars' in result_data:
            result_data['bar_markers'] = cls.process_bar_markers(result_data['bars'])
        
        # 处理整体数据
        data['data'] = cls.process_result_data(result_data)
        
        return data
    
    @classmethod
    def process_bars(cls, bars):
        """
        处理K线数据
        
        Args:
            bars: K线数据列表
        
        Returns:
            处理后的K线数据列表
        """
        processed_bars = []
        for bar in bars:
            processed_bar = cls.process_single_bar(bar)
            processed_bars.append(processed_bar)
        return processed_bars
    
    @classmethod
    def process_single_bar(cls, bar):
        """
        处理单个K线数据
        
        Args:
            bar: 单个K线数据字典
        
        Returns:
            处理后的K线数据字典
        """
        # 可以修改价格、成交量等数据
        return bar
    
    @classmethod
    def process_bar_markers(cls, bars):
        """
        为K线添加标记数据
        
        Args:
            bars: K线数据列表
            
        Returns:
            标记数据列表，格式为：
            [
                {
                    'dt': '2023-01-01 10:00',  # 要标记的K线时间
                    'position': 'above',       # 标记位置，'above'表示K线上方，'below'表示K线下方
                    'text': '买入信号',        # 标记文本内容
                    'color': '#FF0000',        # 标记颜色，十六进制颜色代码
                    'offset': 5                # 标记偏移量，单位为像素
                },
                # 更多标记...
            ]
        """
        markers = []
        for bar in bars:
            marker = cls.process_single_bar_marker(bar)
            if marker:
                markers.extend(marker if isinstance(marker, list) else [marker])
        return markers
    
    @classmethod
    def process_single_bar_marker(cls, bar):
        """
        处理单个K线的标记
        
        Args:
            bar: 单个K线数据字典
            
        Returns:
            标记数据字典或列表或None。如果返回None则表示该K线不需要标记。
            标记数据字典格式为：
            {
                'dt': '2023-01-01 10:00',  # 要标记的K线时间
                'position': 'above',       # 标记位置，'above'表示K线上方，'below'表示K线下方
                'text': '买入信号',        # 标记文本内容
                'color': '#FF0000',        # 标记颜色，十六进制颜色代码
                'offset': 5                # 标记偏移量，单位为像素
            }
        """
        # 默认实现：不添加标记
        return None
    
    @classmethod
    def process_indicators(cls, indicators, bar_dt=None):
        """
        处理技术指标数据
        
        Args:
            indicators: 技术指标数据字典
            bar_dt: 对应K线的日期时间
        
        Returns:
            处理后的技术指标数据字典
        """
        return indicators
    
    @classmethod
    def process_bi_list(cls, bi_list):
        """
        处理笔数据列表
        
        Args:
            bi_list: 笔数据列表
        
        Returns:
            处理后的笔数据列表
        """
        processed_bi_list = []
        for bi in bi_list:
            processed_bi = cls.process_single_bi(bi)
            processed_bi_list.append(processed_bi)
        return processed_bi_list
    
    @classmethod
    def process_single_bi(cls, bi):
        """
        处理单个笔数据
        
        Args:
            bi: 单个笔数据字典
        
        Returns:
            处理后的笔数据字典
        """
        return bi
    
    @classmethod
    def process_fx_list(cls, fx_list):
        """
        处理分型数据列表
        
        Args:
            fx_list: 分型数据列表
        
        Returns:
            处理后的分型数据列表
        """
        processed_fx_list = []
        for fx in fx_list:
            processed_fx = cls.process_single_fx(fx)
            processed_fx_list.append(processed_fx)
        return processed_fx_list
    
    @classmethod
    def process_single_fx(cls, fx):
        """
        处理单个分型数据
        
        Args:
            fx: 单个分型数据字典
        
        Returns:
            处理后的分型数据字典
        """
        return fx
    
    @classmethod
    def process_zs_list(cls, zs_list):
        """
        处理中枢数据列表
        
        Args:
            zs_list: 中枢数据列表
        
        Returns:
            处理后的中枢数据列表
        """
        processed_zs_list = []
        for zs in zs_list:
            processed_zs = cls.process_single_zs(zs)
            processed_zs_list.append(processed_zs)
        return processed_zs_list
    
    @classmethod
    def process_single_zs(cls, zs):
        """
        处理单个中枢数据
        
        Args:
            zs: 单个中枢数据字典
        
        Returns:
            处理后的中枢数据字典
        """
        return zs
    
    @classmethod
    def process_result_data(cls, result_data):
        """
        处理整体结果数据
        
        Args:
            result_data: 整体结果数据字典
        
        Returns:
            处理后的整体结果数据字典
        """
        return result_data 