import logging
import os
import sys
from sys import exc_info


def get_frame(n):
    """Get the nth frame from the call stack."""
    if hasattr(sys, "_getframe"):
        return sys._getframe(n + 1)
    else:
        # Fallback method for systems where sys._getframe() is not available.
        try:
            raise Exception
        except Exception:
            return exc_info()[2].tb_frame.f_back


# 创建日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建控制台处理程序
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建颜色记录格式
log_format = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"

# 定义颜色
COLORS = {
    logging.DEBUG: "\033[94m",  # 蓝色
    logging.INFO: "\033[92m",  # 绿色
    logging.WARNING: "\033[93m",  # 黄色
    logging.ERROR: "\033[91m",  # 红色
    logging.CRITICAL: "\033[1;31;40m",  # 粉红色
}


# 添加颜色到格式化器
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        frame = get_frame(8)
        module_name = os.path.basename(frame.f_globals["__file__"])[:-3]
        record.name = f"\033[1;34;4;40m{module_name}\033[0m"  # Modify the color formatting for module name to blue
        levelname = record.levelname
        color = COLORS.get(record.levelno)
        if color:
            levelname_color = f"{color}{levelname}\033[0m"
            record.levelname = levelname_color
        return super().format(record)


# 使用带颜色的格式化器
colored_formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(colored_formatter)
# 将控制台处理程序添加到日志记录器
logger.addHandler(console_handler)
