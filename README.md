在获取翻译网站的指定单词音频时
设置了代理
proxies = {'https': 'http://127.0.0.1:7890'}
response = requests.get(url, data="", proxies=proxies, headers=headers)
这里的7890端口为vpn软件中开放的端口
如果不添加该设置在下载音频时会报错

间隔即每个单词之间的时间间隔
重复即每个单词的重复次数

新建文本文件，第一行为#，之后每行都存放一个单词

使用该软件需要安装ffmpeg，同时配置到环境变量Path当中

该软件为单词听写软件，可点击菜单打开，打开符合要求的文本文件，或者直接打开mp3格式的文件

也可直接拖拽指软件窗口