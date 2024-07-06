# 2024.6.29
# 视频按帧截取图像
# 重命名文件
import random
import logging
from datetime import datetime
import cv2
import os
import shutil

# 截取视频图像配置
video_path = 'C:\\MyFile\Datasets\\acoustic optic pair\\original data\\video'  # 替换为你的实际视频路径
output_folder = 'C:\\MyFile\Datasets\\acoustic optic pair\\original data\\origin2'  # 替换为你想要保存帧的文件夹
frame_interval = 5  # 每20帧截取一张图片
# 重命名文件配置
renamefile_path = 'C:\\MyFile\\Datasets\\acoustic optic pair\\original data\\origin1'
# 配对文件随机打乱+划分训练测试集+重命名 配置：
root_dir = "C:\\MyFile\\Datasets\\acoustic optic pair\\original data"
rename_pairfile_path = os.path.join(root_dir, "2_pickup")
train_dir = os.path.join(root_dir, "3_shuffle+rename+divide\\train")
test_dir = os.path.join(root_dir, "3_shuffle+rename+divide\\test")
log_filename = os.path.join(root_dir, "3_shuffle+rename+divide\\log\\log.txt")

# 获取文件夹中所有文件
def get_all_file_paths(folder_path):
    file_paths = []
    for root, directories, files in os.walk(folder_path):
        for filename in files:
            # 构建文件路径
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
    return file_paths

# 截取视频帧
def capture_frames(video_path, output_folder, frame_interval):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取视频文件路径
    file_paths = get_all_file_paths(video_path)

    for i, file in enumerate(file_paths):
        # 打开视频文件
        cap = cv2.VideoCapture(file)

        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames in the video: {frame_count}")

        current_frame = 0
        saved_frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 如果当前帧是我们需要保存的帧
            if current_frame % frame_interval == 0:
                frame_filename = os.path.join(output_folder, f"frame_{i}_{saved_frame_count:04d}.jpg")
                cv2.imwrite(frame_filename, frame)
                saved_frame_count += 1

            current_frame += 1

        cap.release()
        print(f"Total frames saved: {saved_frame_count}")

# 重命名文件夹中所有文件，按照序号排序
def rename_files_in_directory(directory):
    # 获取目录下所有文件
    files = os.listdir(directory)
    # 过滤出文件，去掉目录和子目录
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    # 对文件按照名称排序
    files.sort()

    # 遍历文件并重命名
    for index, file in enumerate(files):
        # 构造新文件名，例如：1.txt, 2.txt, ..., n.txt
        new_name = f"{index + 1}{os.path.splitext(file)[1]}"
        # 拼接文件的完整路径
        old_path = os.path.join(directory, file)
        new_path = os.path.join(directory, new_name)
        # 重命名文件
        try:
            shutil.move(old_path, new_path)
            print(f"Renamed {file} to {new_name}")
        except Exception as e:
            print(f"Failed to rename {file}: {str(e)}")


# 重命名文件夹中配对文件文件：xx.jpg xx.json --> 0001.jpg 0001.json
# 并随机划分为训练集和测试集
def rename_pair_in_directory(dir, train_dir, test_dir, log_filename):
    logging.basicConfig(filename=log_filename, level=logging.INFO, filemode='w')
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"-------------------{time_now}-------------------------")
    # 获取目录下所有文件
    files = os.listdir(dir)
    # 过滤出文件，去掉目录和子目录
    files = [file for file in files if os.path.isfile(os.path.join(dir, file))]
    # 对文件按照名称排序
    files.sort()

    total_num = int(len(files)/2)
    train_num = int(total_num * 0.7)
    test_num = total_num - train_num
    train_index_list = list(range(0, train_num))
    test_index_list = list(range(0, test_num))
    random.shuffle(train_index_list)
    random.shuffle(test_index_list)

    train_index = 0
    test_index = 0
    next = False
    pre_name = ''
    pre_path = ''
    for i, file in enumerate(files):
        prefix, extension = os.path.splitext(file)
        if not next:
            if (random.random() <= 0.7 and train_index < train_num) or test_index == test_num:
                new_name = f"{train_index_list[train_index]:04d}{extension}"
                old_path = os.path.join(dir, file)
                new_path = os.path.join(train_dir, new_name)
                pre_name = f"{train_index_list[train_index]:04d}"
                pre_path = train_dir
                train_index += 1
                next = True
                try:
                    shutil.copy(old_path, new_path)
                    logging.info(f"Renamed {old_path} to {new_path}")
                    print(f"Renamed {old_path} to {new_path}")
                except Exception as e:
                    print(f"Failed to rename {file}: {str(e)}")
            else:
                new_name = f"{test_index_list[test_index]:04d}{extension}"
                old_path = os.path.join(dir, file)
                new_path = os.path.join(test_dir, new_name)
                pre_name = f"{test_index_list[test_index]:04d}"
                pre_path = test_dir
                test_index += 1
                next = True
                try:
                    shutil.copy(old_path, new_path)
                    logging.info(f"Renamed {old_path} to {new_path}")
                    print(f"Renamed {old_path} to {new_path}")
                except Exception as e:
                    print(f"Failed to rename {file}: {str(e)}")
        else:
            old_path = os.path.join(dir, file)
            new_name = f"{pre_name}{extension}"
            new_path = os.path.join(pre_path, new_name)
            next = False
            try:
                shutil.copy(old_path, new_path)
                logging.info(f"Renamed {old_path} to {new_path}")
                print(f"Renamed {old_path} to {new_path}")
            except Exception as e:
                print(f"Failed to rename {file}: {str(e)}")


if __name__ == '__main__':
    # capture_frames(video_path, output_folder, frame_interval)
    # rename_files_in_directory(renamefile_path)
    rename_pair_in_directory(rename_pairfile_path, train_dir, test_dir, log_filename)