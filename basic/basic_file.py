import os
import re
import csv
import json
import shutil
import zipfile
import pandas as pd
from loguru import logger


class BasicFile(object):
    def __init__(self):
        self.data_list = []

    @staticmethod
    def get_abs_path():
        # 获取当前文件所在目录的绝对路径
        abs_file = __file__
        abs_dir = abs_file[:abs_file.rfind("/")]
        # print(abs_dir)
        return abs_dir

    @staticmethod
    def mkdir_file(file_path):
        # 创建目录或文件夹
        try:
            os.mkdir(file_path)
        except FileExistsError:
            print(f'{file_path} is existed')

    @staticmethod
    def delete_file_one(file_addr):
        # 删除指定位置的文件
        try:
            os.remove(file_addr)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def delete_dir(file_path):
        # 删除指定位置的目录或文件夹
        try:
            shutil.rmtree(file_path)
        except FileNotFoundError:
            print(f'{file_path} not existed')

    @staticmethod
    def get_now_abspath():
        # 获取当前文件所在的绝对路径
        abs_file = __file__
        # print("abs path is %s" % (__file__))
        abs_dir = abs_file[:abs_file.rfind("/")]
        # print(abs_dir)
        return abs_dir

    @staticmethod
    def unzip_one_file(zip_path, extract_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        logger.info(f"{zip_path} 解压完成")

    def unzip_dir_all_file(self, dir_path, key='', extract_path=None):
        # 遍历目录下的文件和文件夹，dir_path：要遍历的目录，extract_path：解压后文件存储的位置
        for path, dirs, files in os.walk(dir_path):
            for file in files:
                # 根据关键词提取指定文件 key=账户信息.zip
                if key in file:
                    # print(path, file)
                    zip_path = os.path.join(path, file)
                    extract_path = path if extract_path is None else extract_path
                    try:
                        self.unzip_one_file(zip_path=zip_path, extract_path=extract_path)
                    except Exception as e:
                        logger.error(f'file path: {zip_path}, zip error: {e}')

    @staticmethod
    def read_csv_for_dict(csv_path, key='账户状态', encoding='UTF-8'):
        # 根据列名关键词查询csv文件中指定列名的数据并去重
        # UTF-8、GBK、ISO-8859-1
        column_name_pattern = key  # 指定要匹配的部分列名
        with open(csv_path, 'r', encoding=encoding) as fr:
            reader = csv.DictReader(fr)
            # 获取所有列名
            column_names = reader.fieldnames
            # 根据模糊匹配找到符合条件的列名
            matched_column_names = [name for name in column_names if re.search(column_name_pattern, name)]
            # print(matched_column_names)

            column_data = []
            for row in reader:
                data = [row[name] for name in matched_column_names]
                if '只进不出控制\t' in data:
                    print(csv_path)
                column_data.extend(data)
        column_data = list(set(column_data))
        # print(column_data)
        return column_data

    def get_all_csv_data(self, dir_path):
        # 遍历目录下的所有CSV文件，返回所有文件中指定列的数据
        end_list = []
        for filename in os.listdir(dir_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(dir_path, filename)
                status = self.read_csv_for_dict(csv_path=file_path, key='账户状态', encoding='GBK')
                end_list += status
        res = list(set(end_list))
        for j in res:
            self.data_list.append(j.strip())
        result = list(set(self.data_list))
        return result

    @staticmethod
    def get_all_file_path(dir_path):
        # 首先获取到目录下所有的文件
        names = os.listdir(dir_path)
        # 进行路径拼接
        name_list = [os.path.join(dir_path, name) for name in names]
        # 打印结果看看
        return name_list

    def get_all_file(self, path, file_list=[]):
        # 递归获取改目录下所有子目录下的文件路径
        dir_list = os.listdir(path)
        for x in dir_list:
            new_x = os.path.join(path, x)
            if os.path.isdir(new_x):
                self.get_all_file(new_x, file_list)
            else:
                file_tuple = os.path.splitext(new_x)
                # print(file_tuple)
                file_list.append(new_x)
                # 获取制定格式的文件
                # if file_tuple[1] == '.json':
                #     file_list.append(new_x)
        return file_list

    def delete_many_file(self, path):
        # 递归删除一个目录下所有文件而不是文件夹
        ls = os.listdir(path)
        for i in ls:
            c_path = os.path.join(path, i)
            # print(c_path)
            if os.path.isdir(c_path):
                self.delete_many_file(c_path)
            else:
                os.remove(c_path)


class BasicCSV(object):
    def __init__(self):
        self.basic_file = BasicFile()

    @staticmethod
    def csv_to_xlsx(csv_path, xlsx_path):
        reader = pd.read_csv(csv_path, encoding='utf-8')
        reader.to_excel(xlsx_path)

    @staticmethod
    def write_csv(data_list, name, mode='w', fieldnames=[], tag='dict', header=True):
        with open(name, mode, newline='', encoding='utf-8') as f:
            # fieldnames = ['key', 'doc_count']  # 定义CSV表头
            # 创建CSV写入器
            if tag == 'dict':
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if header is True:
                    writer.writeheader()  # 写入表头
                # 写入数据
                for data in data_list:
                    writer.writerow(data)
            elif tag == 'tuple':
                writer = csv.writer(f)
                writer.writerow(data_list)
            else:
                writer = csv.writer(f)
                if len(fieldnames) != 0:
                    writer.writerow(fieldnames)
                writer.writerows(data_list)

    @staticmethod
    def check_csv_key(filename, key):
        key_list = []
        # 打开 CSV 文件并读取数据
        with open(filename, 'r', newline='', errors='ignore') as file:
            reader = csv.reader((line.replace('\0', '') for line in file))
            # 逐行读取数据并筛选出符合条件的数据
            for row in reader:
                if key in row:
                    # print(row)
                    key_list.append(row)
        print(len(key_list))

    @staticmethod
    def read_file_dup(filename):
        # 在一个函数中对同一个文件读取多次，除了第一次外，之后会无法获取文件内容，
        # 因为在第一个函数结束时文件已经被读取到末尾，这意味着第二个函数将无法读取到文件的内容，因为文件已经被读取完毕；
        # 为了避免这种情况，可以考虑将文件的内容存储在一个变量中，并将该变量传递给两个函数进行处理。
        # 或者，在第一个函数中处理完文件后，将文件指针重新定位到文件开头；
        # 使用`fr.seek(0)`方法的作用是：将文件指针移动到文件的第0个字节位置。
        # 需要注意的是，`seek()`方法的参数是以字节为单位的偏移量。
        # 在文本文件中，每个字符通常占用一个字节，但是对于某些特殊的字符编码，一个字符可能会占用多个字节。
        # 因此，如果您要确保准确的偏移量，请根据实际情况选择正确的字符编码。
        with open(filename, 'r') as fr:
            for row, j in enumerate(fr.readlines()):
                print(row, j.strip())
            fr.seek(0)  # 将文件指针移动到文件的第0个字节位置
            for index, line in enumerate(fr.readlines()):
                print(index, line.strip())

    def draw_csv_diff_field(self):
        # 从csv文件中根据不同的vid，将相同vid的资产写入同一文件中
        vuln_ids = []
        with open('test.csv', 'r') as fr:
            for j in fr.readlines():
                if '组件' not in j.strip():
                    data = json.loads(j.strip())
                    vid = data['cve_id']
                    name = vid.replace('-', '_')
                    url = data['url']
                    tar = {"url": url, "vid": vid}
                    self.write_csv(data_list=[tar], name=f'test/{name}.csv', mode='a', fieldnames=['url', 'vid'], header=False)
                    if vid not in vuln_ids:
                        vuln_ids.append(vid)

    def get_fofa_csv_merge(self, name, keyword):
        # 合并指定目录下符合条件的所有csv文件
        data_list = []
        file_list = self.basic_file.get_all_file(path='test.csv')
        print(file_list)
        for f_name in file_list:
            if keyword in f_name:
                with open(f_name, 'r') as fr:
                    for j in fr.readlines():
                        if 'url' not in j.strip():
                            data_list.append(j.strip())
        tar_list = list(set(data_list))
        print(len(tar_list))
        self.write_csv(tar_list, name=name, fieldnames=['url'], tag='list')

    @staticmethod
    def get_diff_csv(path1, path2, path_end):
        # 读取第一个 CSV 文件
        df1 = pd.read_csv(path1)
        # 读取第二个 CSV 文件
        df2 = pd.read_csv(path2)
        # 提取不再第二个 CSV 文件中的数据
        df_result = df1[~df1['url'].isin(df2['url'])]
        # 将结果保存到一个新的 CSV 文件
        df_result.to_csv(path_end, index=False)


class BasicXLSX(object):

    @staticmethod
    def xlsx_to_csv(xlsx_path, csv_path):
        reader = pd.read_excel(xlsx_path)
        df = pd.DataFrame(reader)
        # index: False 不显示第一列的排序，header: True 第一行为键
        df.to_csv(csv_path, mode='w', index=False, header=True)

