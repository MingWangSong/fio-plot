"""
科学论文风格图表样式配置

此模块提供了一套高质量的图表样式配置，专为科学论文发表设计，
参考了多种SCI期刊的图表要求和配色方案。
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

def apply_science_style():
    """应用科学论文风格的全局设置"""
    # 字体设置 - 使用字体回退机制
    # plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']  # 提供多种备选字体
    plt.rcParams['font.size'] = 10         # 基础字体大小
    plt.rcParams['axes.titlesize'] = 12    # 标题字体大小
    plt.rcParams['axes.labelsize'] = 11    # 轴标签字体大小
    plt.rcParams['xtick.labelsize'] = 9    # x轴刻度标签字体大小
    plt.rcParams['ytick.labelsize'] = 9    # y轴刻度标签字体大小
    plt.rcParams['legend.fontsize'] = 9    # 图例字体大小
    
    # 线条设置
    plt.rcParams['lines.linewidth'] = 1.5  # 线宽
    plt.rcParams['lines.markersize'] = 5   # 标记大小
    plt.rcParams['lines.markeredgewidth'] = 1  # 标记边缘宽度
    
    # 图表大小和DPI
    plt.rcParams['figure.figsize'] = (5, 4)  # 默认图表大小
    plt.rcParams['figure.dpi'] = 150         # 显示分辨率
    plt.rcParams['savefig.dpi'] = 300        # 保存分辨率
    
    # 边距设置
    plt.rcParams['figure.subplot.left'] = 0.15
    plt.rcParams['figure.subplot.right'] = 0.95
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.top'] = 0.9
    
    # 网格设置
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.alpha'] = 0.7
    plt.rcParams['axes.grid'] = False  # 默认不启用网格
    
    # 刻度设置
    plt.rcParams['xtick.direction'] = 'out'  # 刻度向外
    plt.rcParams['ytick.direction'] = 'out'
    plt.rcParams['xtick.major.width'] = 1.0  # 主刻度宽度
    plt.rcParams['ytick.major.width'] = 1.0
    plt.rcParams['xtick.major.size'] = 3.5   # 主刻度长度
    plt.rcParams['ytick.major.size'] = 3.5
    plt.rcParams['xtick.minor.width'] = 0.8  # 次刻度宽度
    plt.rcParams['ytick.minor.width'] = 0.8
    plt.rcParams['xtick.minor.size'] = 2.0   # 次刻度长度
    plt.rcParams['ytick.minor.size'] = 2.0
    
    # 轴脊梁设置
    plt.rcParams['axes.linewidth'] = 1.0     # 轴线宽度
    plt.rcParams['axes.edgecolor'] = 'black' # 轴线颜色
    
    # 图例设置
    plt.rcParams['legend.frameon'] = False   # 无边框
    plt.rcParams['legend.framealpha'] = 0.8  # 透明度
    plt.rcParams['legend.edgecolor'] = '0.8' # 边框颜色
    plt.rcParams['legend.borderpad'] = 0.4   # 内边距
    
    # 配色方案 - 使用SCI论文友好的配色
    plt.rcParams['axes.prop_cycle'] = cycler('color', [
        '#0072B2',  # 蓝色
        '#D55E00',  # 红橙色
        '#009E73',  # 绿色
        '#CC79A7',  # 粉色
        '#F0E442',  # 黄色
        '#56B4E9',  # 浅蓝色
        '#E69F00',  # 橙色
        '#694489',  # 紫色
    ])

def get_color_dict():
    """返回一个可用于不同元素的配色字典"""
    return {
        'primary_blue': '#0072B2',    # 主要蓝色
        'accent_orange': '#E69F00',   # 强调橙色
        'accent_red': '#D55E00',      # 强调红色
        'accent_green': '#009E73',    # 强调绿色
        'accent_purple': '#694489',   # 强调紫色
        'accent_pink': '#CC79A7',     # 强调粉色
        'accent_yellow': '#F0E442',   # 强调黄色
        'accent_cyan': '#56B4E9',     # 强调青色
        'gray_light': '#EEEEEE',      # 浅灰色(用于背景)
        'gray_medium': '#AAAAAA',     # 中灰色(用于次要元素)
        'gray_dark': '#444444',       # 深灰色(用于文本)
        'bar_face': '#E2E2E2',        # 柱体填充色
        'bar_edge': '#555555',        # 柱体边缘色
        'error_bar': '#D55E00',       # 误差条颜色
    }

def style_single_bar(ax, bars, bar_color=None, errorbar_color=None):
    """
    设置单Y轴柱状图的样式，与双Y轴柱状图保持一致的视觉风格。
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        轴对象
    bars : matplotlib.container.BarContainer
        柱状图容器
    bar_color : str, optional
        柱状图的颜色，如果为None则根据数据类型自动选择
    errorbar_color : str, optional
        错误条的颜色，默认使用配色方案中的error_bar颜色
    """
    colors = get_color_dict()
    # 根据标签类型选择合适的颜色（如果未指定）
    if bar_color is None:
        ylabel = ax.get_ylabel()
        if "IOPS" in ylabel:
            bar_color = colors["primary_blue"]
        elif "Latency" in ylabel:
            bar_color = colors["accent_red"]
        else:  # 带宽或其他
            bar_color = colors["accent_green"]
    
    errorbar_color = errorbar_color or colors['error_bar']
    
    # 设置柱体样式 - 与双Y轴保持一致
    for bar in bars:
        bar.set_facecolor(bar_color)
        bar.set_edgecolor('black')
        bar.set_linewidth(0.5)
    
    # 设置误差棒样式
    if hasattr(bars, 'errorbar') and bars.errorbar is not None:
        try:
            if hasattr(bars.errorbar, 'lines'):
                bars.errorbar.lines[0].set_color(errorbar_color)
                
                # 处理不同版本matplotlib的兼容性
                if isinstance(bars.errorbar.lines[1], list):
                    for cap in bars.errorbar.lines[1]:
                        cap.set_color(errorbar_color)
                else:
                    bars.errorbar.lines[1].set_color(errorbar_color)
                    
                if isinstance(bars.errorbar.lines[2], list):
                    for cap in bars.errorbar.lines[2]:
                        cap.set_color(errorbar_color)
                else:
                    bars.errorbar.lines[2].set_color(errorbar_color)
        except (AttributeError, IndexError):
            # 处理可能的属性错误或索引错误
            pass
    
    # 美化坐标轴 - 与双Y轴风格一致
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    
    # 设置刻度参数 - 与双Y轴保持一致
    ax.tick_params(axis='both', which='major', direction='out', length=4, width=1)
    ax.tick_params(axis='both', which='minor', direction='out', length=2, width=0.5)
    
    # 设置Y轴标签和刻度颜色与柱状图匹配 - 与双Y轴保持一致
    ax.yaxis.label.set_color(bar_color)
    ax.tick_params(axis='y', colors=bar_color)
    ax.spines['left'].set_color(bar_color)
    
    return ax

def style_multi_bars(ax, bars_list, colors=None):
    """美化多组柱状图样式
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        要美化的坐标轴对象
    bars_list : list of matplotlib.container.BarContainer
        柱状图对象列表
    colors : list, optional
        自定义颜色列表，如果不提供则使用默认配色方案
    """
    if colors is None:
        palette = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = palette[:len(bars_list)]
    
    # 设置柱体样式
    for i, bars in enumerate(bars_list):
        color = colors[i]
        for bar in bars:
            bar.set_facecolor(color)
            bar.set_edgecolor('black')
            bar.set_linewidth(0.5)
        
        # 设置误差棒样式
        if hasattr(bars, 'errorbar'):
            bars.errorbar.lines[0].set_color('black')
            for cap in bars.errorbar.lines[1]:
                cap.set_color('black')
            for cap in bars.errorbar.lines[2]:
                cap.set_color('black')
    
    # 美化坐标轴
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    ax.tick_params(axis='both', which='major', direction='out', length=4, width=1)
    ax.tick_params(axis='both', which='minor', direction='out', length=2, width=0.5)

def format_table(table, fontsize=9, header_color='#E6F2FF', row_colors=None):
    """美化表格样式
    
    Parameters:
    -----------
    table : matplotlib.table.Table
        要美化的表格对象
    fontsize : int
        表格字体大小
    header_color : str
        表头背景色
    row_colors : list, optional
        行背景色交替列表，默认为None (不设置交替色)
    """
    # 设置表格基本样式
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1, 1.2)
    
    # 获取所有单元格
    cells = table.get_celld()
    
    # 获取行列数
    rows = max(key[0] for key in cells.keys()) + 1
    cols = max(key[1] for key in cells.keys()) + 1
    
    # 设置表头样式
    for j in range(cols):
        cell = cells[(0, j)]
        cell.set_facecolor(header_color)
        cell.set_text_props(weight='bold', color='black')
        
    # 设置行交替颜色
    if row_colors:
        for i in range(1, rows):
            row_color = row_colors[i % len(row_colors)]
            for j in range(cols):
                cells[(i, j)].set_facecolor(row_color)
    
    # 设置边框
    for key, cell in cells.items():
        cell.set_linewidth(1.0)  # 增加线宽，使边框更明显
        cell.set_edgecolor('#555555')  # 边框颜色更深
        # 显式设置所有边的可见性
        cell.visible_edges = 'BTRL'  # 显示所有边 (Bottom, Top, Right, Left)

# 预定义的配色方案
COLOR_SCHEMES = {
    'nature': {
        'colors': ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00', '#694489'],
        'bar_face': '#E2E2E2',
        'bar_edge': '#555555',
        'error_bar': '#D55E00',
    },
    'science': {
        'colors': ['#3274A1', '#E1812C', '#3A923A', '#C03D3E', '#9372B2', '#845B53', '#D684BD', '#7F7F7F'],
        'bar_face': '#D9D9D9',
        'bar_edge': '#333333',
        'error_bar': '#C03D3E',
    },
    'ieee': {
        'colors': ['#0071BC', '#D85218', '#007836', '#7B2379', '#89288F', '#F5DF16', '#FF8427', '#FFC24B'],
        'bar_face': '#E6E6E6',
        'bar_edge': '#2E2E2E',
        'error_bar': '#D85218',
    },
    'pastel': {
        'colors': ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3'],
        'bar_face': '#F2F2F2',
        'bar_edge': '#A0A0A0',
        'error_bar': '#FC8D62',
    }
}

def apply_color_scheme(scheme_name):
    """应用预定义的配色方案
    
    Parameters:
    -----------
    scheme_name : str
        配色方案名称，可选值: 'nature', 'science', 'ieee', 'pastel'
    """
    if scheme_name not in COLOR_SCHEMES:
        raise ValueError(f"Unknown color scheme: {scheme_name}. Available schemes: {list(COLOR_SCHEMES.keys())}")
    
    scheme = COLOR_SCHEMES[scheme_name]
    
    # 应用颜色循环
    plt.rcParams['axes.prop_cycle'] = cycler('color', scheme['colors'])
    
    return scheme 

def style_dual_bar(ax1, ax3, rects1, rects2, left_color=None, right_color=None):
    """
    设置双Y轴柱状图的样式。
    
    Parameters
    ----------
    ax1 : matplotlib.axes.Axes
        左侧Y轴对象
    ax3 : matplotlib.axes.Axes
        右侧Y轴对象
    rects1 : matplotlib.container.BarContainer
        左侧Y轴的柱状图容器
    rects2 : matplotlib.container.BarContainer
        右侧Y轴的柱状图容器
    left_color : str, optional
        左侧柱状图的颜色，如果为None则使用默认颜色
    right_color : str, optional
        右侧柱状图的颜色，如果为None则使用默认颜色
    """
    colors = get_color_dict()
    left_color = left_color or colors["primary_blue"]
    right_color = right_color or colors["accent_red"]
    
    # 设置左侧轴柱体样式
    for bar in rects1:
        bar.set_facecolor(left_color)
        bar.set_edgecolor('black')
        bar.set_linewidth(0.5)
    
    # 设置右侧轴柱体样式
    for bar in rects2:
        bar.set_facecolor(right_color)
        bar.set_edgecolor('black')
        bar.set_linewidth(0.5)
    
    # 设置左侧Y轴样式
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(True)
    ax1.spines['bottom'].set_visible(True)
    
    # 设置右侧Y轴样式 - 确保它可见
    ax3.spines['top'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    ax3.spines['right'].set_visible(True)
    ax3.spines['bottom'].set_visible(True)
    
    # 设置刻度参数
    ax1.tick_params(axis='both', which='major', direction='out', length=4, width=1)
    ax3.tick_params(axis='both', which='major', direction='out', length=4, width=1)
    
    # 设置右侧Y轴标签颜色，与柱状图匹配
    ax3.yaxis.label.set_color(right_color)
    ax3.tick_params(axis='y', colors=right_color)
    ax3.spines['right'].set_color(right_color)
    
    # 设置左侧Y轴标签颜色，与柱状图匹配
    ax1.yaxis.label.set_color(left_color)
    ax1.tick_params(axis='y', colors=left_color)
    ax1.spines['left'].set_color(left_color)
    
    return ax1, ax3 