# imgaug为图片添加遮挡和噪声
# 去噪算法
import cv2
from imgaug import augmenters as iaa
import os
import random
import numpy as np


def img_aug(src, dst):
    """
    Add cloud layer and Gaussian noise on the images.

    Args:
        src: source folder path
        dst: destination folder path to save the augmented images

    Returns:

    """
    seq = iaa.Sequential([
        # 确定为此参数
        iaa.CloudLayer(
            intensity_mean=(196, 255),
            intensity_freq_exponent=(-2.0, -1.0),   #
            intensity_coarse_scale=10,
            alpha_min=0,
            alpha_multiplier=(0.5, 0.75),       #
            alpha_size_px_max=(16, 64),          #
            alpha_freq_exponent=(-2.0, -1.0),   #
            sparsity=(1.0, 1.4),
            density_multiplier=(1, 1.2)       #
                ),
        iaa.imgcorruptlike.GaussianNoise(severity=1),
        iaa.imgcorruptlike.ImpulseNoise(severity=1)
    ])

    print('start change!')
    aug_prob = 1
    num_ori = 0
    num_aug = 0
    img_num = 1

    # flag = 0
    for item in os.listdir(src):
        # flag += 1
        # if flag == 20:
        #     break
        # 只对.png结尾图片操作
        if not item.endswith('.png'):
            continue
        # 读取源地址中的图片
        img = cv2.imread(os.path.join(src, item))
        img = [img]
        # 查看目标地址是否有重名图片，有则移除
        if os.path.exists(os.path.join(dst, "%04d.png" % img_num)):
            os.remove(os.path.join(dst, "%04d.png" % img_num))
            print("remove %04d.png" % img_num)
        # 图像增强操作，并保存为.png文件
        if random.random() < aug_prob:
            img_aug = seq.augment_images(img)
            cv2.imwrite(os.path.join(dst, "%04d.png" % img_num), img_aug[0])
            print("save %04d.png successfully" % img_num)
            num_aug += 1
            img_num += 1
        else:
            cv2.imwrite(os.path.join(dst, "%04d.png" % img_num), img[0])
            print("save %04d.png successfully" % img_num)
            num_ori += 1
            img_num += 1

    print('Successfully changed!')
    print('num_ori=%d' % num_ori)
    print('num_aug=%d' % num_aug)


# 定义中值滤波函数
def median_filter(src, dst):
    kernel_size = 5
    print("start read file in %s" % dst)
    for item in os.listdir(src):
        # 检测是否为.png图片文件
        if not item.endswith(".png"):
            print("%s is not .png file and jump over" % item)
            continue
        filename = os.path.join(dst, item)
        if os.path.exists(filename):
            os.remove(filename)
            print("%s already exists and it has been removed" % filename)
        img = cv2.imread(os.path.join(src, item))
        output = cv2.medianBlur(img, kernel_size)
        cv2.imwrite(filename, output)
        print("save %s successfully!" % filename)


# 定义均值滤波函数
def mean_filter(src, dst):
    kernel_size = 5
    kernel = np.ones((kernel_size, kernel_size), np.float32) / kernel_size**2
    print("read file from %s" % src)
    for item in os.listdir(src):
        if not item.endswith(".png"):
            print("%s is not .png file and jump over" % item)
            continue
        # 检查目标文件夹中是否有重名文件
        filename = os.path.join(dst, item)
        if os.path.exists(filename):
            os.remove(filename)
            print("%s is already exists and it has been removed" % filename)
        # 滤波操作
        img = cv2.imread(os.path.join(src, item))
        # cv2.imshow('img', img)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        output = cv2.filter2D(img, -1, kernel)
        cv2.imwrite(filename, output)
        print("save %s successfully!" % filename)


def zmMinFilterGray(src, r=7):
    # 最小值滤波，r是滤波器半径
    return cv2.erode(src, np.ones((2 * r + 1, 2 * r + 1)))


def guidedfilter(I, p, r, eps):
    height, width = I.shape
    m_I = cv2.boxFilter(I, -1, (r, r))
    m_p = cv2.boxFilter(p, -1, (r, r))
    m_Ip = cv2.boxFilter(I * p, -1, (r, r))
    cov_Ip = m_Ip - m_I * m_p

    m_II = cv2.boxFilter(I * I, -1, (r, r))
    var_I = m_II - m_I * m_I

    a = cov_Ip / (var_I + eps)
    b = m_p - a * m_I

    m_a = cv2.boxFilter(a, -1, (r, r))
    m_b = cv2.boxFilter(b, -1, (r, r))
    return m_a * I + m_b


def Defog(m, r, eps, w, maxV1):                 # 输入rgb图像，值范围[0,1]
    '''计算大气遮罩图像V1和光照值A, V1 = 1-t/A'''
    V1 = np.min(m, 2)                           # 得到暗通道图像
    Dark_Channel = zmMinFilterGray(V1, 7)
    # cv2.imshow('20190708_Dark',Dark_Channel)    # 查看暗通道
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    V1 = guidedfilter(V1, Dark_Channel, r, eps)  # 使用引导滤波优化
    bins = 2000
    ht = np.histogram(V1, bins)                  # 计算大气光照A
    d = np.cumsum(ht[0]) / float(V1.size)
    for lmax in range(bins - 1, 0, -1):
        if d[lmax] <= 0.999:
            break
    A = np.mean(m, 2)[V1 >= ht[1][lmax]].max()
    V1 = np.minimum(V1 * w, maxV1)               # 对值范围进行限制
    return V1, A


def _deHaze(m, r=81, eps=0.001, w=0.95, maxV1=0.80, bGamma=False):
    Y = np.zeros(m.shape)
    Mask_img, A = Defog(m, r, eps, w, maxV1)             # 得到遮罩图像和大气光照

    for k in range(3):
        Y[:,:,k] = (m[:,:,k] - Mask_img)/(1-Mask_img/A)  # 颜色校正
    Y = np.clip(Y, 0, 1)
    if bGamma:
        Y = Y ** (np.log(0.5) / np.log(Y.mean()))       # gamma校正,默认不进行该操作
    return Y


def deHaze(src, dst):
    print("start read file in %s" % dst)
    for item in os.listdir(src):
        # 检测原始文件是否为.png图片文件，是才进行转化
        if not item.endswith(".png"):
            print("%s is not .png file and jump over" % item)
            continue
        # 目标文件命名为与原始文件相同的名称
        filename = os.path.join(dst, item)
        if os.path.exists(filename):
            os.remove(filename)
            print("%s already exists and it has been removed" % filename)
        result = _deHaze(cv2.imread(os.path.join(src, item)) / 255.0) * 255
        cv2.imwrite(filename, result)
        print("save %s successfully!" % filename)


def deNoise(src, dst):
    """
    use median_filter, mean_filer and dehaze to the image.
    
    Args:
        src: 
        dst: 

    Returns:

    """
    for item in os.listdir(src):
        # 检测是否为.png图片文件
        if not item.endswith(".png"):
            print("%s is not .png file and jump over" % item)
            continue
        filename = os.path.join(dst, item)
        if os.path.exists(filename):
            os.remove(filename)
            print("%s already exists and it has been removed" % filename)
        img = cv2.imread(os.path.join(src, item))
        # 中值滤波
        output = cv2.medianBlur(img, ksize=5)
        # 均值滤波
        kernel = np.ones((5, 5), np.float32) / 5 ** 2
        output = cv2.filter2D(output, -1, kernel)
        output = _deHaze(output / 255.0) * 255
        cv2.imwrite(filename, output)
        print("save %s successfully!" % filename)


def main():
    img_src = "G:\\dataset\\HRSC2016\\HRSC2016\\FullDataSet\\val_pre"
    img_dst = "G:\\dataset\\HRSC2016\\HRSC2016\\FullDataSet\\val_pre_aug"
    img_aug(img_src, img_dst)
    # median_filter(img_src, img_dst)
    # mean_filter(img_src, img_dst)
    # deHaze(img_src, img_dst)
    # deNoise(img_src, img_dst)


if __name__ == '__main__':
    main()
