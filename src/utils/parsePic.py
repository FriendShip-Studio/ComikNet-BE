import hashlib
import math
from PIL import Image
from io import BytesIO

# 获得图片分割数


def GetSegmentationNum(epsId, scramble_id, pictureName):
    scramble_id = int(scramble_id)
    epsId = int(epsId)
    if epsId < scramble_id:
        num = 0
    elif epsId < 268850:
        num = 10
    else:
        string = str(epsId) + pictureName
        string = string.encode()
        string = hashlib.md5(string).hexdigest()
        num = ord(string[-1])
        num %= 10
        num = num * 2 + 2
    return num

# 图片分割合成


def SegmentationPicture(imgData, epsId, scramble_id, bookId):
    num = GetSegmentationNum(epsId, scramble_id, bookId)
    if num <= 1:
        return imgData

    src = BytesIO(imgData)
    srcImg = Image.open(src)

    size = (width, height) = srcImg.size
    desImg = Image.new(srcImg.mode, size)
    format = srcImg.format

    rem = height % num
    copyHeight = math.floor(height / num)
    block = []
    totalH = 0
    for i in range(num):
        h = copyHeight * (i + 1)
        if i == num - 1:
            h += rem
        block.append((totalH, h))
        totalH = h

    h = 0
    for start, end in reversed(block):
        coH = end - start
        temp_img = srcImg.crop((0, start, width, end))
        desImg.paste(temp_img, (0, h, width, h + coH))
        h += coH

    srcImg.close()
    src.close()

    des = BytesIO()
    desImg.save(des, format)
    value = des.getvalue()
    desImg.close()
    des.close()
    return value
