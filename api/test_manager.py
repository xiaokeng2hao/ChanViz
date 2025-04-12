"""
测试类管理模块

此模块负责加载和管理测试类，用于处理和修改数据
"""
import sys
from typing import Dict, Any, Optional, Type
from loguru import logger
from api.test_framework import TestFramework

class TestManager:
    """
    测试类管理器
    负责动态加载测试类并应用于数据处理
    """
    
    # 默认测试类，在初始化时设置
    DEFAULT_TEST_CLASS: Optional[Type[TestFramework]] = None
    
    @classmethod
    def set_default_test_class(cls, test_class: Type[TestFramework]) -> None:
        """
        设置默认测试类
        
        Args:
            test_class: 要设置为默认的测试类
        """
        cls.DEFAULT_TEST_CLASS = test_class
        logger.info(f"已设置默认测试类: {test_class.__name__}")
    
    @classmethod
    def load_test_class(cls, test_class_path: Optional[str] = None) -> Optional[Type[TestFramework]]:
        """
        根据类路径动态加载测试类
        
        Args:
            test_class_path: 测试类的导入路径，如 'test.MyTest'
            
        Returns:
            Optional[Type[TestFramework]]: 加载的测试类或None
        """
        # 如果未指定类路径，使用默认测试类
        if not test_class_path:
            return cls.DEFAULT_TEST_CLASS
        
        try:
            # 解析模块路径和类名
            module_path, class_name = test_class_path.rsplit('.', 1)
            
            # 动态导入模块
            test_module = __import__(module_path, fromlist=[class_name])
            
            # 获取类对象
            test_class_obj = getattr(test_module, class_name)
            
            # 检查是否是TestFramework的子类
            if not issubclass(test_class_obj, TestFramework):
                logger.warning(f"指定的类 {test_class_path} 不是TestFramework的子类，将使用默认测试类")
                return cls.DEFAULT_TEST_CLASS
            
            logger.info(f"成功加载测试类: {test_class_path}")
            return test_class_obj
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"加载测试类 {test_class_path} 失败: {str(e)}")
            return cls.DEFAULT_TEST_CLASS
    
    @classmethod
    def apply_test_class(cls, data: Dict[str, Any], test_class_path: Optional[str] = None) -> Dict[str, Any]:
        """
        应用测试类处理数据
        
        Args:
            data: 要处理的数据
            test_class_path: 测试类的导入路径
            
        Returns:
            Dict[str, Any]: 处理后的数据
        """
        # 加载测试类
        test_class_obj = cls.load_test_class(test_class_path)
        
        if test_class_obj is not None:
            test_class_name = test_class_obj.__name__
            print(f"开始应用测试类 {test_class_name} 处理数据...")
            sys.stderr.write(f"stderr: 开始应用测试类 {test_class_name} 处理数据...\n")
            sys.stderr.flush()
            
            # 应用测试类处理数据
            response = test_class_obj.process_data(data)
            
            print(f"测试类 {test_class_name} 处理完成")
            sys.stderr.write(f"stderr: 测试类 {test_class_name} 处理完成\n")
            sys.stderr.flush()
            
            return response
        
        # 如果没有可用的测试类，直接返回原始数据
        return data 