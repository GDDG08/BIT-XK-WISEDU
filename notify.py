import requests 
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from userconfig import *


def notifyThrouthWeCom(id, msg):

    content = "ÇÀ¿Î£¡£¡£¡\n" + id + "\n" + msg
    print("Notify--->" + content)

    res = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwb22b1cf2cb811ffd&corpsecret=nE3Ainwo6VuQP1y1JDq6huvdue0H5X-vxs-GyZdJUOA")

    if res.status_code == 200:
        data = res.json()
        access_token = data['access_token']
        print("Notify-->", access_token)
        data = {"touser": "HuXuHao", "msgtype": "text",
                "agentid": 1000002, "text": {"content": content}, "safe": 0}

        requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token, json=data)

def notifyThrouthShell(id, msg):
    pass

def notifyThrouthEmail(id, msg):
    s = smtplib.SMTP()
    s.connect(host="smtp.163.com", port=25)
    mail_user = "hxh_create@163.com"
    mail_pass = "CKINJWZAMQOFSFZL"
    s.login(user=mail_user, password=mail_pass)
    content =  "!!!!!!!!!!!!!!!!!!!\n" + id + "\n" + msg
    print("Notify--->" + content)
    msg = MIMEText(content, _charset="utf-8")
    msg['Subject'] = Header('抢课通知', 'utf8')
    msg['From'] = 'hxh_create@163.com'
    msg['To'] = EMAIL_ADDRESS
    s.sendmail(from_addr=msg['From'], to_addrs=msg['To'],msg=msg.as_string())  
    print("Notify OK!")