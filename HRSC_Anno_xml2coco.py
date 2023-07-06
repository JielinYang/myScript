#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Mar 28 2023

@author: yjl
"""

import os
import os.path
import xml.etree.ElementTree as ET
import os.path as osp
import json
# import re
# import numpy as np
dirpath = './'
xml_paths = ['G:/dataset/HRSC2016/HRSC2016/FullDataSet/Annotations']
coco_path = 'G:/dataset/HRSC2016/HRSC2016/FullDataSet/Annotations/HRSC_coco.json'
# img_path = dirpath+'HRSC_Images'
log_path = dirpath+'results.log'
info = {'description': 'HRSC2016', 'url': 'https://www.kaggle.com/datasets/guofeng/hrsc2016', 'version': None,
        'year': 2023, 'contributor': None, 'date_created': None}

# true_lab = ['ship', 'aircraft_carrier', 'warcraft', 'merchant_ship']    # 对应：1 2 3 4
true_lab = ['ship', 'aircraft_carrier', 'warcraft', 'merchant_ship', 'Nimitz',
            '6', 'ArleighBurke', 'WhidbeyIsland', 'Perry', 'Sanantonio',
            'Ticonderoga', '12few', '13', '14null', 'Austen',
            'Tarawa', '17few', 'Container', 'CommanderA', 'CarcarrierA',
                       '22',                '24', 'ContainerA',
            '26', 'submarine', 'lowa', 'Medical', 'CarcarrierB',
            '31null', 'Midway', '33null']
# true_lab = ['aircraft_carrier', 'cruiser', 'destroyer', 'corvette', 'depot', 'submarine', 'others']
# label_warp = {'100000001': 1,
#               '100000002': 2,
#               '100000003': 3,
#               '100000004': 4,
#               '100000005': 2,
#               '100000006': 2,
#               '100000007': 3,
#               '100000008': 3,
#               '100000009': 3,
#               '100000010': 3,
#               '100000011': 3,
#               '100000012': 2,
#               '100000013': 2,
#               '100000014': 3,
#               '100000015': 3,
#               '100000016': 2,
#               '100000017': 3,
#               '100000018': 4,
#               '100000019': 3,
#               '100000020': 4,  # 无21
#               '100000022': 4,  # 无23
#               '100000024': 4,
#               '100000025': 4,
#               '100000026': 4,
#               '100000027': 1,
#               '100000028': 3,
#               '100000029': 3,
#               '100000030': 4,
#               '100000031': 2,
#               '100000032': 2,
#               '100000033': 2,
#
#               }

label_warp = {'100000001': 1,
              '100000002': 2,
              '100000003': 3,
              '100000004': 4,
              '100000005': 5,
              '100000006': 6,
              '100000007': 7,
              '100000008': 8,
              '100000009': 9,
              '100000010': 10,
              '100000011': 11,
              '100000012': 12,
              '100000013': 13,
              '100000014': 14,
              '100000015': 15,
              '100000016': 16,
              '100000017': 17,
              '100000018': 18,
              '100000019': 19,
              '100000020': 20,  # 无21
              '100000022': 21,  # 无23
              '100000024': 22,
              '100000025': 23,
              '100000026': 24,
              '100000027': 25,
              '100000028': 26,
              '100000029': 27,
              '100000030': 28,
              '100000031': 29,
              '100000032': 30,
              '100000033': 31,

              }
# label_warp = {'100000001': ,
#               '100000002': 1,
#               '100000003': ,
#               '100000004': ,
#               '100000005': 1,
#               '100000006': ,
#               '100000007': 3,
#               '100000008': ,
#               '100000009': 4,
#               '100000010': ,
#               '100000011': 2,
#               '100000012': ,
#               '100000013': ,
#               '100000014': ,
#               '100000015': ,
#               '100000016': ,
#               '100000017': ,
#               '100000018': ,
#               '100000019': ,
#               '100000020': ,  # 无21
#               '100000022': ,  # 无23
#               '100000024': ,
#               '100000025': ,
#               '100000026': ,
#               '100000027': ,
#               '100000028': ,
#               '100000029': ,
#               '100000030': ,
#               '100000031': ,
#               '100000032': ,
#               '100000033': ,
#
#               }


images_coco = list()
annotations_coco = list()
img_index = 0
ann_index = 1
class_names = list()

if osp.exists(log_path):
    os.remove(log_path) 
for xml_path in xml_paths:
    for fp in os.listdir(xml_path):
        if fp.split('.')[-1] != 'xml':
            continue   
        img_index += 1
        root = ET.parse(osp.join(xml_path, fp)).getroot()
        images_dict = dict()
        images_dict['file_name'] = root.find('Img_ID').text + '.bmp'

        # if osp.exists(osp.join(img_path, root.find('Img_ID').text) + '.bmp'):
        #     images_dict['file_name'] = root.find('Img_ID').text + '.bmp'
        # elif osp.exists(osp.join(img_path, fp.split('.xml')[0]+'.bmp')):
        #     images_dict['file_name'] = fp.split('.xml')[0] + '.bmp'
        #     # -----------------log-------------------
        #     # 当xml文件的文件名与图像名不对应时，在日志中写入错误报告
        #     with open(log_path, 'a+') as f:
        #         f.write('Picture name error, xml file name: '+fp+' Corrected picture name: ' + images_dict['file_name']+'/n')
        #     print('false name: ', fp)
        #     print('correct name: ', images_dict['file_name'])
        # else:
        #     with open(log_path, 'a+') as f:
        #         f.write('Picture name error, --------------xml file name: '+fp+ ' I don/'t know the corresponding picture' + '/n')
        #     print('-----------------------false name: ', fp, ' I don/'t know the corresponding picture')
        #     # 图片名称有问题---------------------------------------
        #     continue

        # sz = root.find('size')
        # images_dict['height'] = float(sz[1].text)
        images_dict['height'] = float(root.find('Img_SizeHeight').text)
        # images_dict['width'] = float(sz[0].text)
        images_dict['width'] = float(root.find('Img_SizeWidth').text)
        images_dict['id'] = img_index
        images_coco.append(images_dict)
        # find只找一个，findall找所有
        for child in root.findall('HRSC_Objects/HRSC_Object'):
            annotations_dict = dict()
            annotations_dict['iscrowd'] = 0
            annotations_dict['image_id'] = img_index
            # sub = child.find('bndbox')
            xmin = float(child.find('box_xmin').text)
            ymin = float(child.find('box_ymin').text)
            xmax = float(child.find('box_xmax').text)
            ymax = float(child.find('box_ymax').text)
            if xmin < 0 or xmin >= xmax or ymin < 0 or ymin >= ymax or \
                    xmax > images_dict['width'] or ymax > images_dict['height']:
                with open(log_path, 'a+') as f:
                    f.write('box error! ' + fp+ ' ann_index: ' + str(ann_index) + ' xmin: '+str(xmin) + ' ymin: ' +
                            str(ymin) + ' xmax: ' + str(xmax) + ' ymax: ' + str(ymax) + '/n')
                print(fp, ' ann_index:', ann_index, ' xmin: ', xmin, ' ymin: ', ymin, ' xmax: ', xmax, ' ymax: ', ymax)
                # 边框有问题---------------------------------------
                continue
            annotations_dict['bbox'] = [xmin, ymin, xmax-xmin, ymax-ymin]  # x1, y1, w, h
            # child_name = child.find('name').text
            # # 出现了不应该出现的类别
            # if child_name not in true_lab:
            #     # print(fp)
            #     print(child_name, fp)
            #     continue
            # if child_name not in class_names:
            #     class_names.append(child_name)
            #     # label_warp[child_name] = len(class_names)

            annotations_dict['category_id'] = label_warp[child.find('Class_ID').text]
            annotations_dict['id'] = ann_index
            ann_index +=1
            annotations_dict['area'] = annotations_dict['bbox'][2] * annotations_dict['bbox'][3]
            # x1, x2, y1, y2 = [annotations_dict['bbox'][0], annotations_dict['bbox'][0] + annotations_dict['bbox'][2], 
                                # annotations_dict['bbox'][1], annotations_dict['bbox'][1] + annotations_dict['bbox'][3]]
            # annotations_dict['segmentation'] = [[x1, y1, x1, y2, x2, y2, x2, y1]]
            annotations_coco.append(annotations_dict)

categories = list()
count = 1
for name in true_lab:
    mydict = dict()
    mydict['id'] = count
    mydict['name'] = name
    categories.append(mydict)
    count += 1
    
print('class_names:', class_names, ' len of images_coco:', len(images_coco))
data_train = {'info': info, 'images': images_coco, 'annotations': annotations_coco,
                'categories': categories}
if osp.exists(coco_path):
    os.remove(coco_path)
with open(coco_path, "w") as f:
    json.dump(data_train, f)
print('succeed!')
