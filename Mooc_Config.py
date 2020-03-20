
import re

# ftp
HOST = ''
PORT = 21
USERNAME = ''
PASSWORD = ''
BUFSIZE = 1024

# 
TIMEOUT = 60
WIN_LENGTH = 64
winre = re.compile(r'[?*|<>:"/\\\s]')  # windoes 文件非法字符匹配

# 课程链接的正则匹配
courses_re = {
    "icourse163": re.compile(r'\s*https?://www.icourse163.org/((learn)|(course))/(.*?)(#/.*)?$'),
}