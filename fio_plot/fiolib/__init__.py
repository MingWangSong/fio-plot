"""
fio-plot库包
提供FIO测试结果的图表生成功能
"""
import os

# 检查是否应该启用科学风格
ENABLE_SCIENCE_STYLE = os.environ.get('FIO_PLOT_NOSCISTYLE', '0') != '1'
COLOR_SCHEME = os.environ.get('FIO_PLOT_COLORSCHEME', 'science')

# 导入模块后应用样式设置
if ENABLE_SCIENCE_STYLE:
    try:
        from . import style_config
        style_config.apply_science_style()
        if COLOR_SCHEME in style_config.COLOR_SCHEMES:
            style_config.apply_color_scheme(COLOR_SCHEME)
    except ImportError:
        pass  # 如果style_config不可用，就不应用样式
