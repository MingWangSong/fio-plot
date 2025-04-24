import numpy as np
import matplotlib.pyplot as plt
import pprint

from . import (
    supporting,
    shared_chart as shared,
    tables,
    table_support as ts
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

    return_data = {"ax1": None, "ax3": None, "rects1": None, "rects2": None}
    
    y1_axis = data["y1_axis"]["data"]
    y2_axis = np.array(data["y2_axis"]["data"], dtype=float)
    width = 0.9

    color_iops = "#a8ed63"
    color_lat = "#34bafa"

    if settings["group_bars"]:
        x_pos1 = np.arange(1, len(y1_axis) + 1, 1)
        x_pos2 = np.arange(len(y1_axis) + 1, len(y1_axis) + len(y2_axis) + 1, 1)

        rects1 = ax1.bar(x_pos1, y1_axis, width, color=color_iops)
        rects2 = ax3.bar(x_pos2, y2_axis, width, color=color_lat)

        x_axis = data["x_axis"] * 2
        ltest = np.arange(1, len(x_axis) + 1, 1)

    else:
        x_pos = np.arange(0, (len(y1_axis) * 2), 2)

        rects1 = ax1.bar(x_pos, y1_axis, width, color=color_iops)
        rects2 = ax3.bar(x_pos + width, y2_axis, width, color=color_lat)
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

    return_data["rects1"] = rects1
    return_data["rects2"] = rects2
    return_data["ax1"] = ax1
    return_data["ax3"] = ax3
    return_data["fontsize"] = fontsize
    return return_data

def create_single_bars_and_xlabels(settings, data, ax1):
    """为单Y轴情况创建柱状图和X轴标签"""
    return_data = {"ax1": None, "rects1": None, "fontsize": None}
    
    y1_axis = data["y1_axis"]["data"]
    width = 0.9

    # 使用与双Y轴相同的颜色
    if data["y1_axis"]["format"] == "IOPS":
        color = "#a8ed63"  # IOPS的颜色
    elif "Latency" in data["y1_axis"]["format"]:
        color = "#34bafa"  # 延迟的颜色
    else:
        color = "#ed63a8"  # 带宽的颜色
    
    # 使用与双Y轴相同的X轴位置计算方式
    x_pos = np.arange(0, (len(y1_axis) * 2), 2)
    rects1 = ax1.bar(x_pos, y1_axis, width, color=color)
    
    x_axis = data["x_axis"]
    if "hostname_series" in data.keys():
        if data["hostname_series"]:
            x_axis = format_hostname_labels(settings, data)
    
    # 使用与双Y轴相同的X轴刻度位置
    ltest = np.arange(0.45, (len(y1_axis) * 2), 2)

    ax1.set_ylabel(data["y1_axis"]["format"])
    ax1.set_xlabel(settings["label"])
    ax1.set_xticks(ltest)

    # 设置Y轴范围，保持与双Y轴一致
    if data["y1_axis"]["format"] == "IOPS":
        if settings["max_iops"]:
            ax1.set_ylim(settings["min_iops"], settings["max_iops"])
    elif "Latency" in data["y1_axis"]["format"]:
        if settings["max_lat"]:
            ax1.set_ylim(settings["min_lat"], settings["max_lat"])
    elif settings.get("max_y"):
        ax1.set_ylim(0, settings["max_y"])
    
    fontsize = calculate_font_size(settings, x_axis)
    
    # 设置X轴标签，与双Y轴保持一致
    if settings["graphtype"] == "compare_graph":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    elif settings["graphtype"] == "bargraph2d_qd" or settings["graphtype"] == "bargraph2d_nj":
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize)
    else:
        ax1.set_xticklabels(labels=x_axis, fontsize=fontsize, rotation=-50)

    return_data["rects1"] = rects1
    return_data["ax1"] = ax1
    return_data["fontsize"] = fontsize
    return return_data

def chart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for drawing iops/latency bars for a
    particular iodepth."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set(settings, dataset, dataset_types)
    
    # 检查是否只需要一个Y轴
    single_y_axis = isinstance(settings["type"], list) and len(settings["type"]) == 1
    
    # 使用固定的顶部空间
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    
    # 为顶部标题预留空间
    fig.subplots_adjust(top=0.85)
    
    # 只有在需要双Y轴时才创建第二个Y轴
    ax3 = None
    if not single_y_axis:
        ax3 = ax1.twinx()
    
    fig.set_size_inches(10, 6)
    plt.margins(x=0.01)
    #
    # Puts in the credit source (often a name or url)
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

    #
    # Set title
    settings["type"] = ""
    settings[settings["query"]] = dataset_types[settings["query"]]
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(
            settings,
            plt,
            bs=data["bs"][0],
            skip_keys=[settings["query"]],
        )
    else:
        supporting.create_title_and_sub(
            settings,
            plt,
            bs=data["bs"][0],
            skip_keys=[settings["query"], "filter"],
        )
    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    if not single_y_axis and rects2:
        shared.autolabel(rects2, ax3)
    
    #
    # Draw the standard deviation table
    if settings["show_data"]:
        tables.create_values_table(settings, data, ax2, fontsize)
    else:
        tables.create_stddev_table(settings, data, ax2, fontsize)
    
    #
    # Draw the cpu usage table if requested
    # pprint.pprint(data)
    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2, fontsize)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2, fontsize)

    #
    # Create legend
    if single_y_axis:
        ax2.legend(
            (rects1[0],),
            (data["y1_axis"]["format"],),
            loc="center left",
            frameon=False,
        )
    else:
        ax2.legend(
            (rects1[0], rects2[0]),
            (data["y1_axis"]["format"], data["y2_axis"]["format"]),
            loc="center left",
            frameon=False,
        )
    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)


def compchart_2dbarchart_jsonlogdata(settings, dataset):
    """This function is responsible for creating bar charts that compare data."""
    dataset_types = shared.get_dataset_types(dataset)
    data = shared.get_record_set_improved(settings, dataset, dataset_types)
    
    # pprint.pprint(data)

    # 检查是否只需要一个Y轴
    single_y_axis = isinstance(settings["type"], list) and len(settings["type"]) == 1

    # 使用固定的顶部空间
    fig, (ax1, ax2) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [7, 1]})
    
    # 为顶部标题预留空间
    fig.subplots_adjust(top=0.85)
    
    # 只有在需要双Y轴时才创建第二个Y轴
    ax3 = None
    if not single_y_axis:
        ax3 = ax1.twinx()
        
    fig.set_size_inches(10, 6)
    plt.margins(x=0.01)

    #
    # Puts in the credit source (often a name or url)
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
        
    #
    # Set title
    settings["type"] = ""
    settings["iodepth"] = dataset_types["iodepth"]
    if settings["rw"] == "randrw":
        supporting.create_title_and_sub(settings, plt, skip_keys=["iodepth"])
    else:
        supporting.create_title_and_sub(settings, plt, skip_keys=[])

    #
    # Labeling the top of the bars with their value
    shared.autolabel(rects1, ax1)
    if not single_y_axis and rects2:
        shared.autolabel(rects2, ax3)

    if settings["show_data"]:
        tables.create_values_table(settings, data, ax2, fontsize)
    else:
        tables.create_stddev_table(settings, data, ax2, fontsize)

    if settings["show_cpu"] and not settings["show_ss"]:
        tables.create_cpu_table(settings, data, ax2, fontsize)

    if settings["show_ss"] and not settings["show_cpu"]:
        tables.create_steadystate_table(settings, data, ax2, fontsize)

    # Create legend
    if single_y_axis:
        ax2.legend(
            (rects1[0],),
            (data["y1_axis"]["format"],),
            loc="center left",
            frameon=False,
        )
    else:
        ax2.legend(
            (rects1[0], rects2[0]),
            (data["y1_axis"]["format"], data["y2_axis"]["format"]),
            loc="center left",
            frameon=False,
        )

    #
    # Save graph to PNG file
    #
    supporting.save_png(settings, plt, fig)
