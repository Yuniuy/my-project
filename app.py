"""
数据可视化 Web 应用
上传自己的数据（CSV / Excel），一键生成各种可视化图表。

运行方式：
    streamlit run app.py
"""

import io

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

matplotlib.use("Agg")

# 让 matplotlib 正常显示中文
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# ---------------------------------------------------------------- 页面配置
st.set_page_config(
    page_title="数据可视化工具",
    page_icon="📊",
    layout="wide",
)

st.title("📊 数据可视化工具")
st.caption("上传你自己的 CSV / Excel 数据，一键生成各种图表")


# ---------------------------------------------------------------- 读取数据
@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """根据文件后缀读取 CSV 或 Excel。"""
    if filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    # CSV 自动尝试常见编码
    for encoding in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
        try:
            return pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("无法识别 CSV 文件编码，请另存为 UTF-8 后重试。")


# ---------------------------------------------------------------- 侧边栏：上传
with st.sidebar:
    st.header("① 上传数据")
    uploaded = st.file_uploader(
        "选择 CSV 或 Excel 文件",
        type=["csv", "xlsx", "xls"],
        help="支持逗号分隔的 csv，以及 xlsx / xls 表格",
    )
    st.divider()
    st.header("② 示例数据")
    use_demo = st.checkbox("没有数据？用内置示例试试", value=False)

# ---------------------------------------------------------------- 数据准备
df: pd.DataFrame | None = None

if uploaded is not None:
    try:
        df = load_data(uploaded.getvalue(), uploaded.name)
        st.success(f"已加载：**{uploaded.name}** — {df.shape[0]} 行 × {df.shape[1]} 列")
    except Exception as exc:  # noqa: BLE001
        st.error(f"读取失败：{exc}")
elif use_demo:
    df = pd.DataFrame(
        {
            "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "销售额": [120, 156, 98, 210, 175, 240],
            "利润": [30, 42, 18, 65, 48, 80],
            "地区": ["华东", "华北", "华东", "华南", "华北", "华东"],
        }
    )
    st.info("正在使用内置示例数据")

if df is None:
    st.info("👈 请在左侧上传数据，或勾选「用内置示例试试」")
    st.stop()

# ---------------------------------------------------------------- 数据预览
with st.expander("📋 数据预览", expanded=True):
    tab1, tab2, tab3 = st.tabs(["数据表", "统计摘要", "数据类型"])
    with tab1:
        st.dataframe(df.head(100), use_container_width=True)
        st.caption(f"共 {df.shape[0]} 行，仅展示前 100 行")
    with tab2:
        st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
    with tab3:
        st.dataframe(
            pd.DataFrame(
                {
                    "列名": df.columns,
                    "类型": [str(t) for t in df.dtypes],
                    "缺失值": df.isna().sum().values,
                    "唯一值数": [df[c].nunique() for c in df.columns],
                }
            ),
            use_container_width=True,
        )

# ---------------------------------------------------------------- 绘图区
st.divider()
st.subheader("③ 选择图表类型")

chart_type = st.selectbox(
    "图表类型",
    [
        "柱状图 Bar",
        "折线图 Line",
        "散点图 Scatter",
        "饼图 Pie",
        "直方图 Histogram",
        "箱线图 Box",
        "面积图 Area",
        "相关性热力图 Heatmap",
    ],
)

numeric_cols = df.select_dtypes(include="number").columns.tolist()
all_cols = df.columns.tolist()


def pick_xy():
    """通用的 X / Y 选择器。"""
    c1, c2 = st.columns(2)
    with c1:
        x = st.selectbox("X 轴（分类/横轴）", all_cols, index=0)
    with c2:
        default_y = numeric_cols.index(numeric_cols[0]) if numeric_cols else 0
        y = st.selectbox(
            "Y 轴（数值/纵轴）",
            numeric_cols if numeric_cols else all_cols,
            index=default_y,
        )
    return x, y


fig, ax = plt.subplots(figsize=(9, 4.5))
ok = True

if chart_type.startswith("柱状图"):
    x, y = pick_xy()
    ax.bar(df[x].astype(str), df[y])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

elif chart_type.startswith("折线图"):
    x, y = pick_xy()
    ax.plot(df[x].astype(str), df[y], marker="o")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(alpha=0.3)

elif chart_type.startswith("散点图"):
    x, y = pick_xy()
    ax.scatter(df[x], df[y], alpha=0.6)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.grid(alpha=0.3)

elif chart_type.startswith("饼图"):
    if not numeric_cols:
        st.warning("数据中没有数值列，无法绘制饼图。")
        ok = False
    else:
        label_col = st.selectbox("标签列", all_cols, index=0)
        value_col = st.selectbox("数值列", numeric_cols, index=0)
        data = df.groupby(label_col)[value_col].sum().nlargest(10)
        ax.pie(data.values, labels=data.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")

elif chart_type.startswith("直方图"):
    if not numeric_cols:
        st.warning("数据中没有数值列，无法绘制直方图。")
        ok = False
    else:
        col = st.selectbox("选择数值列", numeric_cols)
        bins = st.slider("分箱数量", 5, 100, 20)
        ax.hist(df[col].dropna(), bins=bins, edgecolor="white")
        ax.set_xlabel(col)
        ax.set_ylabel("频数")

elif chart_type.startswith("箱线图"):
    if not numeric_cols:
        st.warning("数据中没有数值列，无法绘制箱线图。")
        ok = False
    else:
        cols = st.multiselect("选择数值列（可多选）", numeric_cols, default=numeric_cols[:1])
        if cols:
            ax.boxplot([df[c].dropna() for c in cols], labels=cols)
            ax.grid(alpha=0.3)
        else:
            st.warning("请至少选择一列。")
            ok = False

elif chart_type.startswith("面积图"):
    x, y = pick_xy()
    ax.fill_between(range(len(df)), df[y], alpha=0.5)
    ax.plot(range(len(df)), df[y])
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df[x].astype(str), rotation=45, ha="right")
    ax.set_ylabel(y)

elif chart_type.startswith("相关性"):
    if len(numeric_cols) < 2:
        st.warning("至少需要 2 个数值列才能计算相关性。")
        ok = False
    else:
        corr = df[numeric_cols].corr()
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(corr)))
        ax.set_yticklabels(corr.columns)
        for i in range(len(corr)):
            for j in range(len(corr)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, shrink=0.8)

if ok:
    st.pyplot(fig, use_container_width=True)

    # 下载图片
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        "⬇️ 下载这张图（PNG）",
        data=buf,
        file_name="chart.png",
        mime="image/png",
    )

plt.close(fig)

st.divider()
st.caption("基于 Streamlit + pandas + matplotlib 构建")
