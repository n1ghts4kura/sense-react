#
# logger.py
#
# @author n1ghts4kura
# @date 2025/9/28
#

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Union


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColorFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
        'BOLD': '\033[1m',        # 粗体
        'DIM': '\033[2m'          # 暗色
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        bold = self.COLORS['BOLD']

        try:
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        except (ImportError, AttributeError):
            timestamp = "SHUTDOWN"

        module_name = getattr(record, 'module_name', record.name)
        log_message = (
            f"{timestamp} "
            f"{color}{bold}[{record.levelname}]{reset} "
            f"<{module_name}>: {record.getMessage()}"
        )

        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


class ModuleLogger:
    """带模块名前缀的轻量日志包装器"""

    def __init__(self, base_logger: logging.Logger, module_name: str):
        self._base_logger = base_logger
        self._extra = {'module_name': module_name}

    def debug(self, message: str, *args, **kwargs):
        self._base_logger.debug(message, *args, extra=self._extra, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._base_logger.info(message, *args, extra=self._extra, **kwargs)

    def warn(self, message: str, *args, **kwargs):
        self.warning(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._base_logger.warning(message, *args, extra=self._extra, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._base_logger.error(message, *args, extra=self._extra, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self._base_logger.critical(message, *args, extra=self._extra, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self._base_logger.exception(message, *args, extra=self._extra, **kwargs)


class Logger:
    """日志管理器类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = "FrameworkLogger", level: LogLevel = LogLevel.INFO, 
                 enable_color: bool = True):
        if self._initialized:
            return

        self.name = name
        self.level = level
        self.enable_color = enable_color

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)

        self.logger.handlers.clear()
        self.logger.propagate = False
        self._setup_console_handler()

        self._initialized = True
    
    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level.value)

        if self.enable_color:
            formatter = ColorFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] <%(module_name)s>: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def set_level(self, level: LogLevel):
        self.level = level
        self.logger.setLevel(level.value)

        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level.value)

    def make_logger(self, module_name: str) -> ModuleLogger:
        return ModuleLogger(self.logger, module_name)
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常日志（自动包含异常堆栈）"""
        self.logger.exception(message, *args, **kwargs)


# 创建全局日志器实例
logger = Logger(
    name="Framework",
    level=LogLevel.INFO,
    enable_color=True
)


def set_logging_level(level: Union[LogLevel, str, int]):
    """设置当前日志级别"""
    if isinstance(level, LogLevel):
        resolved_level = level
    elif isinstance(level, str):
        normalized_level = level.strip().upper()
        try:
            resolved_level = LogLevel[normalized_level]
        except KeyError as exc:
            raise ValueError(f"Unsupported log level: {level}") from exc
    elif isinstance(level, int):
        try:
            resolved_level = LogLevel(level)
        except ValueError as exc:
            raise ValueError(f"Unsupported log level: {level}") from exc
    else:
        raise TypeError("level must be LogLevel, str, or int")

    logger.set_level(resolved_level)


def get_logger() -> Logger:
    """获取日志器实例"""
    return logger


def make_logger(module_name: str) -> ModuleLogger:
    """创建带模块名标记的日志对象"""
    return logger.make_logger(module_name)


# 便捷函数
def debug(message: str, *args, **kwargs):
    """调试日志"""
    logger.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """信息日志"""
    logger.info(message, *args, **kwargs)


def warn(message: str, *args, **kwargs):
    """警告日志"""
    logger.warning(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """警告日志"""
    logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """错误日志"""
    logger.error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """严重错误日志"""
    logger.critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """异常日志"""
    logger.exception(message, *args, **kwargs)


__all__ = [
    "set_logging_level",
    "make_logger",
    "debug",
    "info",
    "warn",
    "warning",
    "error",
    "critical",
    "exception",
    "get_logger",
    "LogLevel",
]