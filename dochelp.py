import csv
import os
import numpy as np
import random


def generate_parameter_matrix(number):
    # 1. 生成第一列：1-18各出现number次
    first_col = [i for i in range(1, 19) for _ in range(number)]  # 1-18各出现number次
    random.shuffle(first_col)  # 打乱顺序

    # 2. 生成第二列：全为1
    second_col = [1] * len(first_col)

    # 3. 生成第三列和第四列：随机生成1到20之间的整数
    third_col = np.random.randint(1, 21, size=len(first_col)).tolist()  # 1-20之间的随机数
    fourth_col = np.random.randint(1, 21, size=len(first_col)).tolist()  # 1-20之间的随机数

    # 4. 组合成最终的参数矩阵
    parameter_matrix = np.column_stack((first_col, second_col, third_col, fourth_col))

    return parameter_matrix


def is_file_empty(file_path):
    """检查文件内容是否为空（不止是大小为零）"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()  # 去除前后空白字符
        return len(content) == 0


def append_column_to_csv(input_file, new_column_name, new_column_values):
    # 检查文件是否为空
    if not os.path.exists(input_file) or is_file_empty(input_file):
        # 如果文件不存在或文件为空，直接写入新列头和新列值
        with open(input_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([new_column_name])  # 写入新列名
            for value in new_column_values:
                writer.writerow([value])  # 写入每个新列值
        return

    # 如果文件不为空，继续处理
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        original_rows = list(reader)

    # 确保新列值的数量与原始数据行数匹配
    if len(new_column_values) != len(original_rows) - 1:  # -1 是因为不计算表头
        raise ValueError("新列的值数量必须与原始数据行数匹配（不包括表头）。")

    # 创建一个临时文件以存储更新后的内容
    temp_file = 'temp_file.csv'

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
            open(temp_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 读取表头并添加新列名
        headers = next(reader)
        headers.append(new_column_name)  # 添加新列名
        writer.writerow(headers)  # 写入新的表头

        # 写入原始数据，并在每一行后添加新列的值
        for i, row in enumerate(reader):
            row.append(new_column_values[i])  # 在每一行右侧添加新列的值
            writer.writerow(row)  # 写入更新后的行

    # 替换原文件
    os.replace(temp_file, input_file)
