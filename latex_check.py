# 2025.1.6 latex校对任务

import os


# 给每个文件夹创建 questions.md 和 solution.md
def create_md_if_not_exists(root):
    # 使用 os.walk 遍历目录及其子目录
    for sub_dir in os.listdir(root):
        sub_dir_path = os.path.join(root, sub_dir)
        questions_md_path = os.path.join(sub_dir_path, 'questions.md')
        solutions_md_path = os.path.join(sub_dir_path, 'solutions.md')
        if not os.path.exists(questions_md_path):
            with open(questions_md_path, 'w', encoding='utf-8') as f:
                print(f"创建了文件: {questions_md_path}")
        else:
            print(f"文件 {questions_md_path} 已经存在")
        if not os.path.exists(solutions_md_path):
            with open(solutions_md_path, 'w', encoding='utf-8') as f:
                print(f"创建了文件: {solutions_md_path}")
        else:
            print(f"文件 {solutions_md_path} 已经存在")


# 指定要遍历的根目录
root_directory = 'C:\\Users\\yjl\\Desktop\\latex_result'  # 替换为你想要遍历的路径

if __name__ == '__main__':
    create_md_if_not_exists(root_directory)