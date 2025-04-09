import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.optimize import curve_fit

colors = [
    (0.0, 0.0, 1.0),  # 蓝
    (0.0, 1.0, 0.0),  # 绿
    (1.0, 1.0, 0.0),  # 黄
    (1.0, 0.5, 0.0),  # 橙
    (1.0, 0.0, 0.0),  # 红
]

# 创建自定义颜色映射
custom_cmap = LinearSegmentedColormap.from_list(
    "rainbow_custom", colors, N=256
)

def load_excel():
    # 1. 读取 CSV 数据（假设文件名为 data.csv）
    file_path = "./20250305pressure_data20250226_3.39_10v_2.csv"
    df = pd.read_csv(
        file_path,
        # header=None,       # 不将第一行识别为列名
        sep=",",  # 分隔符（默认是逗号，可根据文件调整）
        encoding="utf-8",  # 编码格式（如文件含中文，可改为 'gbk'）
        skipinitialspace=True,  # 忽略分隔符后的空格
        nrows=80  # 读取前 80 行（若 CSV 无多余行可省略）
    )

    # 2. 转换为数值矩阵并处理缺失值
    data = df.iloc[:, :80].values.astype(float)  # 确保读取前 80 列
    data = np.nan_to_num(data)  # 将 NaN 替换为 0
    data = np.sqrt(data)

    # 3. 绘制热力图
    plt.figure()
    heatmap = plt.imshow(
        data,
        cmap=custom_cmap,  # 关键参数：颜色映射设为 'RdBu_r' 或 'bwr'
        aspect='auto',
        vmin=np.min(data),
        vmax=np.max(data)
    )
    plt.colorbar(heatmap, label='Value')

    # 设置标题和坐标轴
    plt.title("80x80 CSV Data Heatmap", fontsize=14)
    plt.xlabel("Column Index", fontsize=12)
    plt.ylabel("Row Index", fontsize=12)

    # 显示图形
    plt.tight_layout()
    plt.show()


def plot_standard():
    # 参数设置
    A = 0.0217  # 正弦幅值
    omega = 2 * np.pi / 18.2  # 角速度

    # 生成原始 x0 和调制后的 x 值
    x0 = np.linspace(0, 80, 80)
    x = A * np.sin(omega * x0)  # x 轴按正弦函数调制
    x = np.abs(x)

    # 生成 data
    data = np.tile(x, (80, 1))

    # 生成逐渐增强的随机噪声
    np.random.seed(42)  # 固定随机种子（可删除以生成随机效果）
    noise = np.random.uniform(low=-A/3, high=A/3, size=(80, 80))
    data += noise
    data[data < 0] = 0
    # 绘制热力图
    plt.figure()
    heatmap = plt.imshow(
        data,
        cmap=custom_cmap,  # 关键参数：颜色映射设为 'RdBu_r' 或 'bwr'
        aspect='auto',
        vmin=np.min(data),
        vmax=np.max(data)
    )
    plt.colorbar(heatmap, label='Value')

    # 设置标题和坐标轴
    plt.title("80x80 CSV Data Heatmap", fontsize=14)
    plt.xlabel("Column Index", fontsize=12)
    plt.ylabel("Row Index", fontsize=12)

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    plot_standard()
