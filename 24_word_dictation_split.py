import os


def split_list(lst, size):
    """
    将列表划分为指定大小的子列表
    :param lst: 要划分的列表
    :param size: 子列表的大小
    :return: 划分后的子列表组成的列表
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]


with open('3 四级-乱序.txt', 'r', encoding="UTF8") as file:
    lines = file.readlines()
    out_path = "out/四级"
    sub_lists = split_list(lines, 10)
    for sublist in sub_lists:
        out_list = os.listdir(out_path)
        out_count = len(out_list)
        tmp_out_path = out_path + "/" + str(out_count)
        os.mkdir(tmp_out_path)
        ref = ""
        listen = "#\n"
        for line in sublist:
            # print(line.strip())  # 去除行尾的换行符
            line = line.strip()
            eng, ch = line.split("\t")
            # print(eng)
            ref += line + "\n"
            listen += eng + "\n"
        # 打开文件以写入模式
        with open(tmp_out_path + "/ref.txt", "w") as file:
            file.write(ref)
        with open(tmp_out_path + "/listen.txt", "w") as file:
            file.write(listen)


