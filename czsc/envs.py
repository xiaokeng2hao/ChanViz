# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2022/3/17 21:41
describe: 环境变量统一管理入口
"""

import os

# True 的有效表达
valid_true = ['1', 'True', 'true', 'Y', 'y', 'yes', 'Yes', True]


def get_verbose(verbose=None):
    """verbose - 是否输出执行过程的详细信息"""
    verbose = verbose if verbose else os.environ.get('czsc_verbose', None)
    v = True if verbose in valid_true else False
    return v


def get_welcome():
    """welcome - 是否输出版本标识和缠中说禅博客摘记"""
    v = True if os.environ.get('czsc_welcome', '0') in valid_true else False
    return v


def get_min_bi_len(v: int = None) -> int:
    """min_bi_len - 一笔的最小长度，也就是无包含K线的数量
    
    根据要求，这里固定返回5，确保笔由至少7根K线构成。
    (底分型 + 至少1根K线 + 顶分型)
    """
    # min_bi_len = v if v else os.environ.get('czsc_min_bi_len', 6)
    # return int(float(min_bi_len))
    return 7


def get_max_bi_num(v: int = None) -> int:
    """max_bi_num - 单个级别K线分析中，程序最大保存的笔数量

    默认值为 50，仅使用内置的信号和因子，不需要调整这个参数。
    如果进行新的信号计算需要用到更多的笔，可以适当调大这个参数。
    """
    max_bi_num = v if v else os.environ.get('czsc_max_bi_num', 50)
    return int(float(max_bi_num))
