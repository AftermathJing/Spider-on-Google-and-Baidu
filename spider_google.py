from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from PIL import Image
import base64
import threading
import traceback
import os
import glob
import io
import time
import random
import requests
import datetime

TIME_DELAY_THUMBNAIL = 10  # 缩略图查找时延
TIME_DELAY_IMAGE = 30  # 高清图查找时延


def download_image(xpath: str, browser: webdriver.Chrome, path: str) -> bool:
    # image_source = browser.find_element(by=By.XPATH, value=f'{xpath}').get_attribute('src')
    # if image_source:
    #     base64_str = image_source.split(",")[1]
    #     # 解码Base64数据
    #     image_data = base64.b64decode(base64_str)
    # # 将图像数据保存为图片文件
    # with open(path, "wb") as file:
    #     file.write(image_data)
    try:
        # 找到缩略图
        thumbnail = None
        start_time = datetime.datetime.now()
        while not thumbnail:
            end_time = datetime.datetime.now()
            # 计算时间差
            time_delta = end_time - start_time
            # 时延过大，无法选择直接返回
            if time_delta.total_seconds() > TIME_DELAY_THUMBNAIL:
                return False
            try:
                thumbnail = browser.find_element(by=By.XPATH, value=f'{xpath}')
            except Exception:
                pass
        # 点击缩略图，找到高清图
        thumbnail.click()
        image_xpath = '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]'
        # 获取高清图url
        image_url = thumbnail.get_attribute('src')  # 初始化url
        if_update_url = False  # url是否更新
        start_time = datetime.datetime.now()
        while not if_update_url:
            end_time = datetime.datetime.now()
            # 计算时间差
            time_delta = end_time - start_time
            # 时延过大跳转下一个
            if time_delta.total_seconds() > TIME_DELAY_IMAGE:
                break
            try:
                temp = image_url
                image_url = browser.find_element(by=By.XPATH, value=f'{image_xpath}').get_attribute('src')
                if_update_url = True if temp != image_url else False  # 判断是否更新url
            except Exception:
                pass
        if image_url.startswith('https:'):
            headers = {'User-Agent':
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36}',
                       'Accept':
                           'image/avif,image/webp,image/apng',
                       'Referer':
                           'https://www.google.com'
                       }
            # 获取图片
            image_data = requests.get(url=image_url, headers=headers).content
            # if image_url.endswith('.png'):
            #     path = path + '.png'
            #     # 将图像数据保存为图片文件
            #     with open(path, "wb") as file:
            #         file.write(image_data)
            #
            #     # 将图像数据转换为PIL图像对象
            #     image = Image.open(io.BytesIO(image_data))
            #
            #     # 将图像转换为JPEG格式
            #     if image.mode != "RGB":
            #         image = image.convert("RGB")
            #
            #     # 保存图像为JPEG文件
            #     image.save(path, "JPEG")
            # else:
            #     path = path + '.jpg'
            #     # 将图像数据保存为图片文件
            #     with open(path, "wb") as file:
            #         file.write(image_data)

        elif image_url.startswith('data:'):
            # 获得Base64数据
            base64_str = image_url.split(",")[1]
            # 解码Base64数据
            image_data = base64.b64decode(base64_str)
        else:
            return False

        try:
            path = path + '.jpg' if if_update_url else path + '_thumbnail.jpg'
            # 将图像数据转换为PIL图像对象
            image = Image.open(io.BytesIO(image_data))

            # 将图像转换为JPEG格式
            if image.mode != "RGB":
                image = image.convert("RGB")

            # 保存图像为JPEG文件
            image.save(path, "JPEG")
            return True
        except Exception:
            traceback.print_exc()
    except Exception:
        traceback.print_exc()
        return False


def get_last_file(folder_path):
    file_paths = glob.glob(os.path.join(folder_path, "*"))
    sorted_files = sorted(file_paths, key=os.path.getmtime)
    last_file_path = sorted_files[-1]
    return last_file_path


class MyThread(threading.Thread):
    def __init__(self, keywords: str, num: int):
        self.keywords = keywords
        self.num = num
        super().__init__()

    def run(self) -> None:
        try:
            # 打开浏览器
            with webdriver.Chrome() as browser:
                browser.get(f'https://www.google.com/search?q={self.keywords}&tbm=isch&source=lnm')
                # time.sleep(10)
                path = './dataset/dataset_' + self.keywords.strip().replace(' ', '_')
                if not os.path.exists(path):
                    os.mkdir(path)
                begin = len(os.listdir(path)) + 1

                # 获得 i 和 k
                if len(os.listdir(path)) == 0:
                    i = 1
                else:
                    last_file_path = get_last_file(path)
                    last_file_name = last_file_path.replace('.jpg', '').replace('_thumbnail', '').split('_')
                    k_str = last_file_name[-1]
                    i_str = last_file_name[-2]
                    try:
                        i = int(i_str)
                        k = int(k_str) + 1
                    except Exception:
                        i = int(k_str) + 1
                        k = 1

                while len(os.listdir(path)) < self.num + begin:
                    if i <= 50:
                        xpath = f"//*[@id=\"islrg\"]/div[1]/div[{i}]/a[1]/div[1]/img"
                        image_path = path + '/' + self.keywords.strip().replace(' ', '_') + '_' + str(i)  # + '.jpg'
                        download_image(xpath, browser, image_path)

                    else:
                        failure_times = 0
                        while failure_times < 5 and len(os.listdir(path)) < self.num + begin:
                            xpath = f"//*[@id=\"islrg\"]/div[1]/div[{i}]/div[{k}]/a[1]/div[1]/img"
                            image_path = path + '/' + self.keywords.strip().replace(' ', '_') + '_' + str(i) + '_' + str(k)  # + '.jpg'
                            # time.sleep(random.randint(1, 3))
                            flag = download_image(xpath, browser, image_path)
                            failure_times = 0 if flag else failure_times + 1
                            # ActionChains(browser).move_by_offset(xoffset=0, yoffset=30)
                            k += 1
                    i += 1
                    k = 1

        except Exception:
            traceback.print_exc()


try:
    thread_potholed = MyThread('potholed road surface', 1000)
    # thread_normal = MyThread('smooth road surface', 2000)
    thread_potholed.start()
    # thread_normal.start()
except Exception:
    traceback.print_exc()

# Google图片xpath
# //*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[24]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[26]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[27]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[44]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[49]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[50]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[51]/div[1]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[51]/div[6]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[54]/div[101]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[54]/div[10]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[53]/div[99]/a[1]/div[1]/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img
# //*[@id="islrg"]/div[1]/div[54]/div[22]/a[1]/div[1]/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/c-wiz/div/div/div/div/div[3]/div[1]/div[1]/a[1]/div[1]/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/c-wiz/div/div/div/div/div[3]/div[2]/div[1]/a[1]/div[1]/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/c-wiz/div/div/div/div/div[3]/div[2]/div[4]/a[1]/div[1]/img
# //*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/c-wiz/div/div/div/div/div[3]/div[1]/div[4]/a[1]/div[1]/img
