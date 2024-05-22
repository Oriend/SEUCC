import requests
import re
import requests.utils
import time
from lxml import etree
import json
import base64
from Crypto.Cipher import AES

PIN = 6

class EncryptDate:
    def __init__(self, key):
        self.key = key                              # 初始化密钥
        self.length = 16                            # 初始化数据块大小
        self.aes = AES.new(self.key, AES.MODE_ECB)  # 初始化AES,ECB模式的实例
        self.unpad = lambda date: date[0:-ord(date[-1])]  # 截断函数，去除填充的字符

    def pad(self, text):
        """
        #填充函数，使被加密数据的字节码长度是block_size的整数倍
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数
        a = self.pad(encrData)
        res = self.aes.encrypt(a.encode("utf-8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        return msg

class grab_lesson():
    def __init__(self, loginname, password, flag=0, begintime=0, type=1, filename=None, label='TJKC'):
        self.session = requests.session()
        self.headers = {}
        self.success_flag = 0
        self.success_num = 0
        self.loginname = loginname
        self.password = password
        self.flag = flag
        self.begintime = begintime
        self.type = type
        self.lessonlist = []
        if not filename is None:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.readlines()
                # print(data, type(data))
                for Data in data:
                    self.lessonlist.append(Data.strip('\n').split(','))
        # print(self.lessonlist)
        self.label=label
                # print(data)
        # self.url = None
        # self.data = {}

    def acq_PIN(self):
        url = 'http://newxk.urp.seu.edu.cn/xsxk/auth/captcha'
        headers = {
            'Referer': 'http://newxk.urp.seu.edu.cn/xsxk/profile/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }
        ack = requests.post(url=url, headers=headers).text
        uuid = re.findall('"uuid": "(.*)"', ack)[0]
        # print('uuid:', uuid)

        return uuid

    def run(self):

        self.headers = {
            'Authorization': None,
            'Host': 'newxk.urp.seu.edu.cn',
            'Origin': 'http://newxk.urp.seu.edu.cn',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://newxk.urp.seu.edu.cn/xsxk/profile/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }

        url = 'http://newxk.urp.seu.edu.cn/xsxk/profile/index.html'
        html = requests.get(url=url, headers=self.headers).text
        aeskey = re.findall('.*?loginVue.loginForm.aesKey = "(.*?)"', html)[0]
        # print(aeskey, type(aeskey))
        aesedata = EncryptDate(aeskey.encode('utf-8'))
        pwd = aesedata.encrypt(self.password)
        # print('pwd:', pwd)
        # print(pwd, type(pwd))

        # etree_html = etree.HTML(html)
        # content = etree_html.xpath('/html/body/script[7]/text()')
        # print(content)
        url = 'http://newxk.urp.seu.edu.cn/xsxk/auth/login'
        try_times = 0
        while True:
            try_times += 1
            uuid = self.acq_PIN()
            print('try times:', try_times)

            data = {'captcha': PIN, 'uuid': uuid}    # 'password': 'HTaXLVcN7BAoYEh6I3xCkw==',

            data['loginname'] = self.loginname
            data['password'] = pwd
            response = self.session.post(url=url, data=data, headers=self.headers).json()
            if response['code'] == 200:
                # print(type(response['data']))
                print('login stage 1 successfully')
                break
            # print(response)

        auth = response['data']['token']
        self.headers['Authorization'] = auth

        url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/seu/user'

        data = {} # 'batchId': 'bea0c6ddb83441da908b34d223cf1d93'
        data['batchId'] = response['data']['student']['electiveBatchList'][self.type]['code']
        # print(data['batchId'])
        # data = '1'
        while True:
            response = self.session.post(url=url, data=data, headers=self.headers).json()
        # print(response)
            if response['code'] == 200:
                print('login stage 2 successfully')
                break

        url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/grablessons?'+'batchId='+data['batchId']+'&'+'token='+self.headers['Authorization']
        refer = url
        self.headers['Upgrade-Insecure-Requests'] = '1'
        data['token'] = self.headers['Authorization']

        self.session.get(url=url, data=data, headers=self.headers)

        # 获取课程
        self.headers['batchId'] = data['batchId']
        self.headers['Referer'] = refer
        # print(refer)
        if self.flag:
            while True:
                ct = time.time()
                local_time = time.localtime(ct)
                data_head = time.strftime("%H:%M:%S", local_time)
                data_secs = (ct - int(ct)) * 1000
                time_stamp = "%s:%03d" % (data_head, data_secs)
                stamp = int("".join(time_stamp.split()[0].split(":")))

                if stamp == self.begintime:
                    break



        url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/list'
        data = {"teachingClassType": self.label, "pageNumber": 2, "pageSize": 10, "orderBy": "", "campus": "1"}
        list = self.session.post(url=url, json=data, headers=self.headers).json()
        if list['code'] == 200:
            print('list successfully')

        # 选课

        url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/add'
        # print(session.cookies)

        data['clazzType'] = self.label
        count = 3
        page = 0
        crouse_idx = 0
        # data['clazzId'] = '202320243B060450001'
        # data['secretVal'] = list['data']['rows'][7]['tcList'][0].get('secretVal')
        # print(data['secretVal'])
        while True:
            for i, lesson in enumerate(self.lessonlist):
                if page != int(lesson[0]):
                    page = int(lesson[0])
                    crouse_idx = int(lesson[1])

                    url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/list'
                    data = {"teachingClassType": self.label, "pageNumber": page, "pageSize": 10, "orderBy": "", "campus": "1"}
                    list = self.session.post(url=url, json=data, headers=self.headers).json()
                    if list['code'] == 200:
                        print('list successfully')

                    url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/add'
                    data = {'clazzType': self.label}
                    data['clazzId'] = list['data']['rows'][crouse_idx]['tcList'][0].get('JXBID')
                    data['secretVal'] = list['data']['rows'][crouse_idx]['tcList'][0].get('secretVal')

                if crouse_idx != int(lesson[1]):
                    crouse_idx = int(lesson[1])
                    data['clazzId'] = list['data']['rows'][crouse_idx]['tcList'][0].get('JXBID')
                    data['secretVal'] = list['data']['rows'][crouse_idx]['tcList'][0].get('secretVal')

                if not (self.success_flag & 2**i):
                    # print(data['clazzId'])
                    # print(data['secretVal'])
                    # print(data)
                    response = self.session.post(url=url, data=data, headers=self.headers).json()
                    print(response)
                    assert response['code'] != 401
                    if response['code'] == 200:
                        self.success_flag = self.success_flag | 2**i
                        self.success_num += 1
                        print('Grab ' + data['clazzId'] +' successfully')

                count -= 1
                if count == 0:
                    count = 3
                    time.sleep(1)

            if self.success_num == len(self.lessonlist):
                break


        return

if __name__ == '__main__':
    count = 1
    loginname = int(input('一卡通号:'))
    password = input('密码:')
    # batchId = input('batchId:')
    flag = int(input('抢课/捡漏(1/0):'))
    type = int(input('列表类别:'))
    filename = input('待抢列表文件名:')
    begintime = 0
    if flag:
        begintime = input('开始时间(h:m:s:ms)[例:00:00:00:000]:')
        begintime = int("".join(begintime.split()[0].split(":")))
        # print(begintime)

    print('第1次尝试')
    while True:
        try:
            Grab = grab_lesson(loginname=loginname, password=password, flag=flag, begintime=begintime, filename=filename)
            Grab.run()
            if Grab.success_flag:
                break
        except:
            count += 1
            print('第%d次尝试'%count)


