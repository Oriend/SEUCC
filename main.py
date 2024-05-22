import requests
import re
import requests.utils
import time
import json
import base64

PIN = 6
def acq_PIN():
    url='http://newxk.urp.seu.edu.cn/xsxk/auth/captcha'
    headers={
        'Referer': 'http://newxk.urp.seu.edu.cn/xsxk/profile/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    reponse=requests.post(url=url,headers=headers).text
    # url2=re.findall('"captcha": "(.*)",',reponse)[0]
    uuid=re.findall('"uuid": "(.*)"',reponse)[0]
    # a=url2.split(',')[1]
    # #print(len(a))
    # imagedata = base64.b64decode(a)
    # #print(imagedata)
    # file = open('1.jpg',"wb")
    # file.write(imagedata)
    # file.close()

    return uuid

def renew_Authorization(response):
    auth = response['data']['token']
    # print(auth)
    # authorization = str(auth[0])
    headers['Authorization'] = auth

# cookie_dict = {
#     'zg_did': '%7B%22did%22%3A%20%22184fa5b8f59c27-0dfc835bee1232-3e604809-144000-184fa5b8f5aad1%22%7D',
#     'zg_8da79c30992d48dfaf63d538e31b0b27': '%7B%22sid%22%3A%201682172990804%2C%22updated%22%3A%201682173122557%2C%22info%22%3A%201682172990807%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%2C%22firstScreen%22%3A%201682172990804%7D',
#     'route': '1994b5e3809a70afaecbdc49f228a574'
# }

session = requests.session()
# session.cookies = requests.utils.cookiejar_from_dict(cookie_dict)

headers = {
    'Authorization': None,
    'Host': 'newxk.urp.seu.edu.cn',
    'Origin': 'http://newxk.urp.seu.edu.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://newxk.urp.seu.edu.cn/xsxk/profile/index.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}

url = 'http://newxk.urp.seu.edu.cn/xsxk/auth/login'

responce = session.get(url=url).text



loginname = int(input('一卡通号:'))
password = input('加密后密码:')
# batchId = input('batchId:')
flag = int(input('抢课/简陋(1/0):'))
if flag:
    begintime = input('开始时间(h:m:s:ms):')
    begintime = int("".join(begintime.split()[0].split(":")))
    # print(begintime)


while True:
    uuid = acq_PIN()

    data = {'captcha': PIN, 'uuid': uuid}    # 'loginname': 213212319, 'password': 'HTaXLVcN7BAoYEh6I3xCkw==',

    data['loginname'] = loginname
    data['password'] = password
    response = session.post(url=url, data=data, headers=headers).json()
    if response['code'] == 200:
        # print(type(response['data']))
        print('login stage 1 successfully')
        break
    # print(response)

renew_Authorization(response)

url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/seu/user'

data = {} # 'batchId': 'bea0c6ddb83441da908b34d223cf1d93'
data['batchId'] = response['data']['student']['electiveBatchList'][1]['code']
# data = '1'
while True:
    response = session.post(url=url, data=data, headers=headers).json()
# print(response)
    if response['code'] == 200:
        print('login stage 2 successfully')
        break

url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/grablessons?'+'batchId='+data['batchId']+'&'+'token='+headers['Authorization']
refer = url
headers['Upgrade-Insecure-Requests'] = '1'
data['token'] = headers['Authorization']

session.get(url=url, data=data, headers=headers)

# 获取课程
headers['batchId'] = data['batchId']
headers['Referer'] = refer
# print(refer)
if flag:
    while True:
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s:%03d" % (data_head, data_secs)
        stamp = int("".join(time_stamp.split()[0].split(":")))

        if stamp == begintime:
            break



url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/list'
data = {"teachingClassType": "TJKC", "pageNumber": 2, "pageSize": 10, "orderBy": "", "campus": "1"}
list = session.post(url=url, json=data, headers=headers).json()
if list['code'] == 200:
    print('list successfully')

# 选课

url = 'http://newxk.urp.seu.edu.cn/xsxk/elective/clazz/add'
# print(session.cookies)

data = {
    'clazzType':'TJKC',
    'clazzId':'202320243B060450001',
    'secretVal':None
}

data['secretVal'] = list['data']['rows'][7]['tcList'][0].get('secretVal')
    # print(data['secretVal'])
while True:
    response = session.post(url=url, data=data, headers=headers).json()
    print(response)
    if response['code'] == 200:
        break
    time.sleep(1)



