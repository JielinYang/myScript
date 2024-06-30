"""
Created on Tues Mar 28 2023
用于创建新的含六类目标的数据集，包含图像重新移动+命令，标签重新创建
@author: yjl
"""

import os.path
import xml.etree.ElementTree as ET
import os.path as osp
import json
from shutil import copyfile

base = 'G:/dataset/HRSC2016/HRSC2016/FullDataSet/'
img_path = base + 'AllImages/'
xml_path = base + 'Annotations/'
coco_path_train = base + 'new_train/HRSC_coco_train.json'
coco_path_val = base + 'new_val/HRSC_coco_val.json'
log_path = './results.log'
info = {'description': 'choose six classes from HRSC2016 and give up other classes ',
        'url': 'https://www.kaggle.com/datasets/guofeng/hrsc2016', 'version': None,
        'year': 2023, 'contributor': None, 'date_created': None}
# 对应：1 2 3 4 5 6六个类别,99为其他类别，不算入
# 分别为航母（航空母舰与攻击舰均算入）、巡洋舰、驱逐舰、护卫舰、补给舰（航母油、装备补给舰和运输舰）、潜艇
true_lab = ['aircraft_carrier', 'cruiser', 'destroyer', 'corvette', 'depot', 'submarine']
label_warp = {'100000001': 99,
              '100000002': 1,
              '100000003': 99,
              '100000004': 99,
              '100000005': 1,
              '100000006': 1,
              '100000007': 3,
              '100000008': 5,
              '100000009': 4,
              '100000010': 5,
              '100000011': 2,
              '100000012': 1,
              '100000013': 1,
              '100000014': 99,
              '100000015': 5,
              '100000016': 1,
              '100000017': 99,
              '100000018': 99,
              '100000019': 99,
              '100000020': 99,  # 无21
              '100000022': 99,  # 无23
              '100000024': 99,
              '100000025': 99,
              '100000026': 99,
              '100000027': 6,
              '100000028': 99,
              '100000029': 99,
              '100000030': 99,
              '100000031': 99,
              '100000032': 1,
              '100000033': 99,
              }

# 定义判断xml是否有需要类别的函数：
def own_target(root):
    for child in root.findall('HRSC_Objects/HRSC_Object'):
        cla = label_warp[child.find('Class_ID').text]
        if 1 <= cla <= 6:
            return True
    return False

img_class = {}
class_calc = []
# 统计图片编号和对应类别类别，以及各类别数量
for fp in os.listdir(xml_path):
    if fp.split('.')[-1] != 'xml':
        continue
    root = ET.parse(osp.join(xml_path, fp)).getroot()
    if own_target(root):
        Img_ID = root.find('Img_ID').text
        img_class[Img_ID] = []
        for child in root.findall('HRSC_Objects/HRSC_Object'):
            ori_cla = child.find('Class_ID').text
            class_calc.append(label_warp[ori_cla])
            img_class[Img_ID].append(label_warp[ori_cla])
# 统计每个类别的数量
class_calc2 = {i : class_calc.count(i) for i in set(class_calc)}

# 训练集测试集大小
train_size = int(0.6 * len(img_class))
val_size = int(0.4 * len(img_class))
# coco数据集的图像和标注
images_coco_train = list()
images_coco_val = list()
annotations_coco_train = list()
annotations_coco_val = list()
# 定义图像和标注序号
img_index = 0
ann_index = 1
class_names = list()

# 判断xml文件中是否有六类目标，如果有则复制对象图像创建新数据集，并生成标注文件
if osp.exists(log_path):
    os.remove(log_path)
for fp in os.listdir(xml_path):
    # 判断标签是否重置
    if img_index == train_size:
        ann_index = 1
    # 跳过非xml文件
    if fp.split('.')[-1] != 'xml':
        continue
    root = ET.parse(osp.join(xml_path, fp)).getroot()
    if own_target(root):
        # 如果图像中具有六类目标之一，则复制图像到新文件夹，并设置标注。
        img = fp.split('.')[0] + '.bmp'
        if osp.exists(img_path + img):
            img_index += 1
            src = img_path + img
            if img_index <= train_size:
                dst_train = base + 'new_train/%04.d.bmp' % img_index
                copyfile(src, dst_train)
            else:
                dst_val = base + 'new_val/%04.d.bmp' % (img_index - train_size)
                copyfile(src, dst_val)
        else:
            print('xml文件找不到对应图像，编号：%s' % fp)

        # 创建coco数据集中img部分
        images_dict = {}
        images_dict['file_name_ori'] = root.find('Img_ID').text + '.bmp'
        images_dict['height'] = float(root.find('Img_SizeHeight').text)
        images_dict['width'] = float(root.find('Img_SizeWidth').text)
        if img_index <= train_size:
            images_dict['file_name'] = '%04.d.bmp' % img_index
            images_dict['id'] = img_index
            images_coco_train.append(images_dict)
        else:
            images_dict['file_name'] = '%04.d.bmp' % (img_index - train_size)
            images_dict['id'] = img_index - train_size
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
                    f.write('box error! ' + fp + ' ann_index: ' + str(ann_index) + ' xmin: ' + str(xmin) + ' ymin: ' +
                            str(ymin) + ' xmax: ' + str(xmax) + ' ymax: ' + str(ymax) + '/n')
                print(fp, ' ann_index:', ann_index, ' xmin: ', xmin, ' ymin: ', ymin, ' xmax: ', xmax, ' ymax: ', ymax)
                # 边框有问题---------------------------------------
                continue
            annotations_dict['bbox'] = [xmin, ymin, xmax - xmin, ymax - ymin]  # x1, y1, w, h
            annotations_dict['category_id'] = label_warp[child.find('Class_ID').text]
            annotations_dict['id'] = ann_index
            ann_index += 1
            annotations_dict['area'] = annotations_dict['bbox'][2] * annotations_dict['bbox'][3]
            if img_index <= train_size:
                annotations_dict['image_id'] = img_index
                annotations_coco_train.append(annotations_dict)
            else:
                annotations_dict['image_id'] = img_index - train_size
                annotations_coco_val.append(annotations_dict)

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
print('class_names:', class_names, ' len of images_coco:', len(images_coco_train))
print('class_names:', class_names, ' len of images_coco:', len(images_coco_val))
data_train = {'info': info, 'images': images_coco_train, 'annotations': annotations_coco_train,
              'categories': categories}
data_val = {'info': info, 'images': images_coco_val, 'annotations': annotations_coco_val,
              'categories': categories}
if osp.exists(coco_path_train):
    os.remove(coco_path_train)
if osp.exists(coco_path_val):
    os.remove(coco_path_val)
with open(coco_path_train, "w") as f:
    json.dump(data_train, f)
with open(coco_path_val, "w") as f:
    json.dump(data_val, f)
print('succeed!')