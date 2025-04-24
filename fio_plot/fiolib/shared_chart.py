import pprint
import sys

from operator import itemgetter
import re
from . import(
    supporting,
    dataimport
)

def get_dataset_types(dataset):
    """This code is probably insane.
    Using only the first item in a list to return because all items should be equal.
    If not, a warning is displayed.
    """
    dataset_types = {"rw": set(), "iodepth": set(), "numjobs": set()}
    operation = {"rw": str, "iodepth": int, "numjobs": int}

    type_list = []

    for item in dataset:
        temp_dict = dataset_types.copy()
        for x in dataset_types.keys():
            for y in item["data"]:
                temp_dict[x].add(operation[x](y[x]))
            temp_dict[x] = sorted(temp_dict[x])
        if len(type_list) > 0:
            tmp = type_list[len(type_list) - 1]
            if tmp != temp_dict:
                print(
                    "Warning: benchmark data may not contain the same kind of data, comparisons may be impossible."
                )
        type_list.append(temp_dict)
    # pprint.pprint(type_list)
    dataset_types = type_list[0]
    return dataset_types


def get_record_set_histogram(settings, dataset):
    rw = settings["rw"]
    iodepth = int(settings["iodepth"][0])
    numjobs = int(settings["numjobs"][0])

    # pprint.pprint(dataset[0])

    # fio_version = dataset["data"]["fio version"]

    record_set = {
        "iodepth": iodepth,
        "numjobs": numjobs,
        "data": None,
        "fio_version": None,
    }

    for record in dataset[0]["data"]:
        if (
            (int(record["iodepth"]) == iodepth)
            and (int(record["numjobs"]) == numjobs)
            and record["rw"] == rw
        ):
            record_set["data"] = record
            record_set["fio_version"] = record["fio_version"]
            return record_set

def validate_get_record_set(settings, mismatch, dataset):
    if mismatch == len(dataset):
        print(f"\n   It seems that none of the data matched your selection criteria.\n \
    Check the filenames of the JSON files check the following parameters \n \
    -r {settings['rw']}  -d {settings['iodepth']} -n {settings['numjobs']}\n")
        print("\nIf you think everything is correct, feel free to report a bug.\n")
        sys.exit(1)

def get_record_set_3d(settings, dataset, dataset_types, rw, metric):
    mismatch = 0
    record_set = {
        "iodepth": dataset_types["iodepth"],
        "numjobs": dataset_types["numjobs"],
        "values": [],
        "fio_version": [],
    }
    # pprint.pprint(dataset)
    if settings["rw"] == "randrw":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                "Since we are processing randrw data, you must specify a "
                "filter for either read or write data, not both."
            )
            sys.exit(1)

    for depth in dataset_types["iodepth"]:
        row = []
        for jobs in dataset_types["numjobs"]:
            for record in dataset[0]["data"]:
                # pprint.pprint(record)
                if (
                    (int(record["iodepth"]) == int(depth))
                    and int(record["numjobs"]) == jobs
                    and record["rw"] == rw
                    and record["type"] in settings["filter"]
                ):
                    row.append(record[metric])
                else:
                    mismatch+=1    
        record_set["values"].append(supporting.round_metric_series(row))
    record_set["fio_version"].append(dataset[0]["data"][0]["fio_version"])
    validate_get_record_set(settings, mismatch, dataset)
    return record_set

def get_record_set_improved(settings, dataset, dataset_types):
    """The supplied dataset, a list of flat dictionaries with data is filtered based
    on the parameters as set by the command line. The filtered data is also scaled and rounded.
    """
    mismatch = 0

    if settings["rw"] == "randrw" or settings["rw"] == "readwrite":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                f"Since we are processing {settings['rw']} data, you must specify a"
                " filter for either read or write data, not both."
            )
            sys.exit(1)

    labels = []
    # This is mostly for debugging purposes.
    for record in dataset:
        record["label"] = dataimport.return_folder_name(record["directory"], settings)
        labels.append(record["label"])

    datadict = {
        "fio_version": [],
        "iops_series_raw": [],
        "iops_stddev_series_raw": [],
        "lat_series_raw": [],
        "lat_stddev_series_raw": [],
        "cpu": {"cpu_sys": [], "cpu_usr": []},
        "x_axis": labels,
        "y1_axis": None,
        "y2_axis": None,
    }

    depth = settings["iodepth"][0]
    numjobs = settings["numjobs"][0]
    rw = settings["rw"]
    for depth in dataset_types["iodepth"]:
        for data in dataset:
            # pprint.pprint(data.keys())
            # pprint.pprint(data['directory'])
            for record in data["data"]:
                #pprint.pprint(record.keys())
                #pprint.pprint(f"-> {record['type']}")
                #print(f"{depth} - {record['iodepth']} + {numjobs} - {record['numjobs']} + {record['rw']} + {record['type']}")
                #print(f"{settings['filter']}")
                if (
                    (int(record["iodepth"]) == int(depth))
                    and int(record["numjobs"]) == int(numjobs)
                    and record["rw"] == rw
                    and record["type"] in settings["filter"]
                ):
                    datadict["fio_version"].append(record["fio_version"])
                    datadict["iops_series_raw"].append(record["iops"])
                    datadict["lat_series_raw"].append(record["lat"])
                    datadict["iops_stddev_series_raw"].append(record["iops_stddev"])
                    datadict["lat_stddev_series_raw"].append(record["lat_stddev"])
                    datadict["cpu"]["cpu_sys"].append(int(round(record["cpu_sys"], 0)))
                    datadict["cpu"]["cpu_usr"].append(int(round(record["cpu_usr"], 0)))
                else:
                    mismatch+=1

    validate_get_record_set(settings, mismatch, dataset)
    return scale_data(datadict)

def return_empty_data_dict(settings, dataset_types):
    numjobs = settings["numjobs"]
    labels = dataset_types[settings["query"]]
    #print(labels)
    datadict = {
        "fio_version": [],
        "iops_series_raw": [],
        "iops_stddev_series_raw": [],
        "lat_series_raw": [],
        "lat_stddev_series_raw": [],
        "cpu": {"cpu_sys": [], "cpu_usr": []},
        "bs": [],
        "x_axis": labels,
        "y1_axis": None,
        "y2_axis": None,
        "numjobs": numjobs,
        "ss_settings": [],
        "ss_attained": [],
        "ss_data_bw_mean": [],
        "ss_data_iops_mean": [],
        "hostname_series": [],
        "bw_series_raw": [],
        "bw_dev_series_raw": []
    }
    return datadict

def get_record_set(settings, dataset, dataset_types):
    """The supplied dataset, a list of flat dictionaries with data is filtered based
    on the parameters as set by the command line. The filtered data is also scaled and rounded.
    """
    #for x in dataset: #(DEBUG)
    #    for y in x["data"]:
    #        print(y["iodepth"])
        
    rw = settings["rw"]
    mismatch = 0

    if settings["rw"] == "randrw":
        if len(settings["filter"]) > 1 or not settings["filter"]:
            print(
                "Since we are processing randrw data, you must specify a filter for either"
                "read or write data, not both."
            )
            sys.exit(1)

    datadict = return_empty_data_dict(settings, dataset_types)    

    for record in dataset:
        for data in record['data']:
            for x in settings["iodepth"]:
                for y in settings["numjobs"]:
                    #print(f"Settings {x} - JSON {data['iodepth']} + {y} - {data['numjobs']} + {data['rw']} + {data['type']}")
                    #print(f"{settings['filter']}") 
                    #print("=====")
                    #pprint.pprint(data.keys())
                    if (
                        (int(data["iodepth"]) == int(x))
                        and int(data["numjobs"]) == int(y)
                        and data["rw"] == rw
                        and data["type"] in settings["filter"]
                    ):
                        #print(f"{x} - {data['iodepth']} + {y} - {data['numjobs']} + {data['rw']} + {data['type']}")
                        #print(f"{x} - {data['iodepth']} + {y} - {data['numjobs']} + {data['iops']}")
                        if "hostname" in data.keys():
                            if supporting.filter_hosts(settings, data):
                                datadict["hostname_series"].append(data['hostname'])  
                            else:
                                continue

                        datadict["fio_version"].append(data["fio_version"])
                        datadict["iops_series_raw"].append(data["iops"])
                        datadict["bw_series_raw"].append(data["bw"])
                        datadict["lat_series_raw"].append(data["lat"])
                        datadict["bs"].append(data["bs"])
                        if "iops_stddev" in data.keys():
                            datadict["iops_stddev_series_raw"].append(data["iops_stddev"])
                            datadict["lat_stddev_series_raw"].append(data["lat_stddev"])
                            datadict["bw_dev_series_raw"].append(data["bw_dev"])
                        
                        if "cpu_sys" in data.keys():
                            datadict["cpu"]["cpu_sys"].append(int(round(data["cpu_sys"], 0)))
                            datadict["cpu"]["cpu_usr"].append(int(round(data["cpu_usr"], 0)))

                        if "ss_attained" in data.keys():
                            if data["ss_settings"]:
                                datadict["ss_settings"].append(str(data["ss_settings"])),
                                datadict["ss_attained"].append(int(data["ss_attained"])),
                                datadict["ss_data_bw_mean"].append(
                                    int(round(data["ss_data_bw_mean"], 0))
                                ),
                                datadict["ss_data_iops_mean"].append(
                                    int(round(data["ss_data_iops_mean"], 0))
                                )
                    else:
                        mismatch+=1

    validate_get_record_set(settings, mismatch, dataset)
    return scale_data(datadict, settings["type"])


def scale_data(datadict, type):

        # 验证数据是否存在
    if not datadict['fio_version']:
        print(f"\n function scale_data did not receive any data\n")
        sys.exit(1)
        
    # 从输入字典中提取原始数据
    iops_series_raw = datadict["iops_series_raw"]
    iops_stddev_series_raw = datadict["iops_stddev_series_raw"]
    lat_series_raw = datadict["lat_series_raw"]
    lat_stddev_series_raw = datadict["lat_stddev_series_raw"]
    cpu_usr = datadict["cpu"]["cpu_usr"]
    cpu_sys = datadict["cpu"]["cpu_sys"]
    
    # 提取带宽数据(如果存在)
    bw_series_raw = None
    bw_dev_series_raw = None
    if "bw_series_raw" in datadict.keys():
        bw_series_raw = datadict["bw_series_raw"]
        bw_dev_series_raw = datadict["bw_dev_series_raw"]
    
    # 提取稳态数据(如果存在)
    ss_data_bw_mean = None
    ss_data_iops_mean = None
    if "ss_settings" in datadict.keys():
        ss_data_bw_mean = datadict["ss_data_bw_mean"]
        ss_data_iops_mean = datadict["ss_data_iops_mean"]

    # ---------- 处理延迟(Latency)数据 ----------
    # 计算延迟数据的缩放因子并应用缩放
    latency_scale_factor = supporting.get_scale_factor_lat(lat_series_raw)
    scaled_latency_data = supporting.scale_yaxis(lat_series_raw, latency_scale_factor)
    
    # 对缩放后的延迟数据进行四舍五入
    scaled_latency_data["data"] = supporting.round_metric_series(scaled_latency_data["data"])
    
    # 使用相同的缩放因子处理延迟标准差
    lat_stdev_scaled = supporting.scale_yaxis(lat_stddev_series_raw, latency_scale_factor)
    lat_stdev_scaled_rounded = supporting.round_metric_series(lat_stdev_scaled["data"])
    
    # 将延迟标准差转换为百分比并四舍五入
    lat_stddev_percent = supporting.raw_stddev_to_percent(
        scaled_latency_data["data"], lat_stdev_scaled_rounded)
    lat_stddev_percent = [int(x) for x in lat_stddev_percent]
    scaled_latency_data["stddev"] = supporting.round_metric_series(lat_stddev_percent)

    # ---------- 处理IOPS数据 ----------
    iops_scale_factor = supporting.get_scale_factor_iops(iops_series_raw)
    scaled_iops_data = supporting.scale_yaxis(iops_series_raw, iops_scale_factor)
    # scaled_iops_data = {}
    # scaled_iops_data["format"] = "IOPS"
    # 对IOPS数据进行四舍五入
    scaled_iops_data["data"] = supporting.round_metric_series(scaled_iops_data["data"])
    
    # 处理IOPS标准差：四舍五入并转换为百分比
    iops_stdev_scaled = supporting.scale_yaxis(iops_stddev_series_raw, iops_scale_factor)
    iops_stdev_scaled_rounded = supporting.round_metric_series(iops_stdev_scaled["data"])

    iops_stddev_percent = supporting.raw_stddev_to_percent(
        scaled_iops_data["data"], iops_stdev_scaled_rounded)
    iops_stddev_percent = [int(x) for x in iops_stddev_percent]
    scaled_iops_data["stddev"] = supporting.round_metric_series(iops_stddev_percent)
    
    # ---------- 处理带宽(Bandwidth)数据(如果存在) ----------
    scaled_bw_data = None
    if bw_series_raw:
        # 计算带宽数据的缩放因子并应用缩放
        bw_scale_factor = supporting.get_scale_factor_bw(bw_series_raw)
        scaled_bw_data = supporting.scale_yaxis(bw_series_raw, bw_scale_factor)
        
        # 对缩放后的带宽数据进行四舍五入
        scaled_bw_data["data"] = supporting.round_metric_series(scaled_bw_data["data"])
        
        # 使用相同的缩放因子处理带宽标准差
        bw_stdev_scaled = supporting.scale_yaxis(bw_dev_series_raw, bw_scale_factor)
        bw_stdev_scaled_rounded = supporting.round_metric_series(bw_stdev_scaled["data"])
        
        
        # 将带宽标准差转换为百分比并四舍五入
        bw_dev_percent = supporting.raw_stddev_to_percent(
            scaled_bw_data["data"], bw_stdev_scaled_rounded
        )
        bw_dev_percent = [int(x) for x in bw_dev_percent]
        scaled_bw_data["stddev"] = supporting.round_metric_series(bw_dev_percent)

    # ---------- 处理稳态数据(如果存在) ----------
    if "ss_settings" in datadict.keys() and datadict["ss_settings"]:
        # 缩放和四舍五入带宽数据
        ss_bw_scalefactor = supporting.get_scale_factor_bw_ss(ss_data_bw_mean)
        ss_data_bw_mean = supporting.scale_yaxis(ss_data_bw_mean, ss_bw_scalefactor)
        ss_data_bw_mean["data"] = supporting.round_metric_series(ss_data_bw_mean["data"])
        
        # 缩放和四舍五入IOPS数据
        ss_iops_scalefactor = supporting.get_scale_factor_iops(ss_data_iops_mean)
        ss_data_iops_mean = supporting.scale_yaxis(ss_data_iops_mean, ss_iops_scalefactor)
        ss_data_iops_mean["data"] = supporting.round_metric_series(ss_data_iops_mean["data"])

    # ---------- 构建返回结果 ----------
    # 根据type参数设置y1_axis和y2_axis
    data_options = {
        'iops': scaled_iops_data,
        'lat': scaled_latency_data,
        'bw': scaled_bw_data
    }
    
    # 设置默认值
    datadict["y1_axis"] = scaled_iops_data
    datadict["y2_axis"] = scaled_bw_data
    
    # 如果type是列表且有足够的元素，根据type设置y轴数据
    if isinstance(type, list) and len(type) >= 2:
        if type[0] in data_options and data_options[type[0]]:
            datadict["y1_axis"] = data_options[type[0]]
        if type[1] in data_options and data_options[type[1]]:
            datadict["y2_axis"] = data_options[type[1]]
    
    # 保留CPU数据
    if cpu_sys and cpu_usr:
        datadict["cpu"] = {"cpu_sys": cpu_sys, "cpu_usr": cpu_usr}
    
    # 添加处理后的稳态数据(如果存在)
    if "ss_settings" in datadict.keys() and datadict["ss_settings"]:
        datadict["ss_data_bw_mean"] = ss_data_bw_mean
        datadict["ss_data_iops_mean"] = ss_data_iops_mean

    return datadict


def get_auto_label_font_size(rects):
    size = 0
    number = len(rects)
    if number <= 8:
        size = 8
    if number > 8 and number < 16:
        size = 7
    if number >= 16:
        size = 6 
    return size


def autolabel(rects, axis):
    fontsize = get_auto_label_font_size(rects)

    for rect in rects:
        height = rect.get_height()
        if height < 10:
            formatter = "%.2f"
        else:
            formatter = "%d"
        value = rect.get_x()

        if height >= 10000:
            value = int(round(height / 1000, 0))
            formatter = "%dK"
        else:
            value = height
        axis.text(
            rect.get_x() + rect.get_width() / 2,
            1.015 * height,
            formatter % value,
            ha="center",
            fontsize=fontsize,
        )
