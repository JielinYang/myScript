"""
Created on July 8th 2023

@author: yjl
@description：对原始HRSC数据集进行精确分类，要求每种船只类别包含具体的船只型号，如航母包含：Nimitz等。并对各个类别进行统计
"""

import os.path
import xml.etree.ElementTree as ET
import os.path as osp
import json
from shutil import copyfile
import random

base = 'G:/dataset/HRSC2016/HRSC2016/FullDataSet/'
img_path = base + 'AllImages/'
xml_path = base + 'Annotations/'
coco_path_train = base + 'train_pre/HRSC_coco_train_accurate.json'
coco_path_val = base + 'val_pre/HRSC_coco_val_accurate.json'
log_path = './results.log'
info = {'description': 'choose six classes from original HRSC2016. Give up other classes and vague images. Divede train and val dataset by 0.6/0.4 probability for every image. ',
        'url': 'https://www.kaggle.com/datasets/guofeng/hrsc2016', 'version': None,
        'year': 2023, 'contributor': None, 'date_created': 'yjl'}

# 对应：1 2 3 4 5 6六个类别,99为其他类别，不算入
# 分别为航母（航空母舰与攻击舰均算入）、巡洋舰、驱逐舰、护卫舰、补给舰（航母油、装备补给舰和运输舰）、潜艇
true_lab = ['aircraft_carrier', 'cruiser', 'destroyer', 'corvette', 'depot', 'submarine']
label_warp = {'100000001': 99,
              '100000002': 1,   # 航母大类
              '100000003': 99,
              '100000004': 99,
              '100000005': 1,   # 航母：Nimitz
              '100000006': 1,   # 航母：Nimitz
              '100000007': 3,   # 驱逐：ArleiguBurke
              '100000008': 5,   # 运输：WhidbeyIsland
              '100000009': 4,   # 护卫：Perry
              '100000010': 5,   # 运输：Sanantonio
              '100000011': 2,   # 巡洋：Ticonderoga
              '100000012': 1,   # 航母：Nimitz
              '100000013': 1,   # 航母：Nimitz
              '100000014': 99,
              '100000015': 5,   # 运输：Austin
              '100000016': 1,   # 航母：Tarawa
              '100000017': 99,
              '100000018': 99,
              '100000019': 5,   # 运输：包含多类
              '100000020': 99,  # 无21
              '100000022': 99,  # 无23
              '100000024': 99,
              '100000025': 99,
              '100000026': 99,
              '100000027': 6,   # 潜艇
              '100000028': 99,
              '100000029': 99,
              '100000030': 99,
              '100000031': 99,
              '100000032': 1,   # 航母：Midway
              '100000033': 99,
              }
vague_img = [7, 684, 1111, 1112, 1113, 1114, 1115, 1145, 1146, 1147, 1240]


# 定义判断xml是否有需要类别的函数：
def valid_target(root) -> bool:
    """
    
    Args:
        root: xml ET.parse().getroot object

    Returns: bool value represents if the xml file own the target we need and if the image is clear

    """
    img_id = int(root.find('Img_ID').text[-4:])
    if img_id in vague_img:
        return False
    for child in root.findall('HRSC_Objects/HRSC_Object'):
        cla = label_warp[child.find('Class_ID').text]
        if 1 <= cla <= 6:
            return True
    return False


def classStatistics(xml_root: str) -> dict:
    """
    Count category in every image and total number of every category.

    Args:
        xml_root: annotations folder path with .xml format files in it

    Returns: dict(img_vs_cls=dict, cls_statistics=dict)
        img_vs_cls: key represents the image id and value represents the category(list) contained in this image. For example '100000622':[4, 5]
        cls_statistics: key represents the category and value represents the total numbers in dataset. For example '1':300, it means the category 'aircraft_carrier' has number of 300.

    """

    img_vs_cls = {}      # 统计包含目标的图片所包含的类别
    cls_statistics = []     # 用于统计各类别及数量

    # 统计图片编号和对应类别类别，以及各类别数量
    for fp in os.listdir(xml_root):
        if fp.split('.')[-1] != 'xml':
            continue
        root = ET.parse(osp.join(xml_path, fp)).getroot()
        if valid_target(root):
            Img_ID = root.find('Img_ID').text
            img_vs_cls[Img_ID] = []
            for child in root.findall('HRSC_Objects/HRSC_Object'):
                ori_cla = child.find('Class_ID').text
                cls_statistics.append(label_warp[ori_cla])
                img_vs_cls[Img_ID].append(label_warp[ori_cla])
    # 统计每个类别的数量
    cls_statistics = {i : cls_statistics.count(i) for i in set(cls_statistics)}
    return dict(img_vs_cls=img_vs_cls, cls_statistics=cls_statistics)


def xml2coco():
    """
    Choose images which contain 6 kind of category from original HRSC dataset, remove vague images. Making new train/val datasets and coco format annotation file.

    Args:

    """
    # coco数据集所需要的图片、标注和类别，其格式为：{'images':[image], 'annotations':[annotation], 'category':[category]}
    images_coco_train = list()
    images_coco_val = list()
    annotations_coco_train = list()
    annotations_coco_val = list()
    class_names = list()
    # 定义图像和标注序号
    img_train_index = 0
    img_val_index = 0
    ann_train_index = 1
    ann_val_index = 1
    # 标志位，如果为True表示该图像设为训练集，否则设置为测试集
    train_flag = None

    # 程序日志
    if osp.exists(log_path):
        os.remove(log_path)
    # 遍历整个xml folder
    for fp in os.listdir(xml_path):
        # 跳过非xml文件
        if fp.split('.')[-1] != 'xml':
            continue
        # 得到当前.xml文件根节点
        root = ET.parse(osp.join(xml_path, fp)).getroot()
        # 判断图片是否有效
        if valid_target(root):
            # 图片有效则产生标志位，判断图片属于训练集还是测试集
            train_flag = True if random.random() < 0.6 else False
            img = fp.split('.')[0] + '.bmp'
            # 判断.xml文件有无对应的.bmp文件，有则复制到新文件夹
            if osp.exists(img_path + img):
                src = img_path + img
                if train_flag:
                    img_train_index += 1
                    dst_train = base + 'train_pre/%04.d.png' % img_train_index
                    copyfile(src, dst_train)
                else:
                    img_val_index += 1
                    dst_val = base + 'val_pre/%04.d.png' % img_val_index
                    copyfile(src, dst_val)
            else:
                print('xml文件找不到对应图像，编号：%s' % fp)

            # 创建coco数据集中img部分
            images_dict = {}
            images_dict['file_name_ori'] = root.find('Img_ID').text + '.bmp'
            images_dict['height'] = float(root.find('Img_SizeHeight').text)
            images_dict['width'] = float(root.find('Img_SizeWidth').text)
            if train_flag:
                images_dict['file_name'] = '%04.d.png' % img_train_index
                images_dict['id'] = img_train_index
                images_coco_train.append(images_dict)
            else:
                images_dict['file_name'] = '%04.d.png' % img_val_index
                images_dict['id'] = img_val_index
                images_coco_val.append(images_dict)

            # 创建coco数据集中anno部分
            for child in root.findall('HRSC_Objects/HRSC_Object'):
                if label_warp[child.find('Class_ID').text] == 99:
                    continue
                annotations_dict = dict()
                annotations_dict['iscrowd'] = 0
                xmin = float(child.find('box_xmin').text)
                ymin = float(child.find('box_ymin').text)
                xmax = float(child.find('box_xmax').text)
                ymax = float(child.find('box_ymax').text)
                # 如果边框有问题，输出错误报告
                if xmin < 0 or xmin >= xmax or ymin < 0 or ymin >= ymax or \
                        xmax > images_dict['width'] or ymax > images_dict['height']:
                    with open(log_path, 'a+') as f:
                        f.write('box error! ' + fp + ' xmin: ' + str(xmin) + ' ymin: ' + str(ymin) + ' xmax: ' + str(xmax) + ' ymax: ' + str(ymax) + '/n')
                    print(fp, ' xmin: ', xmin, ' ymin: ', ymin, ' xmax: ', xmax, ' ymax: ', ymax)
                    # 边框有问题---------------------------------------
                    continue
                annotations_dict['bbox'] = [xmin, ymin, xmax - xmin, ymax - ymin]  # x1, y1, w, h
                annotations_dict['category_id'] = label_warp[child.find('Class_ID').text]
                annotations_dict['area'] = annotations_dict['bbox'][2] * annotations_dict['bbox'][3]
                if train_flag:
                    annotations_dict['id'] = ann_train_index
                    annotations_dict['image_id'] = img_train_index
                    annotations_coco_train.append(annotations_dict)
                    ann_train_index += 1
                else:
                    annotations_dict['id'] = ann_val_index
                    annotations_dict['image_id'] = img_val_index
                    annotations_coco_val.append(annotations_dict)
                    ann_val_index += 1

    # 创建coco数据集中category部分
    categories = list()
    count = 1
    for name in true_lab:
        mydict = dict()
        mydict['id'] = count
        mydict['name'] = name
        categories.append(mydict)
        count += 1

    # 打印类别信息，并保存标注的json文件
    print('class_names:', class_names, ' len of train_images_coco:', len(images_coco_train))
    print('class_names:', class_names, ' len of val_images_coco:', len(images_coco_val))

    # 创建总的coco数据集
    data_train = {'info': info, 'images': images_coco_train, 'annotations': annotations_coco_train, 'categories': categories}
    data_val = {'info': info, 'images': images_coco_val, 'annotations': annotations_coco_val, 'categories': categories}
    if osp.exists(coco_path_train):
        os.remove(coco_path_train)
        print('remove original file:', coco_path_train)
    if osp.exists(coco_path_val):
        os.remove(coco_path_val)
        print('remove original file:', coco_path_val)
    with open(coco_path_train, "w") as f:
        json.dump(data_train, f)
        print('save %s successfully!' % coco_path_train)
    with open(coco_path_val, "w") as f:
        json.dump(data_val, f)
        print('save %s successfully!' % coco_path_val)


if __name__ == '__main__':
    result = classStatistics(xml_path)
    xml2coco()
