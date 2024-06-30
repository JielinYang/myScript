# 2024.6.29
# 视频按帧截取图像
# 重命名文件
import random

import cv2
import os
import shutil

# 截取视频图像配置
video_path = 'C:\\MyFile\Datasets\\acoustic optic pair\\original data\\video'  # 替换为你的实际视频路径
output_folder = 'C:\\MyFile\Datasets\\acoustic optic pair\\original data\\origin2'  # 替换为你想要保存帧的文件夹
frame_interval = 5  # 每20帧截取一张图片
# 重命名文件配置
renamefile_path = 'C:\\MyFile\\Datasets\\acoustic optic pair\\original data\\origin1'
# 重命名配对文件配置
rename_pairfile_path = 'C:\\MyFile\\Datasets\\acoustic optic pair\\original data\\temp'


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
def rename_pair_in_directory(directory):
    # 获取目录下所有文件
    files = os.listdir(directory)
    # 过滤出文件，去掉目录和子目录
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    # 对文件按照名称排序
    files.sort()

    indext_list = list(range(0, int(len(files)/2)))
    random.shuffle(indext_list)

    index = -1
    pre_name = ''
    for i, file in enumerate(files):
        prefix, extension = os.path.splitext(file)
        if prefix != pre_name:
            index += 1
        pre_name = prefix
        new_name = f"{indext_list[index]:04d}{extension}"
        old_path = os.path.join(directory, file)
        new_path = os.path.join(directory, new_name)
        try:
            shutil.move(old_path, new_path)
            print(f"Renamed {file} to {new_name}")
        except Exception as e:
            print(f"Failed to rename {file}: {str(e)}")


if __name__ == '__main__':
    # capture_frames(video_path, output_folder, frame_interval)
    # rename_files_in_directory(renamefile_path)
    rename_pair_in_directory(rename_pairfile_path)