import time
import hashlib
import re
import io
import base64
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..config import app_config

TIMEOUT = 7200
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


# 随机颜色1:
def _rndcolor():
    return random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)


# 随机颜色2:
def _rndcolor2():
    return random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)


# 生成验证图片
def rndpic():
    # 240 x 60:
    width = 60 * 4
    height = 80
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    if app_config['app']['settings']['debug']:
        font = ImageFont.truetype('华文黑体.ttf', 40)
    else:
        font = ImageFont.truetype('/usr/share/fonts/truetype/heiti.ttf', 40)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=_rndcolor())
    list_bchar = []
    # 输出文字:
    for t in range(4):
        code_list = [0x96d5, 0x864e, 0x7684, 0x4e00, 0x4e86, 0x662f,
                     0x6211, 0x4e0d, 0x5728, 0x4eba, 0x4eec, 0x6709,
                     0x6765, 0x4ed6, 0x8fd9, 0x4e0a, 0x7740, 0x4e2a,
                     0x5730, 0x5230, 0x5927, 0x91cc, 0x8bf4, 0x5c31,
                     0x53bb, 0x5b50, 0x5f97, 0x4e5f, 0x548c, 0x90a3,
                     0x8981, 0x4e0b, 0x770b, 0x5929, 0x65f6, 0x8fc7,
                     0x51fa, 0x5c0f, 0x4e48, 0x8d77, 0x4f60, 0x90fd,
                     0x628a, 0x597d, 0x8fd8, 0x591a, 0x6ca1, 0x4e3a,
                     0x53c8, 0x53ef, 0x5bb6, 0x5b66, 0x53ea, 0x4ee5,
                     0x4e3b, 0x4f1a, 0x6837, 0x5e74, 0x60f3, 0x751f,
                     0x540c, 0x8001, 0x4e2d, 0x5341, 0x4ece, 0x81ea,
                     0x9762, 0x524d, 0x5934, 0x9053, 0x5b83, 0x540e,
                     0x7136, 0x8d70, 0x5f88, 0x50cf, 0x89c1, 0x4e24,
                     0x7528, 0x5979, 0x56fd, 0x52a8, 0x8fdb, 0x6210,
                     0x56de, 0x4ec0, 0x8fb9, 0x4f5c, 0x5bf9, 0x5f00,
                     0x800c, 0x5df1, 0x4e9b, 0x73b0, 0x5c71, 0x6c11,
                     0x5019, 0x7ecf, 0x53d1, 0x5de5, 0x5411, 0x4e8b,
                     0x547d, 0x7ed9, 0x957f, 0x6c34, 0x51e0, 0x4e49,
                     0x4e09, 0x58f0, 0x4e8e, 0x9ad8, 0x624b, 0x77e5,
                     0x7406, 0x773c, 0x5fd7, 0x70b9, 0x5fc3, 0x6218,
                     0x4e8c, 0x95ee, 0x4f46, 0x8eab, 0x65b9, 0x5b9e,
                     0x5403, 0x505a, 0x53eb, 0x5f53, 0x4f4f, 0x542c,
                     0x9769, 0x6253, 0x5462, 0x771f, 0x5168, 0x624d,
                     0x56db, 0x5df2, 0x6240, 0x654c, 0x4e4b, 0x6700,
                     0x5149, 0x4ea7, 0x60c5, 0x8def, 0x5206, 0x603b,
                     0x6761, 0x767d, 0x8bdd, 0x4e1c, 0x5e2d, 0x6b21,
                     0x4eb2, 0x5982, 0x88ab, 0x82b1, 0x53e3, 0x653e,
                     0x513f, 0x5e38, 0x6c14, 0x9ec4, 0x4e94, 0x7b2c,
                     0x4f7f, 0x5199, 0x519b, 0x6728, 0x73cd, 0x5427,
                     0x6587, 0x8fd0, 0x518d, 0x679c, 0x600e, 0x5b9a,
                     0x8bb8, 0x5feb, 0x660e, 0x884c, 0x56e0, 0x522b,
                     0x98de, 0x5916, 0x6811, 0x7269, 0x6d3b, 0x90e8,
                     0x95e8, 0x65e0, 0x5f80, 0x8239, 0x671b, 0x65b0,
                     0x5e26, 0x961f, 0x5148, 0x529b, 0x5b8c, 0x5374,
                     0x7ad9, 0x4ee3, 0x5458, 0x673a, 0x66f4, 0x4e5d,
                     0x60a8, 0x6bcf, 0x98ce, 0x7ea7, 0x8ddf, 0x7b11,
                     0x554a, 0x5b69, 0x4e07, 0x5c11, 0x76f4, 0x610f,
                     0x591c, 0x6bd4, 0x9636, 0x8fde, 0x8f66, 0x91cd,
                     0x4fbf, 0x6597, 0x9a6c, 0x54ea, 0x5316, 0x592a,
                     0x6307, 0x53d8, 0x793e, 0x4f3c, 0x58eb, 0x8005,
                     0x5e72, 0x77f3, 0x6ee1, 0x6885, 0x65e5, 0x51b3,
                     0x767e, 0x539f, 0x62ff, 0x7fa4, 0x7a76, 0x5404,
                     0x516d, 0x672c, 0x601d, 0x89e3, 0x7acb, 0x6cb3,
                     0x6751, 0x516b, 0x96be, 0x65e9, 0x8bba, 0x5417,
                     0x6839, 0x5171, 0x8ba9, 0x76f8, 0x7814, 0x4eca,
                     0x5176, 0x4e66, 0x5750, 0x63a5, 0x5e94, 0x5173,
                     0x4fe1, 0x89c9, 0x6b65, 0x53cd, 0x5904, 0x8bb0,
                     0x5c06, 0x5343, 0x627e, 0x4e89, 0x9886, 0x6216,
                     0x5e08, 0x7ed3, 0x5757, 0x8dd1, 0x8c01, 0x8349,
                     0x8d8a, 0x5b57, 0x52a0, 0x811a, 0x7d27, 0x7231,
                     0x7b49, 0x4e60, 0x9635, 0x6015, 0x6708, 0x9752,
                     0x534a, 0x706b, 0x6cd5, 0x9898, 0x5efa, 0x8d76,
                     0x4f4d, 0x5531, 0x6d77, 0x4e03, 0x5973, 0x4efb,
                     0x4ef6, 0x611f, 0x51c6, 0x5f20, 0x56e2, 0x5c4b,
                     0x79bb, 0x8272, 0x8138, 0x7247, 0x79d1, 0x5012,
                     0x775b, 0x5229, 0x4e16, 0x521a, 0x4e14, 0x7531,
                     0x9001, 0x5207, 0x661f, 0x5bfc, 0x665a, 0x8868,
                     0x591f, 0x6574, 0x8ba4, 0x54cd, 0x96ea, 0x6d41,
                     0x672a, 0x573a, 0x8be5, 0x5e76, 0x5e95, 0x6df1,
                     0x523b, 0x5e73, 0x4f1f, 0x5fd9, 0x63d0, 0x786e,
                     0x8fd1, 0x4eae, 0x8f7b, 0x8bb2, 0x519c, 0x53e4,
                     0x9ed1, 0x544a, 0x754c, 0x62c9, 0x540d, 0x5440,
                     0x571f, 0x6e05, 0x9633, 0x7167, 0x529e, 0x53f2,
                     0x6539, 0x5386, 0x8f6c, 0x753b, 0x9020, 0x5634,
                     0x6b64, 0x6cbb, 0x5317, 0x5fc5, 0x670d, 0x96e8,
                     0x7a7f, 0x5185, 0x8bc6, 0x9a8c, 0x4f20, 0x4e1a,
                     0x83dc, 0x722c, 0x7761, 0x5174, 0x5f62, 0x91cf,
                     0x54b1, 0x89c2, 0x82e6, 0x4f53, 0x4f17, 0x901a,
                     0x51b2, 0x5408, 0x7834, 0x53cb, 0x5ea6, 0x672f,
                     0x996d, 0x516c, 0x65c1, 0x623f, 0x6781, 0x5357,
                     0x67aa, 0x8bfb, 0x6c99, 0x5c81, 0x7ebf, 0x91ce,
                     0x575a, 0x7a7a, 0x6536, 0x7b97, 0x81f3, 0x653f,
                     0x57ce, 0x52b3, 0x843d, 0x94b1, 0x7279, 0x56f4,
                     0x5f1f, 0x80dc, 0x6559, 0x70ed, 0x5c55, 0x5305,
                     0x6b4c, 0x7c7b, 0x6e10, 0x5f3a, 0x6570, 0x4e61,
                     0x547c, 0x97f3, 0x7b54, 0x54e5, 0x9645, 0x65e7,
                     0x795e, 0x5ea7, 0x7ae0, 0x5e2e, 0x5566, 0x53d7,
                     0x7cfb, 0x4ee4, 0x8df3, 0x975e, 0x4f55, 0x725b,
                     0x53d6, 0x5165, 0x5cb8, 0x6562, 0x6389, 0x5ffd,
                     0x79cd, 0x88c5, 0x9876, 0x6025, 0x6234, 0x6797,
                     0x505c, 0x606f, 0x53e5, 0x533a, 0x8863, 0x822c,
                     0x62a5, 0x53f6, 0x538b, 0x6162, 0x53d4, 0x80cc,
                     0x7ec6, 0x8273, 0x4f50]
        var = random.choice(code_list)
        bcahr = chr(var)
        draw.text((60 * t + 10, 15), bcahr, font=font, fill=_rndcolor2())
        list_bchar.append(bcahr)
    all_bchar = ''.join(list_bchar)

    # 模糊:
    image = image.filter(ImageFilter.SMOOTH)
    imgbytearr = io.BytesIO()
    image.save(imgbytearr, format='jpeg')
    imgbytearr = imgbytearr.getvalue()
    b64img = base64.b64encode(imgbytearr)
    return all_bchar, b64img


def get_pic_random_value():
    return ''.join(random.sample(string.ascii_letters + string.digits, 20))


def get_app_session_id(tel_number):
    random_value = ''.join(random.sample(string.ascii_letters + string.digits, 20))
    s = '%s-%s-%s' % (tel_number, random_value, _RE_SHA1)
    l = [tel_number, random_value, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(l)


def gen_token(user):
    expires = str(int(time.time() + TIMEOUT))
    s = '%s-%s-%s' % (user, expires, _RE_SHA1)
    L = [user, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def verify_token(token):
    l = token.split('-')
    if len(l) != 3:
        return None
    user, expires, sha1 = l
    # 如果超时，返回None
    if int(expires) < time.time():
        return None
    s = '%s-%s-%s' % (user, expires, _RE_SHA1)
    if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
        return None
    else:
        return True


def generate_verification_code():
    """ 随机生成6位的验证码 """
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))
    myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string
    return verification_code