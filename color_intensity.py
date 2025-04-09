import numpy as np
import matplotlib.pyplot as plt

# 生成平面坐标点
x = np.linspace(0, 80, 80)
y = np.linspace(0, 80, 80)
X, Y = np.meshgrid(x, y)

# 生成与X, Y无关的0-100随机数
np.random.seed(42)  # 设置随机种子，确保结果可复现
Z = np.random.uniform(0, 100, size=X.shape)  # 生成0-100之间的均匀分布随机数

# 绘制热力图
plt.figure()
heatmap = plt.pcolormesh(X, Y, Z, cmap='viridis', shading='auto', vmin=0, vmax=100)
plt.colorbar(heatmap, label='Value (0-100)')

# 绘制坐标系
plt.title('Random Color Intensity (0-100)')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True, linestyle='--', alpha=0.5)
# plt.axhline(0, color='black', linewidth=0.5)
# plt.axvline(0, color='black', linewidth=0.5)
plt.show()
