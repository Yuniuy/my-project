# 数据可视化工具 (Data Visualization Tool)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)

上传自己的数据，一键生成各种可视化图表。

## 功能

- 支持上传 **CSV / Excel** 数据文件（自动识别 UTF-8 / GBK 编码）
- 数据预览：数据表、统计摘要、缺失值检查
- 8 种图表：柱状图、折线图、散点图、饼图、直方图、箱线图、面积图、相关性热力图
- 生成的图表可一键下载为 PNG
- 没有任何数据时，可使用内置示例数据体验

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

### 3. 使用

1. 在左侧边栏上传 CSV 或 Excel 文件（或勾选「用内置示例试试」）
2. 在「数据预览」中确认数据读取正确
3. 选择图表类型，配置 X 轴 / Y 轴
4. 点击「下载这张图」保存 PNG

## 依赖

- Python 3.9+
- streamlit
- pandas
- matplotlib
- openpyxl（用于读取 .xlsx）

## 目录结构

```
my project/
├── app.py              # 主程序
├── requirements.txt    # 依赖清单
├── VERSION             # 版本号
├── README.md
├── LICENSE
└── .gitignore
```

## 更新日志

### v1.0.0 (2026-10-07)

首个正式版本。

- 支持上传 CSV / Excel 数据文件（自动识别 UTF-8 / GBK 编码）
- 数据预览：数据表、统计摘要、数据类型与缺失值检查
- 8 种图表：柱状图、折线图、散点图、饼图、直方图、箱线图、面积图、相关性热力图
- 图表支持一键导出 PNG
- 内置示例数据，无数据时也可体验

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
