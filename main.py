import requests
import base64
import execjs
import json
import re
import time

class Mask():
    def __init__(self):
        self.payload = {
            "name": "",
            "cardNo": "",
            "phone": "",
            "pharmacyName": "百姓缘大药房金屯店",
            "pharmacyCode": "1136",
            "reservationNumber": "5",
            "hash": "",
            "timestamp": "",
            "pharmacyPhase": "",
            "pharmacyPhaseName": "",
            "captcha": "",
        }

        self.headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Host": "kzgm.bbshjz.cn:8000",
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Linux; U; Android 2.3.6; zh-cn; GT-S5660 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 MicroMessenger/4.5.255",
                "User-Agent": "MicroMessenger",
                # "X-Requested-With": "XMLHttpRequest",
                "Cookie": ""
            }
        self.base_url = "http://kzgm.bbshjz.cn:8000/ncms"

    def crawl(self):
        url = self.isv(self.base_url + "/mask/book")
        params = self.payload
        headers = self.headers
        headers['Cookie'], params['captcha'] = self.captcha()
        # cookies, params['captcha'] = self.captcha()
        params['pharmacyPhaseName'], params['pharmacyPhase'] = self.get_last()
        params['timestamp'] = str(int(time.time() * 1000) - 30000)
        params['hash'] = self.md5(params['timestamp'])

        print("传递的参数为")
        print(params)
        response = requests.post(url=url, data=json.dumps(params), headers=headers)
        print("获取的数据为")
        print(response.json())
        status = response.json()["status"]
        if status == 200:
            return True
        else:
            mes = response.json()['msg']
            if "成功" in mes:
                return True
            else:
                return False

        # print(captcha.text)

    def captcha(self):
        captcha_url = self.base_url + "/mask/captcha"
        captcha = requests.get(url=captcha_url, headers=self.headers)
        strings = captcha.text[:257] + 'E' + captcha.text[258:269] + 'E' + captcha.text[270:]

        with open("captcha.jpg", "wb") as f:
            f.write(base64.urlsafe_b64decode(strings))
        while "Set-Cookie" not in captcha.headers:
            print(captcha.headers)
            captcha = requests.get(url=captcha_url, headers=self.headers)
            time.sleep(3)
        print(captcha.headers)
        # return captcha.cookies, self.slove_captcha(strings)
        return captcha.headers['Set-Cookie'].split(';')[0], self.slove_captcha(strings)


    def slove_captcha(self, img):
        params = {"image": img}
        baidu_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        access_token = ""
        baidu_ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        response = requests.post(url=baidu_ocr_url + "?access_token=" + access_token, data=params, headers=baidu_headers)
        print(response.json()['words_result'][0]['words'])
        return response.json()['words_result'][0]['words']


    def get_js(self):
        f = open("isv.js", 'r', encoding='UTF-8')
        line = f.readline()
        htmlstr = ""
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        return htmlstr

    def isv(self, url):
        ctx = execjs.compile(self.get_js())
        return ctx.call('isvData', url)

    def md5(self, content):
        ctx = execjs.compile(self.get_js())
        return ctx.call('hex_md5', str(content) + "c7c7405208624ed90976f0672c09b884")

    def get_last(self):
        url = self.base_url + "/mask/pharmacy-stock?code=1136"
        response = requests.get(url=self.isv(url), headers=self.headers)
        print(self.isv(url))
        text = re.findall(r'"text":"(.*?)","value":"(.*?)"', response.json()['msg'])[1]
        return text

if __name__ == '__main__':
    mask = Mask()

    currentTimeStamp = time.time()  # 获取当前时间戳
    time_local = time.localtime(currentTimeStamp)  # 格式化时间戳为本地时间
    time_YmdHMS = time.strftime("%Y%m%d_%H%M%S", time_local)  # 自定义时间格式
    print('currentTimeStamp:', currentTimeStamp)
    print('time_local:', time_local)
    print('time_YmdHMS:', time_YmdHMS)

    status = mask.crawl()
    if status is False:

        currentTimeStamp = time.time()  # 获取当前时间戳
        time_local = time.localtime(currentTimeStamp)  # 格式化时间戳为本地时间
        time_YmdHMS = time.strftime("%Y%m%d_%H%M%S", time_local)  # 自定义时间格式
        print('currentTimeStamp:', currentTimeStamp)
        print('time_local:', time_local)
        print('time_YmdHMS:', time_YmdHMS)

        time.sleep(10)
        status = mask.crawl()
    else:
        print("抢到了")
