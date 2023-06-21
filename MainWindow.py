from ui_MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QFileDialog, QProgressDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import os
import configparser
import requests
import time
import random
from pydub import AudioSegment
import subprocess


# 读取配置文件
def read_config_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


# 写入配置文件
def write_config_file(file_path, config):
    with open(file_path, "w") as file:
        config.write(file)


config = read_config_file("config.ini")
# # 设置ffmpeg路径
# AudioSegment.converter = "ffmpeg/bin/ffmpeg.exe"
# AudioSegment.ffmpeg = "ffmpeg/bin/ffmpeg.exe"
# AudioSegment.ffprobe = "ffmpeg/bin/ffprobe.exe"

def show_message_box(self, msg):
    # 创建一个信息提示框
    message_box = QMessageBox(self)
    message_box.setWindowTitle("提示")
    message_box.setText(msg)
    message_box.setIcon(QMessageBox.Information)
    message_box.exec_()


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
    if config.get("WD_CONFIG", "PROXY") == "no":
        proxies = {}
    save_path = "tmp"
    save_path = os.path.abspath(save_path)
    save_path = save_path + "\\" + word + ".mp3"
    if config.get("WD_CONFIG", "SOURCE") == "baidu":
        return down_word_audio_baidu(word, proxies, headers, save_path)
    elif config.get("WD_CONFIG", "SOURCE") == "youdao":
        return down_word_audio_youdao(word, proxies, headers, save_path)
    elif config.get("WD_CONFIG", "SOURCE") == "sougou":
        return down_word_audio_sougou(word, proxies, headers, save_path)
    elif config.get("WD_CONFIG", "SOURCE") == "google":
        return down_word_audio_google(word, proxies, headers, save_path)
    else:
        return

# 删除指定文件夹中的所有文件
def delete_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def open_file(self, file_path):
    file_path2 = file_path
    print("处理: ", file_path)
    file_name, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == ".mp3":
        self.player.pause()
        audio_file = QUrl.fromLocalFile(file_path)
        self.player.setMedia(QMediaContent(audio_file))
        self.play_status = "play"
        self.ui.play.setIcon(QIcon("img/play.png"))
        self.ui.replay.setParent(None)
        self.ui.speed.setValue(1.0)
        self.ui.label.setText(os.path.basename(file_path2))
    elif file_extension.lower() == ".txt":
        delete_files("tmp")
        delete_files("target")
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        if len(lines) == 0:
            show_message_box(self, "文件: " + file_path + "为空")
            return
        flag = lines[0].strip()
        if flag != "#":
            show_message_box(self, "文件: " + file_path + "不符合指定格式，请保证第一行为#,后面每行一个单词")
            return
        if len(lines) == 1:
            show_message_box(self, "文件: " + file_path + "没有单词")
            return
        lines.pop(0)
        print("开始下载音频")
        index = 1
        for line in lines:
            # 获取每个单词的音频
            word = line.strip()
            print("下载 " + word)
            self.ui.label.setText("下载 " + str(index) + "/" + str(len(lines)))
            down_word_audio(word)
            delay = random.uniform(0.5, 1)
            time.sleep(delay)
            index += 1
        print("音频下载完成")
        print("开始合并音频")
        target_audio = AudioSegment.empty()
        target_audio += AudioSegment.silent(duration=2000)
        # 创建3秒的空白音频
        blank = config.get("WD_CONFIG", "PADDING_TIME")
        blank_duration = 1000 * int(blank)  # 空白音频持续时间，单位为毫秒
        blank_audio = AudioSegment.silent(duration=blank_duration)
        for root, dirs, files in os.walk("tmp"):
            index = 1
            shuffled_list = files
            if config.get("WD_CONFIG", "ORDER") == "no":
                shuffled_list = random.sample(files, len(files))
            for file in shuffled_list:
                file_path = os.path.join(root, file)
                print("合成 " + file_path)
                self.ui.label.setText("合成 " + str(index) + "/" + str(len(lines)))
                audio = AudioSegment.from_file(file_path)
                repeat = config.get("WD_CONFIG", "REPEAT")
                if int(repeat) > 1:
                    for i in range(repeat):
                        target_audio += audio + blank_audio
                else:
                    target_audio += audio + blank_audio
                index += 1
        target_audio.export("target/target.mp3", format="mp3")
        print("合并音频完成")
        self.player.pause()
        audio_file = QUrl.fromLocalFile("target/target.mp3")
        self.player.setMedia(QMediaContent(audio_file))
        self.play_status = "play"
        self.ui.play.setIcon(QIcon("img/play.png"))
        self.ui.replay.setParent(None)
        self.ui.speed.setValue(1.0)
        self.ui.label.setText(os.path.basename(file_path2))
    else:
        show_message_box(self, "只能处理mp3和txt")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("24_单词听写")
        self.setWindowIcon(QIcon("img/word.png"))
        self.ui.actionnew.setText("新建")
        self.ui.actionnew.setIcon(QIcon("img/new.png"))
        self.ui.actionopen.setText("打开")
        self.ui.actionopen.setIcon(QIcon("img/open.png"))
        self.ui.actionrepeat.setText("重复")
        self.ui.actionpadding_time.setText("间隔")
        self.ui.actionbaidu.setText("百度翻译")
        self.ui.actionyoudao.setText("有道翻译")
        self.ui.actionsougou.setText("搜狗翻译")
        self.ui.actiongoogle.setText("谷歌翻译")
        self.set_action_source()
        self.ui.actionp_open.setText("代理开启")
        self.ui.actionp_close.setText("代理关闭")
        if config.get("WD_CONFIG", "PROXY") == "yes":
            self.ui.actionp_open.setIcon(QIcon("img/ok.png"))
        else:
            self.ui.actionp_close.setIcon(QIcon("img/ok.png"))
        self.ui.actionorder.setText("顺序")
        self.ui.actionunorder.setText("乱序")
        if config.get("WD_CONFIG", "ORDER") == "yes":
            self.ui.actionorder.setIcon(QIcon("img/ok.png"))
        else:
            self.ui.actionunorder.setIcon(QIcon("img/ok.png"))
        self.ui.play.setText("")
        self.ui.play.setIcon(QIcon("img/play.png"))
        self.ui.play.setIconSize(self.ui.play.size())
        self.ui.replay.setText("")
        self.ui.replay.setIcon(QIcon("img/repeat.png"))
        self.ui.replay.setIconSize(self.ui.play.size())
        self.ui.replay.setParent(None)
        self.ui.speed.setSingleStep(0.1)
        self.ui.speed.setMaximum(3.0)
        self.ui.speed.setValue(1.0)
        self.ui.label.setText("单词听写")

        self.play_status = "play"
        self.player = QMediaPlayer(self)
        # audio_file = QUrl.fromLocalFile(r"D:\workspace\python\24_word_dictation\22.mp3")
        # self.player.setMedia(QMediaContent(audio_file))

        self.ui.actionopen.triggered.connect(self.action_open)
        self.ui.actionnew.triggered.connect(self.action_new)
        self.ui.actionpadding_time.triggered.connect(self.action_padding_time)
        self.ui.actionrepeat.triggered.connect(self.action_repeat)
        self.ui.actionbaidu.triggered.connect(self.action_baidu)
        self.ui.actionyoudao.triggered.connect(self.action_youdao)
        self.ui.actionsougou.triggered.connect(self.action_sougou)
        self.ui.actiongoogle.triggered.connect(self.action_google)
        self.ui.actionp_open.triggered.connect(self.action_proxy_open)
        self.ui.actionp_close.triggered.connect(self.action_proxy_close)
        self.ui.actionorder.triggered.connect(self.action_order)
        self.ui.actionunorder.triggered.connect(self.action_unorder)

        self.ui.play.clicked.connect(self.play_or_pause)
        self.ui.replay.clicked.connect(self.replay)
        self.ui.progress.sliderMoved.connect(self.update_position_func)
        self.ui.progress.valueChanged.connect(self.slider_value_changed)
        self.player.durationChanged.connect(self.get_duration_func)
        self.player.positionChanged.connect(self.get_position_func)
        self.ui.speed.valueChanged.connect(self.speed_change)

        self.setAcceptDrops(True)

    def action_proxy_open(self):
        config.set("WD_CONFIG", "PROXY", "yes")
        self.ui.actionp_open.setIcon(QIcon("img/ok.png"))
        self.ui.actionp_close.setIcon(QIcon())
        write_config_file("config.ini", config)

    def action_proxy_close(self):
        config.set("WD_CONFIG", "PROXY", "no")
        self.ui.actionp_open.setIcon(QIcon())
        self.ui.actionp_close.setIcon(QIcon("img/ok.png"))
        write_config_file("config.ini", config)

    def action_order(self):
        config.set("WD_CONFIG", "ORDER", "yes")
        self.ui.actionorder.setIcon(QIcon("img/ok.png"))
        self.ui.actionunorder.setIcon(QIcon())
        write_config_file("config.ini", config)

    def action_unorder(self):
        config.set("WD_CONFIG", "ORDER", "no")
        self.ui.actionorder.setIcon(QIcon())
        self.ui.actionunorder.setIcon(QIcon("img/ok.png"))
        write_config_file("config.ini", config)

    def action_open(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.exec_()
        selected_files = file_dialog.selectedFiles()
        if len(selected_files) > 0:
            file_path = selected_files[0]
            print("Selected file:", file_path)
            open_file(self, file_path)

    def action_new(self):
        subprocess.Popen('notepad.exe')

    def action_padding_time(self):
        default_text = config.get("WD_CONFIG", "padding_time")
        text, ok = QInputDialog.getText(self, "设置间隔时间", "请输入:", text=default_text)
        if ok:
            try:
                target = int(text)
                if target < 0:
                    return
                config.set("WD_CONFIG", "padding_time", str(target))
                write_config_file("config.ini", config)
            except ValueError as e:
                print("error")

    def action_repeat(self):
        default_text = config.get("WD_CONFIG", "repeat")
        text, ok = QInputDialog.getText(self, "设置重复次数", "请输入:", text=default_text)
        if ok:
            try:
                target = int(text)
                if target < 0:
                    return
                config.set("WD_CONFIG", "repeat", str(target))
                write_config_file("config.ini", config)
            except ValueError as e:
                print("error")

    def set_action_source(self):
        if config.get("WD_CONFIG", "SOURCE") == "baidu":
            self.ui.actionbaidu.setIcon(QIcon("img/ok.png"))
        elif config.get("WD_CONFIG", "SOURCE") == "youdao":
            self.ui.actionyoudao.setIcon(QIcon("img/ok.png"))
        elif config.get("WD_CONFIG", "SOURCE") == "sougou":
            self.ui.actionsougou.setIcon(QIcon("img/ok.png"))
        elif config.get("WD_CONFIG", "SOURCE") == "google":
            self.ui.actiongoogle.setIcon(QIcon("img/ok.png"))

    def clear_action_source(self):
        if config.get("WD_CONFIG", "SOURCE") == "baidu":
            self.ui.actionbaidu.setIcon(QIcon())
        elif config.get("WD_CONFIG", "SOURCE") == "youdao":
            self.ui.actionyoudao.setIcon(QIcon())
        elif config.get("WD_CONFIG", "SOURCE") == "sougou":
            self.ui.actionsougou.setIcon(QIcon())
        elif config.get("WD_CONFIG", "SOURCE") == "google":
            self.ui.actiongoogle.setIcon(QIcon())

    def action_baidu(self):
        self.clear_action_source()
        config.set("WD_CONFIG", "SOURCE", "baidu")
        self.set_action_source()
        write_config_file("config.ini", config)

    def action_youdao(self):
        self.clear_action_source()
        config.set("WD_CONFIG", "SOURCE", "youdao")
        self.set_action_source()
        write_config_file("config.ini", config)

    def action_sougou(self):
        self.clear_action_source()
        config.set("WD_CONFIG", "SOURCE", "sougou")
        self.set_action_source()
        write_config_file("config.ini", config)

    def action_google(self):
        self.clear_action_source()
        config.set("WD_CONFIG", "SOURCE", "google")
        self.set_action_source()
        write_config_file("config.ini", config)

    def speed_change(self, v):
        self.player.setPlaybackRate(v)

    def replay(self):
        self.play_status = "pause"
        self.ui.play.setIcon(QIcon("img/pause.png"))
        self.player.pause()
        self.player.setPosition(0)
        self.player.play()

    def play_or_pause(self):
        if self.play_status == "play":
            self.player.play()
            self.play_status = "pause"
            self.ui.play.setIcon(QIcon("img/pause.png"))
            self.ui.horizontalLayout.addWidget(self.ui.replay)
        elif self.play_status == "pause":
            self.player.pause()
            self.play_status = "continue"
            self.ui.play.setIcon(QIcon("img/continue.png"))
        else:
            self.player.play()
            self.play_status = "pause"
            self.ui.play.setIcon(QIcon("img/pause.png"))

    def get_time_func(self, d):
        seconds = int(d / 1000)
        minutes = int(seconds / 60)
        seconds -= minutes * 60
        if minutes == 0 and seconds == 0:
            self.ui.time.setText('--/--')
            self.ui.play.setIcon(QIcon('img/play.png'))
        else:
            self.ui.time.setText('{}:{}'.format(minutes, seconds))

    def update_position_func(self, v):
        self.player.setPosition(v)
        d = self.ui.progress.maximum() - v
        self.get_time_func(d)

    def get_duration_func(self, d):
        self.ui.progress.setRange(0, d)
        self.ui.progress.setEnabled(True)
        self.get_time_func(d)

    def get_position_func(self, p):
        self.ui.progress.setValue(p)
        v = self.ui.progress.value()
        d = self.ui.progress.maximum() - v
        self.get_time_func(d)

    def slider_value_changed(self):
        if self.ui.progress.value() == self.ui.progress.maximum():
            self.play_status = "play"
            self.ui.play.setIcon(QIcon("img/play.png"))
            self.ui.replay.setParent(None)

    '''
    处理拖拽文件事件
    '''

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.process_dropped_files(file_paths)
            event.acceptProposedAction()

    def process_dropped_files(self, file_paths):
        # 在这里处理拖放的文件
        for file_path in file_paths:
            open_file(self, file_path)
            break
