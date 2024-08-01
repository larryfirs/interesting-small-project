
"""
自动批量转换目标文件夹下的所有pdf文件为word文件

提供GUI视图选择文件夹

不支持相同文件夹下已有转换word存在条件下运行
"""
# 导入os模块，用于处理文件和目录
import os
# 导入PyPDF2模块，用于读取PDF文件
from PyPDF2 import PdfReader
# 导入docx模块，用于创建和操作Word文档
from docx import Document
# 导入tkinter模块，用于获取用户选择的文件夹
import tkinter as tk
from tkinter import filedialog
# 定义方法select_directory，通过弹窗选择文件夹
def select_directory():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    directory_path = filedialog.askdirectory()
    return directory_path

# 把文件下的所有PDF逐页转换为word
def conversion(file_dir):
    if not os.path.exists(file_dir):
        print('文件路径不正确，请检查')
    else:
        file_list = [f for f in os.listdir(file_dir) if f.endswith('.pdf')]  # 确保是PDF文件
        for file in file_list:
            pdf_path = os.path.join(file_dir, file)
            try:
                #调用转换方法
                pdf2word(pdf_path)
            except Exception as e:
                print(f"转换错误: {e}")
# pdf转为docx方法
def pdf2word(pdf_path):
    # 使用PyPDF2读取PDF文件
    reader = PdfReader(pdf_path)
    doc = Document()
    # 遍历PDF中的每一页
    for page_num in range(len(reader.pages)):
        # 获取每一页的内容
        page = reader.pages[page_num]
        # 将文本添加到Word文档
        text = page.extract_text()
        if text:  # 确保提取的文本不为空
            doc.add_paragraph(text)
    # 保存Word文档
    name = get_name(pdf_path)
    # Word文档输出路径
    docx_file = os.path.join(output_dir, f"{name}.docx")
    try:
        doc.save(docx_file)
        print(f"文件已保存: {docx_file}")
    except Exception as e:
        print(f"保存文件时出错: {e}")
# 获取文件名（去除后缀）
def get_name(file_path):
    # 使用os.path.basename()获取文件名
    file_name_with_extension = os.path.basename(file_path)
    # 使用os.path.splitext()分离文件名和后缀名
    file_name, _ = os.path.splitext(file_name_with_extension)
    return file_name


# 调用函数

# 定义变量output_dir存储文件夹路径
output_dir = select_directory()
# 确保选择的文件夹存在（这一步不写也可以）
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# 执行转换操作
conversion(output_dir)
