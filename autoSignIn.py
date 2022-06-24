import json
import requests
import time
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.header import Header


tz = pytz.timezone('Asia/Shanghai')#设置时区
SERVER = "on"
SCKEY = "SCT135282T3xQT7veStDDDfSdnliLnGt3W"
MAIL_NOTICE = 'on'
MAILBOX = 'lin2472612203@163.com'
mail_host = 'smtp.qq.com'
mail_sender = '2472612203@qq.com'
mail_pw = "trhirrozwjkddicg"

dkStart = datetime.now()
stu = ["4136010406","2116085400010","江西省","南昌市","红谷滩区","","115.826517","28.649543"]
status = {"1001":"打卡成功","1002":"今日已打卡！","1003":"打卡异常"}
#学生信息

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
#发送邮件
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
def login():

    if stu[0] != '学校代码':
        # 登录页面，提交学校代码和学号，用于获取cookie，直接get请求
        loginurl = f'https://fxgl.jx.edu.cn/{stu[0]}/public/homeQd?loginName={stu[1]}&loginType=0'
        print(loginurl)
        # 签到页面，需要使用cookie登录，post一系列参数实现签到
        signinurl = f'https://fxgl.jx.edu.cn/{stu[0]}/studentQd/saveStu'
        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'
        }
        # 使用session会话保持技术，可跨请求保留cookie
        session = requests.session()
        # 访问登陆界面，获取到用户的cookie，保持于session会话中
        session.get(loginurl, headers=headers)
        # 需要post的数据
        data = {
            'province': stu[2],  # 省份
            'city': stu[3],  # 市
            'district': stu[4],  # 区/县
            'street': stu[5],  # 具体地址
            'xszt': 0,
            'jkzk': 0,  # 健康状况 0:健康 1:异常
            'jkzkxq': '',  # 异常原因
            'sfgl': 1,  # 是否隔离 0:隔离 1:未隔离
            'gldd': '',
            'mqtw': 0,
            'mqtwxq': '',
            'zddlwz': stu[2] + stu[3] + stu[4],  # 省市区
            'sddlwz': '',
            'bprovince': stu[2],
            'bcity': stu[3],
            'bdistrict': stu[4],
            'bstreet': stu[5],
            'sprovince': stu[2],
            'scity': stu[3],
            'sdistrict': stu[4],
            'lng': stu[6],  # 经度
            'lat': stu[7],  # 纬度
            'sfby': 1  # 是否为毕业生 0:是 1:否
        }
        result = session.post(url=signinurl, data=data, headers=headers).text
        # 访问接口返回的数据是json字符串，使用loads方法转换为python字典
        statusCode = json.loads(result)['code']
        # 根据状态码判断签到状态
        print(status.get(str(statusCode)))
        sendMsg(status.get(str(statusCode)))
        sendMail(status.get(str(statusCode)))
        print(f"学号为{stu[1]}的同学" + status.get(str(statusCode)))


if __name__ == '__main__':
    login()
