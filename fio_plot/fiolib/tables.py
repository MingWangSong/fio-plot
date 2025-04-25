import sys
from . import table_support as ts



def create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize):
    """创建通用表格并应用美观的样式
    
    Parameters:
    -----------
    settings : dict
        全局设置
    data : dict
        数据集
    table_vals : list
        表格数据
    ax2 : matplotlib.axes.Axes
        要绘制表格的坐标轴
    rowlabels : list
        行标签
    location : str
        表格位置
    fontsize : int
        字体大小
        
    Returns:
    --------
    table : matplotlib.table.Table
        创建的表格对象
    """
    # 计算列数及列宽度
    cols = len(table_vals[0])
    matrix = ts.get_max_width(table_vals, cols)
    colwidths = ts.calculate_colwidths(settings, cols, matrix)
    
    # 创建表格
    table = ax2.table(
        cellText=table_vals,
        loc=location,
        rowLabels=rowlabels,
        colLoc="center",
        colWidths=colwidths,
        cellLoc="center",
        rasterized=False,
    )
    
    # 关闭自动字体大小调整
    table.auto_set_font_size(False)
    
    # 设置表格缩放，使行高更适合内容
    table.scale(1, 1.2)
    
    # 获取所有单元格以进行样式设置
    cells = table.get_celld()
    
    # 获取行列数
    nrows = max(key[0] for key in cells.keys()) + 1
    ncols = max(key[1] for key in cells.keys()) + 1
    
    # 应用交替行颜色
    header_color = '#D9D9D9'  # 表头背景色
    row_colors = ['#FFFFFF', '#F8F8F8']  # 交替行背景色
    
    # 美化表格
    for i in range(nrows):
        for j in range(-1, ncols):  # -1索引用于行标签列
            try:
                cell = cells[(i, j)]
                
                # 设置基础字体大小
                if i == 0:  # 表头行
                    cell.set_fontsize(fontsize)
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor(header_color)
                else:  # 数据行
                    cell.set_fontsize(fontsize)
                    cell.set_facecolor(row_colors[i % len(row_colors)])
                
                # 确保所有单元格边框都可见
                cell.visible_edges = 'BTRL'  # Bottom, Top, Right, Left
                cell.set_linewidth(1.0)
                cell.set_edgecolor('#555555')
                
                # 设置单元格文本对齐
                if j == -1:  # 行标签
                    cell._text.set_horizontalalignment('right')
                else:  # 数据单元格
                    cell._text.set_horizontalalignment('center')
                
                # 根据需要调整行高
                if i == 0 and matrix and max(matrix) > 8:
                    # 调整表头行高，使长标签显示更好
                    height = cell.get_height()
                    cell.set_height(height * 1.2)
            except KeyError:
                # 某些组合可能不存在
                pass
    
    # 返回表格对象以便在后续代码中应用样式
    return table

    
def create_cpu_table(settings, data, ax2, fontsize):
    table_vals = [data["x_axis"], data["cpu"]["cpu_usr"], data["cpu"]["cpu_sys"]]
    rowlabels = ["CPU Usage", "cpu_usr %", "cpu_sys %"]
    location = "lower center"
    table = create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)
    return table


def create_values_table(settings, data, ax2, fontsize):
    # 检查y2_axis是否为None（单Y轴情况）
    if data["y2_axis"] is None:
        iops = ts.scale_iops(data["y1_axis"]["data"])
        table_vals = [data["x_axis"], iops]
        rowlabels = [settings["query"], data["y1_axis"]["format"]]
        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "data")
                table_vals = tabledata["table_vals"]
                metricname = tabledata["metricname"]
                # 根据单Y轴情况调整标签
                rowlabels = ["Hostname", metricname, "IOP/s"]
    else:
        iops = ts.scale_iops(data["y1_axis"]["data"])
        table_vals = [data["x_axis"], iops, data["y2_axis"]["data"]]
        rowlabels = [settings["query"], data["y1_axis"]["format"], data["y2_axis"]["format"]]
        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "data")
                table_vals = tabledata["table_vals"]
                metricname = tabledata["metricname"]
                rowlabels = ["Hostname", metricname, "IOP/s", "Latency"]
    
    location = "lower right"
    table = create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)
    return table


def create_stddev_table(settings, data, ax2, fontsize):
    # 检查不应该显示表格的情况
    if settings["show_ss"]:
        return None
    
    # 检查是否为单Y轴情况
    if data["y2_axis"] is None:
        # 检查是否有标准差数据
        if not data["y1_axis"]["stddev"]:
            return None
            
        table_vals = [data["x_axis"], data["y1_axis"]["stddev"]]    
        table_name = settings["label"]
        rowlabels = [table_name, data["y1_axis"]["format"]+" \u03C3 %"]
        
        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "stddev")
                table_vals = tabledata["table_vals"]
                metricname = tabledata["metricname"]
                rowlabels = ["Hostname", metricname, data["y1_axis"]["format"]+" \u03C3 %"]
    else:
        # 双Y轴情况
        if not data["y2_axis"]["stddev"]:
            return None
            
        table_vals = [data["x_axis"], data["y1_axis"]["stddev"], data["y2_axis"]["stddev"]]    
        table_name = settings["label"]
        rowlabels = [table_name, data["y1_axis"]["format"]+" \u03C3 %", data["y2_axis"]["format"]+" \u03C3 %"]
        
        if "hostname_series" in data.keys():
            if data["hostname_series"]:
                tabledata = ts.create_data_for_table_with_hostname_data(settings, data, "stddev")
                table_vals = tabledata["table_vals"]
                metricname = tabledata["metricname"]
                rowlabels = ["Hostname", metricname, "IOP/s \u03C3 %", "Latency \u03C3 %"]
    
    location = "lower right"
    table = create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)
    return table


def create_steadystate_table(settings, data, ax2, fontsize):
    # pprint.pprint(data)
    ## This error is required until I address this
    
    if "hostname_series" in data.keys():
        if data["hostname_series"]:
            print(f"\n Sorry, the steady state table is not compatible (yet) with client/server data\n")
            sys.exit(1)

    if data["ss_attained"]:
        data["ss_attained"] = ts.convert_number_to_yes_no(data["ss_attained"])
        table_vals = [
            data["x_axis"],
            data["ss_data_bw_mean"]["data"],
            data["ss_data_iops_mean"]["data"],
            data["ss_attained"],
        ]

        rowlabels = [
            "Steady state",
            f"BW mean {data['ss_data_bw_mean']['format']}",
            f"{data['ss_data_iops_mean']['format']}  mean",
            f"{data['ss_settings'][0]} attained",
        ]
        location = "lower center"
        table = create_generic_table(settings, data, table_vals, ax2, rowlabels, location, fontsize)
        return table
    else:
        print(
            "\n No steadystate data was found, so the steadystate table cannot be displayed.\n"
        )
        return None
