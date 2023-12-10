import requests
import time
from threading import Thread
import traceback
import json
from datetime import datetime
from collections import defaultdict
from tongyi import *
#####gpt配置
host = 'https://chat.extkj.cn/api/chat-stream'
first_id = "chatcmpl-7FunqjtgiPrQhBR5hnOoOlqDsdxZr"
#####

sendmslist=[]
sendlist = {}
####
login_cookie = '__client_id=e17cf************************748175850ca; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2F; _uid=1154310'
login_uid=1154310
csrf_token = '自动分配'
#ad = '【欢迎加入 BPOJ (bpoj.top;154.12.55.87),开发组招人中~ 欢迎合作~】'
ad='暂时没有'
help = '''目前有三个功能：
1.普通回答，使用通义万象模型 使用方式：问答即可
2.使用GPT，使用方式：#GPT [问题](一天上限3次) 2023/12/7：没啦
3.传话系统，使用方式：#传话 [对方UID] [问题]
查看更新请输入“#更新”
查看关于请输入“#关于”
'''
gengxin = '''1.增加更新
2.qyk转为通义万象
3.赞助一个API QwQ
'''
about = '''原作者：董乐山2020
原作者死因：BOT账号被封禁
现任开发者：_YuTian_
不说别的，不要乱发！！！
以后想做一个生成图片的，同意的给_YuTian_发私信！！
'''
####

send_ban = []
is_ans = []  # 防止重复回答

# 创建一个默认字典，指定默认值为0
gptuser = defaultdict(int)

####

def cut(obj, sec):  # https://blog.csdn.net/qq_26373925/article/details/101135611
	return [obj[i:i + sec] for i in range(0, len(obj), sec)]

def clear_gptuser_at_midnight():
	while True:
		now = datetime.now()
		# 获取当前时间的小时和分钟
		current_hour = now.hour
		current_minute = now.minute
		# 如果是凌晨0点，清空gptuser列表
		if current_hour == 0 and current_minute == 0:
			gptuser.clear()
		# 等待一段时间，避免频繁检查
		time.sleep(60)  # 每分钟检查一次

def ban(uid):
	
	send_ban.append(uid)
	with open('ban.txt', 'a') as f:
		f.write(str(uid) + '\n')


def gpt35(ques,uid):
#	if int(gptuser[str(uid)]) > 3:
#		return "每个用户一天只能询问3次哦"
#	gptuser[str(uid)] += 1;
	api_key = "sk-CVkG***************************************CyeWEteAVv"

	url = "https://api.openai-proxy.com/v1/chat/completions"

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}
	# 设置请求体
	data = {
		"model": "gpt-3.5-turbo",
		"messages": [{"role": "user", "content": ques}]
	}

	# 发送POST请求
	response = requests.post(url, json=data, headers=headers)

	# 检查响应
	if response.status_code == 200:
		#print("成功：")
		#print(response.json())
		ans=response.json()
		return "model:"+ans['model']+"|usage_token:"+str(ans['usage']['total_tokens'])+'\n'+ans['choices'][0]['message']['content']
	else:
		print(f"请求失败，状态码：{response.status_code}")
		print(response.text)

		return "请求失败，状态码："+response.text

def qyk(s):
	##所有需要回答的问题都会经过这里
	##TODO:分流 
	# print('问题：',s)
	ans = requests.get('http://api.qingyunke.com/api.php?key=free&appid=0&msg=' + s)
	sendans = '如有问题可询问"help"\n模型:qyk\n回答:' + ans.json()['content']
	return sendans


def sendms(ruid, msg):  # msgs是列表
	msgs=cut('疑问请输入“help”获取帮助\n__RainDay__：\n'+msg, 250);
	if len(msgs) > 1:
		sendm(ruid, '发送的信息过长，已开启分段发送')
	for i in reversed(msgs):
		time.sleep(1)
		sendm(ruid, i)
def sendm(ruid, msg):
	sendmslist.append((ruid,msg))
def sendm2():
	print("sendm2线程，启动！")
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
	while True:
		if sendmslist==[]:
			continue
		ruid=sendmslist[-1][0]
		msg=sendmslist[-1][1]
		del sendmslist[-1]
		res_send = requests.post("https://www.luogu.com.cn/api/chat/new", headers=headers2, json={"user": ruid, "content": msg})
		if res_send.text != '{"_empty":true}':
			#ban(ruid)
			pass
		print('发送信息：', res_send.text)
		time.sleep(3)

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

def ToPaste(content):
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
	return1 = requests.post("https://www.luogu.com.cn/paste/new", headers=headers2, json={"public":'true',"data":content})
	retrun_data = return1.json()
	return "消息过长转换为链接https://www.luogu.com.cn/paste/" + retrun_data["id"]

def answermsg(uid, content):  # 这个模块主要用于多线程，回答后给sendms。
	##TODO:让用户选择ta想要的模型（bot）
	#sendms(uid, qyk(content))
	try:
		if content[:3] == "#传话":#传话
			sendms(uid,'消息发送成功，对方确认后可查看你的消息。')
			sendms(int(content.split(' ')[1]),'你有一条匿名信息，回复“#OK”即可查看，如有任何违反社区规则的信息本bot和其作者不承担相关责任')
			# sendm(int(content.split(' ')[1]), content.split(' ')[2])
			sendlist[int(content.split(' ')[1])] = content.split(' ')[2]
		elif content[:3] == "#OK":
			try:
				sendms(uid, "这是此bot代发送的匿名消息，本bot和其作者不承担相关责任\n" + sendlist[uid])
			except:
				sendms(uid, "出现错误，有可能你没有消息……")
		elif content[:4] == "#GPT":
			sendms(uid, "GPT没啦！如果你有API赞助一个呗（通义千问也挺好的啊QAQ）")
		elif content == "help" or content == "Help":
			sendms(uid, help)
		elif content[:3] == "#更新":
			sendms(uid, gengxin)
		elif content[:3] == "#关于":
			sendms(uid, about)
		else:
			content_tonyi = tongyi("你是一个聊天机器人，回答问题："+content)
			if len(content_tonyi) > 250:
				content_tonyi = ToPaste(content_tonyi)
			sendms(uid, content_tonyi)
	except:
		print("Error")
#sendms(uid, gpt35("字数限制在250字以内，问题："+content.split(' ')[1],uid))
def auto_replace_csrf_token():
	print("auto_replace_csrf_token，启动！")
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
Thread(target=clear_gptuser_at_midnight).start()
time.sleep(2)#等待csrftoken更换
Thread(target=sendm2).start()
time.sleep(2)
sendm(655082, '开机')

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
			for key, value in gptuser.items():
				print(f"用户: {key}, 次数: {value}",end = ",")
			print("")
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
