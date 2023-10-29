import os
import requests
import threading
import time
import random
import traceback
import xml

url = "https://image.baidu.com/search/acjson"


def get_picture_url(keyword: str, times: int) -> list:
    global url
    headers = {'User-Agent':
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36}',
               'Connection':
                   'keep - alive'
               }

    params = {'tn': 'resultjson_com', 'logid': '9476014156012216682', 'ipn': 'rj', 'ct': '201326592', 'is': '', 'fp': 'result', 'fr': '', 'word': f'{keyword}', 'queryWord': f'{keyword}', 'cl': '2', 'lm': '-1', 'ie': 'utf-8', 'oe': 'utf-8', 'adpicid': '', 'st': '-1', 'z': '', 'ic': '', 'hd': '', 'latest': '', 'copyright': '', 's': '', 'se': '', 'tab': '', 'width': '', 'height': '', 'face': '0', 'istype': '2', 'qc': '', 'nc': '1', 'expermode': '', 'nojc': '', 'isAsync': '', 'pn': f'{times*30}', 'rn': '30', 'gsm': '1e', '1698419352159': ''}
    # 携带请求头和params表达发送请求
    response = requests.get(url=url, headers=headers, params=params)
    if response.status_code == 200:
        # 设置编码格式
        response.encoding = 'utf-8'
        try:
            # 转换为json
            json_dict = response.json()
        except Exception:
            traceback.print_exc()
            return []

        # 定位到30个图片上一层
        data_list = json_dict['data']
        # 删除列表中最后一个空值
        del data_list[-1]
        # 用于存储图片链接的列表
        img_url_list = []
        for i in data_list:
            img_url = i['thumbURL']
            img_url_list.append(img_url)
        # 返回图片列表
        return img_url_list
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return []


def get_down_img(img_url_list: list, dir: str, num: int):
    type = dir.split('_')[1]
    # 在当前路径下生成存储图片的文件夹
    if not os.path.exists(f'./dataset/{dir}'):
        os.mkdir(f'./dataset/{dir}')
    # 定义图片编号
    n = len(os.listdir(f'./dataset/{dir}'))
    if n > num:
        return False

    if not list:
        return True

    for img_url in img_url_list:
        # 图片编号递增
        n = n + 1
        headers = {'User-Agent':
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36}',
                   'Connection':
                       'keep - alive'
                   }
        # 获取图片
        img_data = requests.get(url=img_url, headers=headers).content
        # 拼接图片存放地址和名字
        img_path = f'./dataset/{dir}/{type}' + str(n) + '.jpg'
        # 将图片写入指定位置
        with open(img_path, 'wb') as f:
            f.write(img_data)

    return True


class MyThread(threading.Thread):

    def __init__(self, dir: str, keywords: str, num: int):
        self.dir = dir
        self.keywords = keywords
        self.num = num
        super().__init__()

    def run(self) -> None:
        n = 1
        flag = True
        while flag:
            flag = get_down_img(img_url_list=get_picture_url(keyword=self.keywords, times=n), dir=self.dir, num=self.num)
            time.sleep(random.randint(0, 5))
            n += 1


try:
    th_girl = MyThread(dir="dataset_girl", keywords="二次元萌妹图片", num=200)
    th_boy = MyThread(dir="dataset_boy", keywords="二次元帅哥图片", num=200)
    th_building = MyThread(dir="dataset_building", keywords="二次元建筑图片", num=200)
    th_girl.start()
    th_boy.start()
    th_building.start()
except Exception:
    traceback.print_exc()
