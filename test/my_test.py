from api.test_framework import TestFramework
from datetime import datetime

class MyTest(TestFramework):
    """
    自定义测试类
    
    通过继承TestFramework并重写需要的方法，可以方便地查看和修改数据
    """
    
    @classmethod
    def process_single_bar(cls, bar):
        """
        处理单个K线数据
        修改这个方法可以查看或修改每根K线的内容
        """
        try:
            # 查看K线数据
            # print(f"K线数据: {bar['dt']} 收盘价: {bar['close']}")
            
            # 查看K线的技术指标数据
            if 'indicators' in bar and bar['indicators']:
                # 查看MACD指标
                if 'macd' in bar['indicators']:
                    macd = bar['indicators']['macd']
                    print(f"K线 {bar.get('dt', '未知日期')} MACD: ", end="")
                    if 'dif' in macd:
                        print(f"DIF={macd['dif']}", end=", ")
                    if 'dea' in macd:
                        print(f"DEA={macd['dea']}", end=", ")
                    if 'histogram' in macd:
                        print(f"HIST={macd['histogram']}", end="")
                    print("") # 换行
                
                # 查看布林带指标
                if 'boll' in bar['indicators']:
                    boll = bar['indicators']['boll']
                    print(f"K线 {bar.get('dt', '未知日期')} 布林带: ", end="")
                    # 安全地访问布林带各数据
                    if 'upper' in boll:
                        print(f"UPPER={boll['upper']}", end=", ")
                    if 'mid' in boll:
                        print(f"MID={boll['mid']}", end=", ")
                    elif 'middle' in boll:
                        print(f"MIDDLE={boll['middle']}", end=", ")
                    if 'lower' in boll:
                        print(f"LOWER={boll['lower']}", end="")
                    print("") # 换行
                    
                    # 查看布林带完整数据结构以便调试
                    print(f"布林带完整数据: {boll}")
            
            # 修改数据 - 例如提高收盘价5%
            # if 'close' in bar:
            #     bar['close'] = round(bar['close'] * 1.05, 2)
            
            return bar
        except Exception as e:
            print(f"处理K线数据出错: {e}")
            return bar
    
    @classmethod
    def process_single_bar_marker(cls, bar):
        """
        为单个K线添加标记
        
        判断条件可以基于：
        1. 时间（特定日期）
        2. 价格（突破某个价位）
        3. 技术指标（金叉死叉等）
        4. 其他自定义条件
        
        返回标记数据
        """
        try:
            markers = []
            
            # 保存上一个K线的MACD值以便对比，使用静态变量
            if not hasattr(cls, '_last_macd'):
                cls._last_macd = {'dif': None, 'dea': None}
            
            # 示例1：MACD金叉死叉信号（真正的交叉判断）
            if 'indicators' in bar and 'macd' in bar['indicators']:
                macd = bar['indicators']['macd']
                if 'dif' in macd and 'dea' in macd:
                    current_dif = macd['dif']
                    current_dea = macd['dea']
                    
                    # 只有当有前一个值时才进行交叉判断
                    if cls._last_macd['dif'] is not None and cls._last_macd['dea'] is not None:
                        # 金叉：当前DIF在DEA上方，但前一K线DIF在DEA下方
                        if (current_dif > current_dea and cls._last_macd['dif'] <= cls._last_macd['dea']):
                            markers.append({
                                'dt': bar['dt'],  
                                'position': 'above',  # K线上方
                                'text': '金叉',
                                'color': '#FF0000',  # 红色
                                'offset': 5
                            })
                            
                        # 死叉：当前DIF在DEA下方，但前一K线DIF在DEA上方
                        elif (current_dif < current_dea and cls._last_macd['dif'] >= cls._last_macd['dea']):
                            markers.append({
                                'dt': bar['dt'],
                                'position': 'below',  # K线下方
                                'text': '死叉',
                                'color': '#00FF00',  # 绿色
                                'offset': 5
                            })
                    
                    # 更新最后的MACD值
                    cls._last_macd = {'dif': current_dif, 'dea': current_dea}
            
            # 示例2：价格突破布林带上轨
            if 'indicators' in bar and 'boll' in bar['indicators']:
                boll = bar['indicators']['boll']
                # 计算K线长度和半个K线长度
                k_line_length = bar['high'] - bar['low']
                half_k_line_length = k_line_length / 2
                
                # 上轨突破：高点超过上轨且突破距离大于等于半个K线长度
                if 'upper' in boll and bar['high'] > boll['upper'] and (bar['high'] - boll['upper']) >= half_k_line_length:
                    markers.append({
                        'dt': bar['dt'],
                        'position': 'above',
                        'text': '突破上轨',
                        'color': '#FF00FF',  # 紫色
                        'offset': 10
                    })
                    
                # 下轨突破：低点低于下轨且突破距离大于等于半个K线长度
                if 'lower' in boll and bar['low'] < boll['lower'] and (boll['lower'] - bar['low']) >= half_k_line_length:
                    markers.append({
                        'dt': bar['dt'],
                        'position': 'below',
                        'text': '突破下轨',
                        'color': '#0000FF',  # 蓝色
                        'offset': 10
                    })
            
            # 示例3：特定日期标记
            if isinstance(bar['dt'], str) and '2023-01-01' in bar['dt']:
                markers.append({
                    'dt': bar['dt'],
                    'position': 'above',
                    'text': '新年',
                    'color': '#FFA500',  # 橙色
                    'offset': 15
                })
            
            return markers if markers else None
            
        except Exception as e:
            print(f"处理K线标记出错: {e}")
            return None
    
    @classmethod
    def process_single_bi(cls, bi):
        """
        处理单个笔数据
        修改这个方法可以查看或修改每个笔的内容
        """
        try:
            # 安全地获取笔的起点和终点日期
            fx_a_dt = bi.get('fx_a', {}).get('dt', '未知')
            fx_b_dt = bi.get('fx_b', {}).get('dt', '未知')
            direction = bi.get('direction', '未知')
            
            # 查看笔数据
            print(f"笔: {fx_a_dt} -> {fx_b_dt}, 方向: {direction}")
            
            # 修改数据 - 例如增强MACD面积
            # if 'macd_area' in bi and (direction == 'Up' or direction == 'up'):
            #     bi['macd_area'] = int(bi['macd_area'] * 1.5)
            
            return bi
        except Exception as e:
            print(f"处理笔数据出错: {e}")
            return bi
    
    @classmethod
    def process_single_zs(cls, zs):
        """
        处理单个中枢数据
        修改这个方法可以查看或修改每个中枢的内容
        """
        try:
            # 安全地获取中枢数据
            start_dt = zs.get('start_dt', '未知')
            end_dt = zs.get('end_dt', '未知')
            zg = zs.get('zg', '未知')
            zz = zs.get('zz', '未知')
            zd = zs.get('zd', '未知')
            
            # 查看中枢数据
            print(f"中枢: {start_dt} -> {end_dt}, 上沿={zg}, 中轴={zz}, 下沿={zd}")
            
            # 修改数据 - 例如扩大中枢范围
            # if 'zg' in zs and 'zd' in zs:
            #     zs['zg'] = round(zs['zg'] * 1.02, 2)  # 上沿提高2%
            #     zs['zd'] = round(zs['zd'] * 0.98, 2)  # 下沿降低2%
            #     if 'zz' in zs:
            #         zs['zz'] = round((zs['zg'] + zs['zd']) / 2, 2)  # 重新计算中轴
            
            return zs
        except Exception as e:
            print(f"处理中枢数据出错: {e}")
            return zs
    
    @classmethod
    def process_fx_list(cls, fx_list):
        """
        处理分型列表
        修改这个方法可以查看或修改分型列表
        """
        try:
            # 打印分型数量
            print(f"共有 {len(fx_list)} 个分型")
            
            # 查看前几个分型
            for i, fx in enumerate(fx_list[:5]):
                dt = fx.get('dt', '未知')
                mark = fx.get('mark', '未知')
                price = fx.get('fx', '未知')
                print(f"分型{i+1}: 时间={dt}, 类型={mark}, 价格={price}")
                
            return fx_list
        except Exception as e:
            print(f"处理分型列表出错: {e}")
            return fx_list 