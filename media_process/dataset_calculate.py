# 统计数据集中各个类别的数量
import json

anno_json_path = "C:\\MyFile\\Datasets\\acoustic optic pair\\original data\\6_final_dataset\\train_annotations.json"


def count_categories(json_file_path):
    # 加载JSON文件
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    print(f"图片数量：{len(data['images'])}")

        # 初始化一个字典来存储每个类别的计数
    category_counts = {}

    # 遍历所有标注
    for annotation in data['annotations']:
        # 获取标注的类别ID
        category_id = annotation['category_id']

        # 如果这个类别ID已经在字典中，则增加计数
        if category_id in category_counts:
            category_counts[category_id] += 1
        else:
            # 否则，在字典中为这个类别ID添加一个新的条目，并设置计数为1
            category_counts[category_id] = 1

            # （可选）如果你想要根据类别名称而不是ID来统计，你可以这样做：
    # 首先，从categories中创建一个类别ID到名称的映射
    category_id_to_name = {cat['id']: cat['name'] for cat in data['categories']}

    # 然后，更新category_counts以使用类别名称作为键
    category_name_counts = {category_id_to_name[cid]: count for cid, count in category_counts.items()}

    total = 0;
    # 打印结果
    for name, count in category_name_counts.items():
        print(f"Category: {name}, Count: {count}")
        total += count

    print(f"所有目标：{total}")


if __name__ == '__main__':
    count_categories(anno_json_path)