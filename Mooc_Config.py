import re

# 
TIMEOUT = 60

# 课程链接的正则匹配
courses_re = {
    "icourse163": re.compile(r'\s*https?://www.icourse163.org/((learn)|(course))/(.*?)(#/.*)?$'),
}