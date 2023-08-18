import requests
import time
from threading import Thread
import traceback
import json

#####gpt配置
host = 'https://chat.extkj.cn/api/chat-stream'
first_id = "chatcmpl-7FunqjtgiPrQhBR5hnOoOlqDsdxZr"
#####


####
login_cookie = '__client_id=cb4d60f****************************5; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2F; _uid=988888'
login_uid=988888
csrf_token = '自动分配'
#ad = '【欢迎加入 BPOJ (bpoj.top;154.12.55.87),开发组招人中~ 欢迎合作~】'
ad=''

####

send_ban = []
is_ans = []  # 防止重复回答


####

def cut(obj, sec):  # https://blog.csdn.net/qq_26373925/article/details/101135611
    return [obj[i:i + sec] for i in range(0, len(obj), sec)]



def ban(uid):
    
    send_ban.append(uid)
    with open('ban.txt', 'a') as f:
        f.write(str(uid) + '\n')


def answer(s):
    ##所有需要回答的问题都会经过这里
    ##TODO:分流 
    # print('问题：',s)
    ans = requests.get('http://api.qingyunke.com/api.php?key=free&appid=0&msg=' + s)
    sendans = ad + '\n----------\n问题:' + s + '\n----------\n模型:qyk\n----------\n回答:' + ans.json()[
        'content'] +'\n----------\n' + ad
    return cut(sendans, 250)


def sendms(ruid, msgs):  # msgs是列表
    if len(msgs) > 1:
        sendm(ruid, '发送的信息过长，已开启分段发送')
    for i in msgs:
        time.sleep(1)
        sendm(ruid, i)


def sendm(ruid, msg):
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        '_contentOnly': 'WoXiHuanFanQianXing',
        'x-luogu-type': 'content-only',
        'cookie': login_cookie,
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.luogu.com.cn/',
        'x-csrf-token': csrf_token,
        "content-type": "application/json",
    }
    res_send = requests.post("https://www.luogu.com.cn/api/chat/new", headers=headers2,
                             json={"user": ruid, "content": msg})
    if res_send.text != '{"_empty":true}':
        #ban(ruid)
        pass
    print('发送信息：', res_send.text)
    time.sleep(5)

def getcsrf():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
        '_contentOnly': 'WoXiHuanFanQianXing',
        'x-luogu-type': 'content-only',
        'cookie': login_cookie,
        'x-requested-with': 'XMLHttpRequest',
    }
    res2 = requests.get("https://www.luogu.com.cn/", headers=headers)
    # <meta name="csrf-token" content="1682209913:+IHBdXuEXdGyGjCgJFRKo/Ul3Yu3+AJhXC1qU8+CrC4=">
    res2 = res2.text
    csrftoken = res2.split("<meta name=\"csrf-token\" content=\"")[-1].split("\">")[0]
    print("csrftoken:", csrftoken)
    return csrftoken


def answermsg(uid, content):  # 这个模块主要用于多线程，回答后给sendms。
    sendms(uid, answer(content))


def auto_replace_csrf_token():
    global csrf_token
    while True:
        csrf_token = getcsrf()
        print("csrftoken更换成功!", csrf_token)
        time.sleep(3600)


##################

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    '_contentOnly': 'WoXiHuanFanQianXing',
    'x-luogu-type': 'content-only',
    'cookie': login_cookie,
    'x-requested-with': 'XMLHttpRequest',
}
Thread(target=auto_replace_csrf_token).start()
time.sleep(2)
sendm(379916, '开机')
with open('ban.txt', 'r') as f:
    tmp = f.read()
    tmp = tmp.split()
    print('banlist', tmp)
    for i in tmp:
        send_ban.append(int(i))
while True:
    try:
        while True:

            time.sleep(5)
            res = requests.get('https://www.luogu.com.cn/chat', headers=headers)
            resjson = res.json()
            print(resjson['code'])
            for i in resjson['currentData']['latestMessages']['result']:
                # print(i['id'],i['time'],i['sender']['uid'],"->",i['receiver']['uid'],i['content'])
                if ((i['receiver']['uid'] == login_uid) and (not (i['sender']['uid'] in send_ban)) and (
                not i['id'] in is_ans)):
                    is_ans.append(i['id'])
                    Thread(target=answermsg, args=(i['sender']['uid'], i['content'])).start()

                    time.sleep(1)  

                    # sendms(i['sender']['uid'],answer(i['content']))
                    # is_answer_id.append(i['id'])
    except Exception as e:
        traceback.print_exc()

