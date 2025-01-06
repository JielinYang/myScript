# 2025.1.6 latex校对任务

import os
import re
import shutil
import logging

# 配置日志记录器，将日志输出到文件
logging.basicConfig(filename='latex_check.log', filemode='w', level=logging.INFO)


# 给每个文件夹创建 questions.md 和 solution.md
def create_md_if_not_exists(root):
    # 使用 os.walk 遍历目录及其子目录
    for sub_dir in os.listdir(root):
        sub_dir_path = os.path.join(root, sub_dir)
        if not os.path.isdir(sub_dir_path):
            continue
        questions_md_path = os.path.join(sub_dir_path, 'questions.md')
        solutions_md_path = os.path.join(sub_dir_path, 'solutions.md')
        if not os.path.exists(questions_md_path):
            with open(questions_md_path, 'w', encoding='utf-8') as f:
                logging.info(f"create: {questions_md_path}")
        else:
            logging.info(f"file {questions_md_path} already exist ")
        if not os.path.exists(solutions_md_path):
            with open(solutions_md_path, 'w', encoding='utf-8') as f:
                logging.info(f"create: {solutions_md_path}")
        else:
            logging.info(f"file {solutions_md_path} already exist ")


def find_1xxx(pdf_dir, md_dir, res_dir):
    # 正则表达式模式，用于匹配以1开头的四位数字
    pattern = r'\b[123]\d{3}\b'
    problem_number = {}
    part1 = 272
    part2 = 84
    part3 = 54

    for sub_file in os.listdir(md_dir):
        if not sub_file.split('.')[-1] == 'md':
            continue
        md_path = os.path.join(md_dir, sub_file)
        with open(md_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                matches = re.findall(pattern, line)
                if matches and len(line.rstrip()) <= 12:
                    problem_number[int(matches[0])] = {'page': sub_file.split('.')[0], 'line': line_number}

    sorted_dict = {k: problem_number[k] for k in sorted(problem_number)}

    for key in sorted_dict:
        dir_name = str(int(key/1000)) + '_' + str(key % 1000)
        prob_dir = os.path.join(res_dir, dir_name)
        if key+1 not in problem_number:
            continue
        if problem_number[key+1]['line'] <= 4:
            end_page = int(problem_number[key+1]['page']) - 1
        else:
            end_page = int(problem_number[key+1]['page'])
        start_page = int(problem_number[key]['page'])
        for i in range(start_page, end_page+1):
            # 复制pdf文件
            pdf_src = os.path.join(pdf_dir, str(i)+'.pdf')
            pdf_dst = os.path.join(res_dir, prob_dir, str(i)+'.pdf')
            if not os.path.exists(pdf_dst):
                shutil.copy(pdf_src, pdf_dst)
                logging.info(f"copy {pdf_src} to {pdf_dst} success")
            else:
                logging.info(f"file {pdf_dst}already exist ")
            # 复制md文件
            md_src = os.path.join(md_dir, str(i)+'.md')
            md_dst = os.path.join(res_dir, prob_dir, str(i)+'.md')
            if not os.path.exists(md_dst):
                shutil.copy(md_src, md_dst)
                logging.info(f"copy {md_src} to {md_dst} success")
            else:
                logging.info(f"file {md_dst} already exist ")

    # sorted_dict = {k: problem_number[k] for k in sorted(problem_number)}
    # lack_number = []
    # for i in range(1001, 1272):
    #     if i not in sorted_dict:
    #         lack_number.append(i)
    # logging.info(sorted_dict)

# 创建第二章问题的文件夹
def create_dir():
    dir = 'C:\\Users\\yjl\\Desktop\\latex_result'
    part1 = 272
    part2 = 84
    part3 = 54
    for i in range(1, part1+1):
        path = os.path.join(dir, '1_'+str(i))
        if os.path.exists(path):
            logging.info(f"already exist {path}")
            continue
        try:
            os.mkdir(path)
            logging.info(f"Folder '{path}' created successfully.")
        except FileExistsError:
            logging.info(f"Folder '{path}' already exists.")

    for i in range(1, part2+1):
        path = os.path.join(dir, '2_'+str(i))
        if os.path.exists(path):
            logging.info(f"already exist {path}")
            continue
        try:
            os.mkdir(path)
            logging.info(f"Folder '{path}' created successfully.")
        except FileExistsError:
            logging.info(f"Folder '{path}' already exists.")

    for i in range(1, part3+1):
        path = os.path.join(dir, '3_'+str(i))
        if os.path.exists(path):
            logging.info(f"already exist {path}")
            continue
        try:
            os.mkdir(path)
            logging.info(f"Folder '{path}' created successfully.")
        except FileExistsError:
            logging.info(f"Folder '{path}' already exists.")


if __name__ == '__main__':
    root_directory = 'C:\\Users\\yjl\\Desktop\\latex_result'
    create_md_if_not_exists(root_directory)

    # create_dir()

    # pdf_dir = 'C:\\Users\\yjl\\Desktop\\temp\\mechanics\\pdf'
    # md_dir = 'C:\\Users\\yjl\\Desktop\\temp\\mechanics\\md'
    # res_dir = 'C:\\Users\\yjl\\Desktop\\latex_result'
    # find_1xxx(pdf_dir, md_dir, res_dir)