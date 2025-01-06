# 根据已经标注的coco信息进行分类
# 原始文件：包含train和val文件夹，以及一个coco标注文件
# 目标文件：多个文件夹，每个类别对应一个文件夹

import os
import json
import shutil

# 文件路径
json_file_path = 'C:\\MyFile\Datasets\\acoustic optic pair\\4_anno2coco(add_low_quality)\\test\\annotations.json'
image_folder_path = 'C:\\MyFile\Datasets\\acoustic optic pair\\5_opt2aco(add_low_quality_and_internet_image)'
image_subfolder = 'aco_test_low_quality'  # 图片所在的子目录

# 读取JSON文件
with open(json_file_path, 'r') as f:
    annotations = json.load(f)

# 获取标注信息
images = annotations['images']
annotations = annotations['annotations']

# 创建类别文件夹
categories = set()
for annotation in annotations:
    categories.add(annotation['category_id'])

for category in categories:
    category_folder = os.path.join(image_folder_path, f'category_{category}')
    os.makedirs(category_folder, exist_ok=True)

# 将图片分类到相应的文件夹
for annotation in annotations:
    image_id = annotation['image_id']
    category_id = annotation['category_id']

    # 找到对应的图片文件名
    image_info = next(img for img in images if img['id'] == image_id)
    image_filename = image_info['file_name']

    # 源文件路径
    src_path = os.path.join(image_folder_path, image_subfolder, os.path.basename(image_filename))
    # 目标文件路径
    dest_path = os.path.join(image_folder_path, f'category_{category_id}', os.path.basename(image_filename))

    # 复制图片到目标文件夹
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
    else:
        print(f"File not found: {src_path}")

print("图片分类完成。")
