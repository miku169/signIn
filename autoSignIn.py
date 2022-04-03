#! usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time
import re
import urllib
import random
import pytz
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime


tz = pytz.timezone('Asia/Shanghai')
# 系统变量
card_id = os.environ['card_id']
sfzMd5 = os.environ['sfzMd5']
school_no = os.environ['school_no']  # 学校代码
SERVER = "on"
SCKEY = "SCT135282T3xQT7veStDDDfSdnliLnGt3W"
MAIL_NOTICE = 'on'
MAILBOX = 'lin2472612203@163.com'
mail_host = 'smtp.qq.com'
mail_sender = '2472612203@qq.com'
mail_pw = "trhirrozwjkddicg"

dkStart = datetime.now()
def ali_pay_login():
    url = f"https://fxgl.jx.edu.cn/{school_no}/third/alipayLogin?cardId={card_id}&sfzMd5={sfzMd5}"
    accept_encoding = "gzip, deflate, br"
    accept_language = "zh-CN,en-US;q=0.8"
    connection = "keep-alive"
    host = "fxgl.jx.edu.cn"
    login = requests.get(url, headers={
        # 'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
        'Connection': connection,
        # 'Cookie': cookie,
        'Host': host,
        # 'User-Agent': user_agent,
        # 'sign': sign,
        # 'ts': ts
    })
    return login.history[0]  # 此处重定向到新的地址


def get_cookies(value: "ali_pay_login返回的对象"):
    cookie_str = value.headers["Set-Cookie"]
    cookies = {}
    jseSion = (re.search('JSESSIONID=(.+?);', cookie_str)).group(0).replace(';', '')
    loginName = (re.search('loginName=(.+?);', cookie_str)).group(0).replace(';', '')
    loginType = (re.search('loginType=(.+?);', cookie_str)).group(0).replace(';', '')
    yzxx = (re.search('yzxx=(.+?);', cookie_str)).group(0).replace(';', '')
    for e in [jseSion, loginName, loginType, yzxx]:
        # print(e)
        name, val = e.split('=', 1)
        cookies[name] = val
    return cookies


def checkin(my_cookies):
    url = f"https://fxgl.jx.edu.cn/{school_no}/studentQd/saveStu"
    accept = '*/*'
    accept_encoding = 'gzip, deflate, br'
    accept_language = 'zh-CN,en-US;q=0.8'
    connection = 'keep-alive'
    content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
    host = 'fxgl.jx.edu.cn'
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                 'Mobile/18E199 Ariver/1.1.0 AliApp(AP/10.2.33.6200) Nebula WK RVKType(1) AlipayDefined(nt:4G,' \
                 'ws:390|780|3.0) AlipayClient/10.2.33.6200 Language/zh-Hans Region/CN MiniProgram APXWebView ' \
                 'NebulaX/1.0.0X-Requested-With: XMLHttpRequest '
    data = {'province': '江西省',
            'city': '南昌市',
            'district': '红谷滩区',
            'street': '丰和南大道696号南昌航空大学',
            'xszt': 0,
            'jkzk': 0,
            'jkzkxq': '',
            'sfgl': 1,
            'gldd': '',
            'mqtw': 0,
            'mqtwxq': '',
            'zddlwz': '江西省南昌市红谷滩区丰和南大道696号南昌航空大学',
            'sddlwz': '',
            'bprovince': '江西省',
            'bcity': '南昌市',
            'bdistrict': '红谷滩区',
            'bstreet': '丰和南大道696号南昌航空大学',
            'sprovince': '江西省',
            'scity': '南昌市',
            'sdistrict': '红谷滩区',
            'lng': '115.826517',
            'lat': '28.649543',
            'sfby': 1

            }
    data = urllib.parse.urlencode(data)
    res = requests.post(url, headers={
        'Accept': accept,
        'Accept-Encoding': accept_encoding,
        'Accept-Language': accept_language,
        'Connection': connection,
        'Content-Type': content_type,
        'Host': host,
        'User-Agent': user_agent
    }, cookies=my_cookies, data=data)
    # print(res.text)
    return res.text



def create_log(text):
    msg = (re.search(r'("msg":.*?),', text)).group(1)
    tm = datetime.now(tz).strftime('%Y-%m-%d-%H:%M:%S')
    l = tm + ',' + msg
    return l


# 自动打卡
def autoSignIn():
    global dkStart
    try:
        time.sleep(int(random.random()*1000%60))
        location = ali_pay_login()
        myCookies = get_cookies(location)
        t = checkin(myCookies)
        log = create_log(t)
        sendMsg(log)
        sendMail()

    except Exception as e:
        print('打卡失败！\n{}'.format(str(e)))
        sendMsg("打卡失败！", str(e))
        sendMail("打卡失败！", str(e))


# 发送微信推送消息
def sendMsg(m, error=''):
    if SERVER == 'on':
        timeNow = time.strftime('%Y-%m-%d', time.localtime())
        duration = datetime.now() - dkStart
        if error == '':
            msg = '{}本次打卡耗时{}秒。'.format(m, duration.seconds)
        else:
            msg = '{} {}!'.format(timeNow, error)
        url = 'https://sc.ftqq.com/{}.send?text={}&desp={}'.format(SCKEY, msg, '{}\n{}'.format(msg, error))
        requests.get(url)

def sendMail(text="健康打卡成功", error=''):
    print('发送邮件...')
    if MAIL_NOTICE == 'on':
        timeNow = datetime.now(tz).strftime('%Y-%m-%d-%H:%M:%S')
        duration = datetime.now() - dkStart
        content = "{}\n{}\n本次耗时{}秒！".format(timeNow, text, duration)
        msg = MIMEText(content, 'plain', 'utf-8')
        msg["From"] = Header(mail_sender, 'utf-8')
        msg["To"] = Header(MAILBOX, 'utf-8')
        subject = "{0}-{1}".format(time.strftime("%Y%m%d", time.localtime()), text)
        msg["Subject"] = Header(subject, 'utf-8')
        try:
            server = smtplib.SMTP()
            server.connect(mail_host, 25)
            server.login(mail_sender, mail_pw)
            server.sendmail(mail_sender, MAILBOX, msg.as_string())
            server.quit()
            print("邮件发送成功！")
        except Exception as e:
            print("邮件发送失败！\n{}".format(e))
if __name__ == '__main__':
    autoSignIn()
