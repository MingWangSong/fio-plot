import numpy as np
import matplotlib.pyplot as plt
import pprint

from . import (
    supporting,
    shared_chart as shared,
    tables,
    table_support as ts,
    style_config  # 导入新的样式配置模块
)

def format_hostname_labels(settings, data):
    labels = []
    counter = 1
    hostcounter = 0 
    divide = int(len(data["hostname_series"]) / len(data["x_axis"])) # that int convert should work
    for host in data["hostname_series"]:
        hostcounter += 1
        attr = data["x_axis"][counter-1]
        labels.append(f"{host}\n{settings['graphtype'][-2:]} {attr}")
        if hostcounter % divide == 0:
            counter += 1
    return labels

def set_max_yaxis(settings, axes):
    for ax in axes:
        if ax.get_ylabel() == "IOPS":
            if settings["max_iops"]:
                ax.set_ylim(settings["min_iops"],settings["max_iops"])
        if "Latency" in ax.get_ylabel():
            if settings["max_lat"]:
                ax.set_ylim(settings["min_lat"],settings["max_lat"])

def calculate_font_size(settings, x_axis):
    max_label_width = max(ts.get_max_width([x_axis], len(x_axis)))
    #print(max_label_width)
    fontsize = 0
    #
    # This hard-coded font sizing is ugly but if somebody knows a better algorithm...
    #
    cols = len(x_axis)
    if settings["group_bars"]:
        if max_label_width >= 10:
            fontsize = 6
        else:
            fontsize = 8
    else:
        if max_label_width >= 10 and cols > 8:
            fontsize = 6
        else:
            fontsize = 8
    return fontsize

def create_bars_and_xlabels(settings, data, ax1, ax3):

    return_data = {"ax1": None, "ax3": None, "rects1": None, "rects2": None, "fontsize": None}
    
    y1_axis = data["y1_axis"]["data"]
    y2_axis = np.array(data["y2_axis"]["data"], dtype=float)
    width = 0.9

    # 使用科学配色方案
    colors = style_config.get_color_dict()
    color_iops = colors["primary_blue"]
    color_lat = colors["accent_red"]

    if settings["group_bars"]:
        x_pos1 = np.arange(1, len(y1_axis) + 1, 1)
        x_pos2 = np.arange(len(y1_axis) + 1, len(y1_axis) + len(y2_axis) + 1, 1)

        rects1 = ax1.bar(x_pos1, y1_axis, width, color=color_iops, ec='black', lw=0.5)
        rects2 = ax3.bar(x_pos2, y2_axis, width, color=color_lat, ec='black', lw=0.5)

        x_axis = data["x_axis"] * 2
        ltest = np.arange(1, len(x_axis) + 1, 1)

    else:
        x_pos = np.arange(0, (len(y1_axis) * 2), 2)

        rects1 = ax1.bar(x_pos, y1_axis, width, color=color_iops, ec='black', lw=0.5)
        rects2 = ax3.bar(x_pos + width, y2_axis, width, color=color_lat, ec='black', lw=0.5)
        x_axis = data["x_axis"]

        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                x_axis = format_hostname_labels(settings, data)
        ltest = np.arange(0.45, (len(y1_axis) * 2), 2)

    ax1.set_ylabel(data["y1_axis"]["format"])
    ax3.set_ylabel(data["y2_axis"]["format"])
    ax1.set_xlabel(settings["label"])
    ax1.set_xticks(ltest)

    set_max_yaxis(settings, [ax1, ax3])
    
    fontsize = calculate_font_size(settings, x_axis)
    #print(fontsize)
    if settings["graphtype"] == "compare_graph":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    elif settings["graphtype"] == "bargraph2d_qd" or settings["graphtype"] == "bargraph2d_nj":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize,)
    else:
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize, rotation=-50)

    # 应用双轴样式
    ax1, ax3 = style_config.style_dual_bar(ax1, ax3, rects1, rects2, color_iops, color_lat)
    
    return_data["rects1"] = rects1
    return_data["rects2"] = rects2
    return_data["ax1"] = ax1
    return_data["ax3"] = ax3
    return_data["fontsize"] = fontsize
    return return_data

def create_single_bars_and_xlabels(settings, data, ax1):
    
    return_data = {"ax1": None, "rects1": None, "fontsize": None}
    
    y1_axis = data["y1_axis"]["data"]
    width = 0.9

    # 使用配色方案
    colors = style_config.get_color_dict()
    color = colors["primary_blue"]  # 默认使用IOPS的颜色
    
    # 根据数据类型选择合适的颜色
    if data["y1_axis"]["format"] == "IOPS":
        color = colors["primary_blue"]  # IOPS的颜色
    elif "Latency" in data["y1_axis"]["format"]:
        color = colors["accent_red"]  # 延迟的颜色
    else:
        color = colors["accent_green"]  # 带宽的颜色
    
    # 与create_bars_and_xlabels保持一致的分割方式
    if settings["group_bars"]:
        x_pos = np.arange(1, len(y1_axis) + 1, 1)
        rects1 = ax1.bar(x_pos, y1_axis, width, color=color, ec='black', lw=0.5)
        x_axis = data["x_axis"]
        ltest = np.arange(1, len(x_axis) + 1, 1)
    else:
        x_pos = np.arange(0, (len(y1_axis) * 2), 2)
        rects1 = ax1.bar(x_pos, y1_axis, width, color=color, ec='black', lw=0.5)
        x_axis = data["x_axis"]
        
        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                x_axis = format_hostname_labels(settings, data)
        ltest = np.arange(0.45, (len(y1_axis) * 2), 2)

    ax1.set_ylabel(data["y1_axis"]["format"])
    ax1.set_xlabel(settings["label"])
    ax1.set_xticks(ltest)

    # 设置Y轴范围
    set_max_yaxis(settings, [ax1])
    
    fontsize = calculate_font_size(settings, x_axis)
    
    # 设置X轴标签，与双Y轴保持一致
    if settings["graphtype"] == "compare_graph":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    elif settings["graphtype"] == "bargraph2d_qd" or settings["graphtype"] == "bargraph2d_nj":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    else:
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize, rotation=-50)

    # 美化柱状图和轴 - 明确传递颜色参数
    style_config.style_single_bar(ax1, rects1, bar_color=color)

    return_data["rects1"] = rects1
    return_data["ax1"] = ax1
    return_data["fontsize"] = fontsize
    return return_data

def chart_2dbarchart_jsonlogdata(settings, dataset):
    # 应用科学论文风格
    style_config.apply_science_style()
    
    # 应用适合的配色方案 (可以根据需要选择 'nature', 'science', 'ieee', 'pastel')
    style_config.apply_color_scheme('science')

    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)
    
    # 检查是否只需要一个Y轴
    single_y_axis = isinstance(settings["type"], list) and len(settings["type"]) == 1
    
    # 创建图表和轴
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    
    # 为顶部标题预留更多空间，特别是在有多个表格时
    fig.subplots_adjust(top=0.88, bottom=0.15)
    
    # 只有在需要双Y轴时才创建第二个Y轴
    ax3 = None
    if not single_y_axis:
        ax3 = ax1.twinx()
    
    # 设置图表大小
    fig.set_size_inches(10, 6)
    plt.margins(x=0.01)
    
    # 添加信息来源和FIO版本
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax2)

    ax2.axis("off")

    # 根据是否是单Y轴来调用不同的绘图函数
    if single_y_axis:
        return_data = create_single_bars_and_xlabels(settings, data, ax1)
        rects1 = return_data["rects1"]
        ax1 = return_data["ax1"]
        fontsize = return_data["fontsize"]
        rects2 = None
    else:
        return_data = create_bars_and_xlabels(settings, data, ax1, ax3)
        rects1 = return_data["rects1"]
        rects2 = return_data["rects2"]
        ax1 = return_data["ax1"]
        ax3 = return_data["ax3"]
        fontsize = return_data["fontsize"]

    # 设置标题 - 添加轴类型的完整信息
    original_type = settings["type"]  # 保存原始类型值以便后续恢复
    
    # 临时设置type为空，避免在标题中重复显示
    settings["type"] = ""
    
    # 设置查询参数
    settings[settings["query"]] = dataset_types[settings["query"]]
    
    # 根据读写模式设置合适的标题
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(
            settings,
            plt,
            ax1,
            bs=data["bs"][0],
            skip_keys=[settings["query"]]
        )
    else:
        supporting.create_title_and_sub(
            settings,
            plt,
            ax1,
            bs=data["bs"][0],
            skip_keys=[settings["query"], "filter"]
        )
    
    # 恢复原始type值
    settings["type"] = original_type
    
    # 在柱形顶部标注数值
    shared.autolabel(rects1, ax1)
    if not single_y_axis and rects2 is not None:
        shared.autolabel(rects2, ax3)
    
    # 绘制表格
    if settings["show_data"]:
        table = tables.create_values_table(settings, data, ax2, fontsize-1)
    else:
        table = tables.create_stddev_table(settings, data, ax2, fontsize-1)
    
    # 绘制CPU使用表格（如果需要）
    if settings["show_cpu"] and not settings["show_ss"]:
        table = tables.create_cpu_table(settings, data, ax2, fontsize-1)

    # 绘制稳态表格（如果需要）
    if settings["show_ss"] and not settings["show_cpu"]:
        table = tables.create_steadystate_table(settings, data, ax2, fontsize-1)

    # 创建图例，确保位置合适避免遮挡
    legend_loc = "lower left" if settings["show_cpu"] or settings["show_ss"] else "center left"
    
    if single_y_axis:
        ax2.legend(
            (rects1[0],),
            (data["y1_axis"]["format"],),
            loc=legend_loc,
            frameon=False,
        )
    else:
        ax2.legend(
            (rects1[0], rects2[0]),
            (data["y1_axis"]["format"], data["y2_axis"]["format"]),
            loc=legend_loc,
            frameon=False,
        )
    
    # 确保紧凑布局，避免标题和表格重叠
    plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.88])
    
    # 保存图表为PNG文件
    supporting.save_png(settings, plt, fig)


def compchart_2dbarchart_jsonlogdata(settings, dataset):
    """创建用于比较数据的柱状图。"""
    # 应用科学论文风格
    style_config.apply_science_style()
    
    # 应用适合的配色方案
    style_config.apply_color_scheme('science')
    
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set_improved(settings, dataset, dataset_types)
    
    # 检查是否只需要一个Y轴
    single_y_axis = isinstance(settings["type"], list) and len(settings["type"]) == 1

    # 创建图表和轴
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    
    # 为顶部标题预留更多空间，特别是在有多个表格时
    fig.subplots_adjust(top=0.88, bottom=0.15)
    
    # 只有在需要双Y轴时才创建第二个Y轴
    ax3 = None
    if not single_y_axis:
        ax3 = ax1.twinx()
        
    # 设置图表大小
    fig.set_size_inches(10, 6)
    plt.margins(x=0.01)

    # 添加信息来源和FIO版本
    supporting.plot_source(settings, plt, ax1)
    supporting.plot_fio_version(settings, data["fio_version"][0], plt, ax2)

    ax2.axis("off")

    # 根据是否是单Y轴来调用不同的绘图函数
    if single_y_axis:
        return_data = create_single_bars_and_xlabels(settings, data, ax1)
        rects1 = return_data["rects1"]
        ax1 = return_data["ax1"]
        fontsize = return_data["fontsize"]
        rects2 = None
    else:
        return_data = create_bars_and_xlabels(settings, data, ax1, ax3)
        rects1 = return_data["rects1"]
        rects2 = return_data["rects2"]
        ax1 = return_data["ax1"]
        ax3 = return_data["ax3"]
        fontsize = calculate_font_size(settings, data["x_axis"])
        
    # 设置标题 - 保存原始类型
    original_type = settings["type"]
    settings["type"] = ""
    settings["iodepth"] = dataset_types["iodepth"]
    settings["numjobs"] = dataset_types["numjobs"]
    
    # 根据单/双Y轴情况设置副标题
    subtitle = "Comparison"
    if single_y_axis:
        subtitle = f"Comparison - Metric: {', '.join(original_type)}"
    
    # 设置标题和副标题
    if "filter" in settings.keys():
        supporting.create_title_and_sub(
            settings, plt, bs=data["bs"][0], subtitle=subtitle, skip_keys=["filter"]
        )
    else:
        supporting.create_title_and_sub(
            settings, plt, bs=data["bs"][0], subtitle=subtitle
        )
    
    # 恢复原始type值
    settings["type"] = original_type

    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    if not single_y_axis and rects2 is not None:
        shared.autolabel(rects2, ax3)

    if settings["show_data"]:
        table = tables.create_values_table(settings, data, ax2, fontsize)
    else:
        table = tables.create_stddev_table(settings, data, ax2, fontsize)

    if settings["show_cpu"] and not settings["show_ss"]:
        table = tables.create_cpu_table(settings, data, ax2, fontsize)

    if settings["show_ss"] and not settings["show_cpu"]:
        table = tables.create_steadystate_table(settings, data, ax2, fontsize)

    # 创建图例，确保位置合适避免遮挡
    legend_loc = "lower left" if settings["show_cpu"] or settings["show_ss"] else "center left"
    
    if single_y_axis:
        ax2.legend(
            (rects1[0],),
            (data["y1_axis"]["format"],),
            loc=legend_loc,
            frameon=False,
        )
    else:
        ax2.legend(
            (rects1[0], rects2[0]),
            (data["y1_axis"]["format"], data["y2_axis"]["format"]),
            loc=legend_loc,
            frameon=False,
        )
    
    # 确保紧凑布局，避免标题和表格重叠
    plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.88])
    
    # 保存图表为PNG文件
    supporting.save_png(settings, plt, fig)
