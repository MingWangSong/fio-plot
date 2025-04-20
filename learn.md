
# fio_plot工具-l参数绘图原理分析

## 工具简介

fio_plot是一个基于Python实现的工具，用于将FIO（Flexible I/O Tester）测试生成的数据可视化。本文档重点分析-l参数（对应`--bargraph2d-qd`选项）的实现机制，该参数用于生成展示不同队列深度下IOPS和延迟性能的2D柱状图。

## 执行流程概述

1. 用户执行命令：`fio-plot -i INPUT_DIR -T "标题" -l -r randread`
2. `__main__.py`调用`fio_plot.main()`函数
3. main函数解析命令行参数，识别-l参数，设置图表类型为"bargraph2d_qd"
4. 根据路由表调用`get_json_data()`函数获取数据
5. 调用`chart_2dbarchart_jsonlogdata()`函数处理数据并绘制图表
6. 保存图表并嵌入元数据

## 入口点分析

程序从`__main__.py`开始执行：
```python
import fio_plot

if __name__ == '__main__':
    fio_plot.main()
```

在`__init__.py`中的main函数控制整个执行流程：
```python
def main():
    rawsettings = get_settings()
    settings = rawsettings[1]
    parser = rawsettings[0]
    routing_dict = getdata.get_routing_dict()
    graphtype = settings["graphtype"]
    settings = getdata.configure_default_settings(settings, routing_dict, graphtype)
    data = routing_dict[graphtype]["get_data"](settings)
    routing_dict[graphtype]["function"](settings, data)
    option_found = True
    checks.post_flight_check(parser, option_found)
```

## 参数解析

当用户指定-l参数时，在`fiolib/argparsing.py`中将图表类型设置为"bargraph2d_qd"：
```python
if settings["bargraph2d_qd"]:
    settings["graphtype"] = "bargraph2d_qd"
```

## 路由机制

在`fiolib/getdata.py`中，路由字典将"bargraph2d_qd"类型映射到数据获取函数和绘图函数：
```python
routing_dict = {
    "bargraph2d_qd": {
        "get_data": get_json_data,
        "function": fiolib.bar2d.chart_2dbarchart_jsonlogdata,
    },
    # 其他图表类型...
}
```

## 数据获取流程

`get_json_data`函数从指定目录获取和处理JSON文件：
1. 遍历输入目录，找出所有JSON文件
2. 根据读写模式、IO深度和作业数筛选文件
3. 解析JSON内容，提取性能数据
4. 创建易于访问的数据映射

核心实现在`fiolib/jsonimport.py`和`fiolib/jsonparsing.py`中：
```python
# 获取指定目录下的JSON文件
def get_benchmark_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                file_list.append(os.path.join(root, filename))
    return file_list

# 导入JSON数据集
def import_json_dataset(file_list, rw, iodepth, numjobs):
    dataset = {"directory": os.path.dirname(file_list[0]), "files": [], "rawdata": []}
    
    for item in file_list:
        with open(item) as json_file:
            try:
                data = json.load(json_file)
                if check_valid_file(item, rw, iodepth, numjobs, data):
                    dataset["files"].append(item)
                    dataset["rawdata"].append(data)
            except:
                pass
    
    return dataset
```

## 图表绘制实现

`chart_2dbarchart_jsonlogdata`函数在`fiolib/bar2d.py`中负责图表绘制：

1. **数据准备**：
   - 使用`get_record_set_improved`函数提取和组织数据
   - 根据数据范围自动确定适当的单位缩放

2. **双Y轴构建**：
   - 左Y轴显示IOPS数据
   - 右Y轴显示延迟数据
   - 每个队列深度对应两个柱状图

3. **图表美化**：
   - 添加图例、标题、网格
   - 设置X轴标签为队列深度值
   - 根据数据单位调整Y轴标签

4. **辅助信息**：
   - 创建标准差表格
   - 可选添加CPU使用表格

5. **保存图表**：
   - 将图表保存为PNG文件
   - 嵌入测试参数等元数据

核心绘图代码结构：
```python
def chart_2dbarchart_jsonlogdata(settings, dataset_list):
    # 准备图表
    fig, ax1 = plt.subplots(figsize=(15, 8))
    plt.grid(True)
    
    # 数据准备
    record_set = shared_chart.get_record_set_improved(settings, dataset_list)
    datadict = shared_chart.get_record_set_improved(settings, dataset_list)
    
    # 数据缩放
    scale_factor_iops, unit_iops = supporting.scale_data(datadict["iops"])
    scale_factor_lat, unit_lat = supporting.scale_data(datadict["lat"])
    
    # 绘制IOPS柱状图(左Y轴)
    x = np.arange(len(iodepth_list))
    width = 0.35
    iops_bars = []
    for i, iops_value in enumerate(datadict["iops"]):
        bar = ax1.bar(x[i] - width/2, iops_value * scale_factor_iops, width)
        iops_bars.append(bar)
    
    # 绘制延迟柱状图(右Y轴)
    ax2 = ax1.twinx()
    lat_bars = []
    for i, lat_value in enumerate(datadict["lat"]):
        bar = ax2.bar(x[i] + width/2, lat_value * scale_factor_lat, width)
        lat_bars.append(bar)
    
    # 设置轴标签和图例
    ax1.set_ylabel(f'IOPS ({unit_iops})')
    ax2.set_ylabel(f'Latency ({unit_lat})')
    ax1.set_xticks(x)
    ax1.set_xticklabels(iodepth_list)
    ax1.set_xlabel("IO Depth")
    
    # 添加标题和辅助信息
    plt.title(settings["title"])
    supporting.create_stddev_table(fig, record_set, settings)
    
    # 保存图表
    plt.tight_layout()
    supporting.save_png(settings, plt, fig)
    plt.close(fig)
```

## 关键技术特点

1. **模块化设计**：使用路由机制分离数据获取和可视化逻辑
2. **灵活的数据处理**：支持多种数据筛选和聚合方式
3. **自适应单位缩放**：根据数据范围自动调整显示单位
4. **双Y轴表示**：在同一图表上同时展示IOPS和延迟
5. **统计信息展示**：添加标准差表格提供数据可靠性参考
6. **元数据嵌入**：将测试参数嵌入到PNG文件中，便于后期查阅

## 总结

fio_plot工具通过精心设计的数据处理和可视化流程，将FIO测试生成的复杂性能数据转换为直观的2D柱状图。-l参数（bargraph2d_qd）特别关注于展示不同队列深度下存储设备的IOPS和延迟性能，帮助用户快速识别最佳队列深度设置和潜在的性能瓶颈。该工具采用模块化架构，便于扩展更多图表类型和数据处理方式。
