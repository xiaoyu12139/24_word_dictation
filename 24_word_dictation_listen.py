import os
import configparser
import requests
import time
import random
from pydub import AudioSegment
import subprocess
from PyQt5.QtCore import QUrl


def down_word_audio_baidu(word, proxies, headers, save_path):
    url = "https://fanyi.baidu.com/gettts?lan=en&text=" + word + "&spd=3&source=wise"
    response = requests.get(url, proxies=proxies, headers=headers)
    with open(save_path, "wb") as file:
        file.write(response.content)


def down_word_audio_youdao(word, proxies, headers, save_path):
    url = "https://dict.youdao.com/dictvoice?audio=" + word + "&le=en"
    response = requests.get(url, proxies=proxies, headers=headers)
    with open(save_path, "wb") as file:
        file.write(response.content)


def down_word_audio_sougou(word, proxies, headers, save_path):
    url = "https://dlweb.sogoucdn.com/phonetic/" + word + "DELIMITER_gb_1.mp3"
    response = requests.get(url, proxies=proxies, headers=headers)
    with open(save_path, "wb") as file:
        file.write(response.content)


def down_word_audio_google(word, proxies, headers, save_path):
    url = "https://translate.google.com/translate_tts?ie=UTF-&&client=tw-ob&tl=en&q=" + word
    response = requests.get(url, proxies=proxies, headers=headers)
    with open(save_path, "wb") as file:
        file.write(response.content)


# 下载指定单词的音频
def down_word_audio(word):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    proxies = {'https': 'http://127.0.0.1:7890'}
    save_path = "tmp"
    save_path = os.path.abspath(save_path)
    save_path = save_path + "\\" + word + ".mp3"
    return down_word_audio_youdao(word, proxies, headers, save_path)


# 删除指定文件夹中的所有文件
def delete_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def open_file(file_path, out_path):
    print("处理: ", file_path)
    delete_files("tmp")
    # delete_files("target")
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    if len(lines) == 0:
        print("文件: " + file_path + "为空")
        return
    flag = lines[0].strip()
    if flag != "#":
        print("文件: " + file_path + "不符合指定格式，请保证第一行为#,后面每行一个单词")
        return
    if len(lines) == 1:
        print("文件: " + file_path + "没有单词")
        return
    lines.pop(0)
    # print("开始下载音频")
    index = 1
    for line in lines:
        # 获取每个单词的音频
        word = line.strip()
        # print("下载 " + word)
        down_word_audio(word)
        delay = random.uniform(0.5, 1)
        time.sleep(delay)
        index += 1
    # print("音频下载完成")
    # print("开始合并音频")
    target_audio = AudioSegment.empty()
    target_audio += AudioSegment.silent(duration=2000)
    # 创建3秒的空白音频
    blank_duration = 1000 * 3  # 空白音频持续时间，单位为毫秒
    blank_audio = AudioSegment.silent(duration=blank_duration)
    for root, dirs, files in os.walk("tmp"):
        index = 1
        shuffled_list = random.sample(files, len(files))
        for file in shuffled_list:
            file_path = os.path.join(root, file)
            # print("合成 " + file_path)
            audio = AudioSegment.from_file(file_path)
            repeat = 2  # 重复次数
            if int(repeat) > 1:
                for i in range(repeat):
                    target_audio += audio + blank_audio
            else:
                target_audio += audio + blank_audio
            index += 1
    target_audio.export(out_path, format="mp3")
    # print("合并音频完成")


folder_path = "out/四级"  # 替换为你的文件夹路径
out_listen = "out_listen/四级"
# 获取指定文件夹下的文件列表
file_list = os.listdir(folder_path)
print(len(file_list))
# 遍历文件列表
for file_name in range(len(file_list)):
    file_path = folder_path + "/" + str(file_name) + "/listen.txt"
    # print(file_path)
    tmp_out_listen = out_listen + "/" + str(file_name) + ".mp3"
    # print(tmp_out_listen)
    try:
        open_file(file_path, tmp_out_listen)
    except Exception as e:
        print("error")
        open_file(file_path, tmp_out_listen)
# for file_name in file_list:
#     file_path = folder_path + "/" + file_name + "/listen.txt"
#     # print(file_path)
#     tmp_out_listen = out_listen + "/" + file_name + ".mp3"
#     # print(tmp_out_listen)
#     try:
#         open_file(file_path, tmp_out_listen)
#     except Exception as e:
#         print("error")
#         open_file(file_path, tmp_out_listen)
print("program is end.")

