import requests
from PIL import Image
import pytesseract

# 验证码地址
url = "https://img-blog.csdnimg.cn/20200729141658437.png"
response = requests.get(url).content

# 将图片保存在当前目录下
with open('yzm.png', 'wb') as f:
    f.write(response)
f.close()

'''识别验证码'''
# 通过内置模块PIL打开文件
image = Image.open('yzm.png')

# 识别图片，打印输出
result = pytesseract.image_to_string(image)
print(result)
