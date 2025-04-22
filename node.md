# fio-plot项目使用手册

fio-plot是一套用于存储设备性能基准测试和可视化的工具集。它包含两个主要工具：**bench_fio**用于自动化运行FIO测试并收集数据，以及**fio_plot**用于将测试数据生成各种可视化图表。

## 简介

[FIO](https://github.com/axboe/fio)是用于存储设备基准测试的工具，可评估存储性能的IOPS和延迟。fio-plot项目可处理FIO的JSON输出文件和CSV日志文件，生成各种图表。使用bench_fio可以自动化基准测试过程。

![2D图表示例][2dchartiodepth]

使用这些工具的基本流程：
1. 使用bench_fio运行测试
2. 确定需要展示的信息
3. 使用fio-plot根据命令行选项生成图片

[2dchartiodepth]: https://louwrentius.com/static/images/fio-plot/fioplot0001.png

## 安装方法

Ubuntu 18.04+需要先运行：
```bash
apt install zlib1g-dev libjpeg-dev python3-pip
```

所有操作系统：
```bash
pip3 install fio-plot
```

如果不希望全局安装，可以使用虚拟环境：
```bash
cd /目标/路径
python3 -m venv fio-plot
source fio-plot/bin/activate
pip3 install fio-plot
```

## bench_fio工具

### 简介
bench_fio是自动执行多个不同参数基准测试的脚本，可测试不同队列深度和/或并发任务数，并显示实时进度。

### 特点
- 支持[FIO"稳态"特性](https://github.com/axboe/fio/blob/master/examples/steadystate.fio)，当达到所需稳态一段时间后自动停止测试
- 支持SSD预处理作业，可在进行实际基准测试前运行，甚至可以在每次基准测试后重复运行
- 支持对多个设备进行并行测试
- 支持Fio客户端/服务器模式，可在远程主机上执行测试

### 使用示例

测试两个设备的随机读/写性能：
```bash
./bench_fio --target /dev/md0 /dev/md1 --type device --mode randread randwrite --output RAID_ARRAY --destructive
```

测试一个设备，使用自定义队列深度和任务数：
```bash
./bench_fio --target /dev/md0 --type device --mode randread randwrite --output RAID_ARRAY --iodepth 1 8 16 --numjobs 8 --destructive
```

使用稳态特性进行测试：
```bash
./bench_fio --target /dev/sda --type device -o test -m randwrite --loops 1 --iodepth 1 8 16 32 --numjobs 1 --ss iops:0.1% --ss-ramp 10 --ss-dur 20 --runtime 60 --destructive
```

### INI配置文件支持

除了命令行参数外，bench_fio还支持使用INI格式配置文件：
```bash
./bench_fio /path/to/benchmark.ini
```

配置示例：
```ini
[benchfio]
target = /dev/example
output = benchmark
type = device
mode = randread,randwrite
size = 10G
iodepth = 1,2,4,8,16,32,64
numjobs = 1,2,4,8,16,32,64
direct = 1
engine = libaio
precondition = False
precondition_repeat = False
extra_opts = norandommap=1,refill_buffers=1
runtime = 60
destructive = False
```

### 输出结构
基准测试数据包括两种类型：
1. Fio .json输出
2. Fio .log输出（日志数据）

输出目录结构示例：
```
RAID_ARRAY/ <-- 输出文件夹
└── md0 <-- 设备
    ├── randrw75 <-- 混合负载（读比例%）
    │   ├── 4k <-- 块大小
    │   │   ├── randrw-16-8.json
    │   │   ├── randrw-1-8.json
    │   │   ├── randrw-8-8.json
    │   └── 8k <-- 块大小
    │       ├── randrw-16-8.json
    │       ├── randrw-1-8.json
    │       ├── randrw-8-8.json
    └── randrw90
        ├── 4k
        │   ├── randrw-16-8.json
        │   ├── randrw-1-8.json
        │   ├── randrw-8-8.json
        └── 8k
            ├── randrw-16-8.json
            ├── randrw-1-8.json
            ├── randrw-8-8.json
```

## fio_plot工具

### 简介
fio_plot用于从FIO基准测试数据生成图表，可处理JSON格式输出和CSV日志文件。

### 配置方式
fio_plot支持通过命令行或INI配置文件配置：

使用INI文件：
```bash
fio-plot /path/to/fio-plot.ini
```

### 图表类型

#### 2D图表（队列深度）
显示不同队列深度的IOPS和延迟：

![2D图表（队列深度）][2dchartiodepth]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610 --source "https://louwrentius.com" -T "INTEL D3-S4610 SSD on IBM M1015" -l -r randread
```

#### 2D图表（任务数）
显示不同并发任务数的IOPS和延迟：

![2D图表（任务数）][2dchartnumjobs]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610 --source "https://louwrentius.com" -T "INTEL D3-S4610 SSD on IBM M1015" -N -r randread
```

[2dchartnumjobs]: https://louwrentius.com/static/images/fio-plot/fioplot0002.png

#### 比较图表
在一个图表中比较多个基准测试结果：

![比较图表][2dchartcompare]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610 SAMSUNG_860_PRO KINGSTON_DC500M SAMSUNG_PM883 --source "https://louwrentius.com" -T "Comparing the performance of various Solid State Drives" -C -r randread --xlabel-parent 0
```

可以对IOPS和延迟进行分组：

![分组比较图表][2dchartcomparegroup]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610 SAMSUNG_860_PRO KINGSTON_DC500M SAMSUNG_PM883 --source "https://louwrentius.com" -T "Comparing the performance of various Solid State Drives" -C -r randread --xlabel-parent 0 --group-bars
```

[2dchartcompare]: https://louwrentius.com/static/images/fio-plot/fioplot0003.png
[2dchartcomparegroup]: https://louwrentius.com/static/images/fio-plot/fioplot0004.png

#### 3D图表
将队列深度和任务数同时绘制成3D柱状图：

IOPS示例：

![3D IOPS图表][3dbarchartiops]

命令示例：
```bash
fio-plot -i RAID10 --source "https://louwrentius.com" -T "RAID10 performance of 8 x WD Velociraptor 10K RPM" -L -t iops -r randread
```

延迟示例：

![3D延迟图表][3dbarchartlat]

命令示例：
```bash
fio-plot -i RAID10 --source "https://louwrentius.com" -T "RAID10 performance of 8 x WD Velociraptor 10K RPM" -L -t lat -r randread
```

[3dbarchartiops]: https://louwrentius.com/static/images/fio-plot/fioplot0005.png
[3dbarchartlat]: https://louwrentius.com/static/images/fio-plot/fioplot0006.png

#### 线图（基于FIO日志数据）
基于时间绘制性能指标，例如多个SSD的IOPS比较：

![IOPS线图][linegraph01]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610/ KINGSTON_DC500M/ SAMSUNG_PM883/ SAMSUNG_860_PRO/ --source "https://louwrentius.com" -T "Comparing IOPs performance of multiple SSDs" -g -t iops -r randread --xlabel-parent 0
```

延迟线图：

![延迟线图][linegraph02]

命令示例：
```bash
fio-plot -i INTEL_D3-S4610/ KINGSTON_DC500M/ SAMSUNG_PM883/ SAMSUNG_860_PRO/ --source "https://louwrentius.com" -T "Comparing latency performance of multiple SSDs" -g -t lat -r randread --xlabel-parent 0
```

[linegraph01]: https://louwrentius.com/static/images/fio-plot/fioplot0012.png
[linegraph02]: https://louwrentius.com/static/images/fio-plot/fioplot0013.png

#### 延迟直方图
显示不同延迟分布的直方图：

![延迟直方图][histogram01]

命令示例：
```bash
fio-plot -i SAMSUNG_860_PRO/ --source "https://louwrentius.com" -T "Historgram of SSD" -H -r randread -d 16 -n 16
```

[histogram01]: https://louwrentius.com/static/images/fio-plot/fioplot0011.png

### PNG元数据
所有用于生成PNG文件的设置都作为元数据嵌入到PNG文件中（tEXT），可以使用ImageMagick查看：

```bash
identify -verbose filename.png
```

## 注意事项

1. JSON/LOG文件名要求格式为：
   ```
   [rwmode]-iodepth-[iodepth]-numjobs-[numjobs]_[fio generated type].[numbjob job id].log
   ```

2. 使用SSD预处理很重要，特别是在测试SSD性能时，应先进行预处理以获得更真实的性能数据

3. 关于IO队列深度和任务数：如果qd=1且nj=5，将有5个IO在进行中；如果qd=4且nj=4，将有4×4=16个IO在进行中

4. fio-plot需要matplotlib（至少3.3.0版本）和numpy库支持
