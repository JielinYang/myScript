'''
created on June 2 2023
transfer original vertical annotations and xml format to rotated annotations and txt format.
@author: yjl
'''
import math
import os.path as osp
import os
import json
import xml.etree.ElementTree as ET
from PIL import Image
import cv2
import numpy as np

root = r"G:\dataset\HRSC2016\HRSC2016\FullDataSet"
train_coco_path = osp.join(root, r"new_train\HRSC_coco_train.json")
val_coco_path = osp.join(root, r"new_val\HRSC_coco_val.json")
anno_ori_path = osp.join(root, "Annotations")
train_dota_path = osp.join(root, "train_dota")
val_dota_path = osp.join(root, "val_dota")
png_path = osp.join(root, r"new_train")
jpg_path = osp.join(root, r"new_train_jpg")

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


def coco_xml_to_dota_txt(cx_path, dt_path, anno_ori_path):
    # 先读取coco格式的xml文件找到图片的原始名字，根据原始名字找到原始的标注文件，转化为dota格式后保存在dt_path中
    target_id = 0
    with open(cx_path, 'r') as f:
        coco_dict = json.load(f)
        img_num = len(coco_dict['images'])
        target_num = len(coco_dict['annotations'])
    for i in range(img_num):
        name_ori = coco_dict['images'][i]['file_name_ori'].split('.')[0]
        name = coco_dict['images'][i]['file_name'].split('.')[0]
        xml_path = osp.join(anno_ori_path, name_ori + '.xml')
        if osp.exists(osp.join(dt_path, f"{name}.txt")):
            os.remove(osp.join(dt_path, f"{name}.txt"))
            print(f"以前的{name}.txt文件被删除")
        if osp.exists(xml_path):
            print(f'成功找到图片{name}.bmp对应的原始xml文件，路径为：{xml_path}')
            root_cls = ET.parse(xml_path).getroot()
            for child in root_cls.findall('HRSC_Objects/HRSC_Object'):
                if label_warp[child.find('Class_ID').text] == 99:
                    print("原始文件中找到1个其他类")
                    continue
                cx = float(child.find('mbox_cx').text)
                cy = float(child.find('mbox_cy').text)
                w = float(child.find('mbox_w').text)
                h = float(child.find('mbox_h').text)
                theta = float(child.find('mbox_ang').text)
                # HRSC数据集中theta范围为-pi/2到pi/2，假设以顺时针为正方向
                alpha = math.atan(h/w) + theta
                beta = math.atan(h/w) - theta
                d = 0.5 * math.sqrt(w**2 + h**2)
                # 左上角为A，逆时针旋转依次为BCD
                Ax, Ay = cx - d * math.cos(alpha), cy - d * math.sin(alpha)
                Bx, By = cx - d * math.cos(beta), cy + d * math.sin(beta)
                Cx, Cy = 2 * cx - Ax, 2 * cy - Ay
                Dx, Dy = 2 * cx - Bx, 2 * cy - By
                print("原始xywh为：%.0f %.0f %.0f %.0f %f" % (cx, cy, w, h, theta))
                print("对应四点：%.0f %.0f %.0f %.0f" % (cx-w/2, cy-h/2, cx+w/2, cy+h/2))
                print("修改后为：%.0f %.0f %.0f %.0f %.0f %.0f %.0f %.0f" % (Ax, Ay, Bx, By, Cx, Cy, Dx, Dy))
                # 寻找该目标的类别
                category = "None"
                if target_id == coco_dict['annotations'][target_id]['id'] - 1 and i == coco_dict['annotations'][target_id]['image_id'] - 1:
                    category = true_lab[coco_dict['annotations'][target_id]['category_id']-1]
                    target_id += 1
                    print(f"成功找到第{target_id}个目标")
                with open(osp.join(dt_path, f"{name}.txt"), 'a') as f:
                    f.write("%.0f %.0f %.0f %.0f %.0f %.0f %.0f %.0f %s %d\n" % (Ax, Ay, Bx, By, Cx, Cy, Dx, Dy, category, 0))
                    print(f"成功将第{target_id}个目标写入{name}.txt文件")
        print("------------------完成一张图片对应的目标格式转化-----------------")
    if target_id == target_num - 1:
        print(f'目标数量对应，总共：{target_num}')


def png_to_jpg(png_path, jpg_path):
    flag = 0
    for img in os.listdir(png_path):
        flag += 1
        if flag == 21:
            break
        img_path = osp.join(png_path, img)
        save_path = osp.join(jpg_path, f"{img.split('.')[0]}.png")
        with Image.open(img_path, 'r') as f:
            f.save(save_path)


def show_box():
    img = np.zeros((1024, 1024, 3), np.uint8)

    pts = np.array([[100, 100], [200, 100], [150, 200], [50, 200]], np.int32)
    pts = pts.reshape((-1, 1, 2))

    color = (255, 0, 0)
    cv2.fillPoly(img, [pts], color)

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    # coco_xml_to_dota_txt(train_coco_path, train_dota_path, anno_ori_path)
    coco_xml_to_dota_txt(val_coco_path, val_dota_path, anno_ori_path)
    # png_to_jpg(png_path, jpg_path)
    # show_box()


if __name__ == '__main__':
    main()

