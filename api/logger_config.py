"""
日志配置模块

此模块负责配置和管理应用程序的日志系统
"""
import os
import sys
import builtins
from loguru import logger

class LoggerConfig:
    """
    日志配置管理器
    配置和管理应用程序的日志记录
    """
    
    @staticmethod
    def setup_logging(log_dir="logs"):
        """
        设置日志系统
        
        Args:
            log_dir: 日志文件存储目录
        """
        # 设置czsc库的专用环境变量，禁用详细日志输出
        os.environ["czsc_verbose"] = "0"  # 禁用czsc的详细日志

        # 设置环境变量，控制czsc库的日志级别
        os.environ["LOGURU_LEVEL"] = "WARNING"  # 将czsc库的日志级别设置为WARNING，抑制INFO日志

        # 移除所有默认处理器，防止重复日志
        logger.remove()

        # 添加控制台输出，方便实时查看，但排除czsc相关日志
        logger.add(
            sys.stderr, 
            level="INFO",
            filter=lambda record: "czsc" not in record["name"] and record["level"].name != "PRINT"
        )

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 添加文件输出，用于详细调试
        log_file_path = os.path.join(log_dir, "runtime.log") # 所有日志写入 runtime.log
        # 注意：设置 level="DEBUG" 以捕获所有级别的日志
        logger.add(log_file_path, rotation="1 day", encoding="utf-8", level="DEBUG")

        # 为czsc库创建单独的日志文件
        czsc_log_path = os.path.join(log_dir, "czsc.log")
        logger.add(
            czsc_log_path,
            rotation="1 day",
            encoding="utf-8",
            level="WARNING",  # 只记录WARNING及以上级别的czsc日志
            filter=lambda record: "czsc" in record["name"]
        )

        # 确保print语句能够正常输出到控制台
        LoggerConfig._setup_print_override()

        logger.info("日志系统初始化完成")
        logger.info("czsc模块的INFO级别日志已被抑制，只记录WARNING及以上级别")
        logger.info("print语句输出已启用")
    
    @staticmethod
    def _setup_print_override():
        """设置print函数重载，确保正常输出到控制台"""
        original_print = builtins.print

        def print_override(*args, **kwargs):
            # 调用原始的print函数确保输出到控制台
            original_print(*args, **kwargs)

        # 替换内置print函数
        builtins.print = print_override
    
    @staticmethod
    def suppress_czsc_logs():
        """禁用czsc库的详细日志输出"""
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
        
        logger.info("已禁用czsc库的详细日志输出") 