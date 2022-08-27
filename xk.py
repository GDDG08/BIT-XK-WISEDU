import re
import time
from urllib import request
import requests
import base64
import json
from urllib import parse

studentCode = xxxxxxxxxx
stuPwd = ""

electiveBatchCode = ""
recommendedList = [""]
publicList = [""]

# TTSHITU
TT_user = ""
TT_pwd = ""

# WECOM
WC_id = ""
WC_secret = ""

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
cookie = ""
token = ""

isChecking = False


def collectQRcode():
    queryQRcodeUrl = "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/student/4/vcode.do"
    header = {
        "Content-Type": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": userAgent,
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    r = requests.get(queryQRcodeUrl, params={"timestamp": int(
        round(time.time() * 1000))}, headers=header)
    vtoken = r.json().get('data').get('token')
    getQRcodeImgUrl = "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/student/vcode/image.do"
    rr = requests.get(getQRcodeImgUrl, params={
                      'vtoken': vtoken}, headers=header)

    # with open("./last_code.jpeg", 'wb') as file:
    #     file.write(rr.content)
    #     file.flush
    # file.close()

    base64_data = base64.b64encode(rr.content)
    b64 = base64_data.decode()
    data = {"username": TT_user, "password": TT_pwd,
            "typeid": "3", "image": b64}
    result = json.loads(requests.post(
        "http://api.ttshitu.com/predict", json=data).text)

    code = ""
    if result['success']:
        code = result["data"]["result"]
    else:
        print("TTSHITU Error"+result["message"])
    return vtoken, code


def login():
    global cookie, token, isChecking
    print("======Try to decode Code======")
    vtoken, code = collectQRcode()
    print(vtoken, code)

    print("======Try to Login======")

    params = {
        "timestrap": int(round(time.time() * 1000)),
        "loginName": studentCode,
        "loginPwd": stuPwd,
        "verifyCode": code,
        "vtoken": vtoken
    }
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "User-Agent": userAgent,
        "x-requested-with": "XMLHttpRequest",
        "referrer": "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do"
    }
    lr = requests.get("http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/student/check/login.do",
                      params=params, headers=headers)
    print(lr)
    data = lr.json()
    print(lr.text)
    if (data['code'] == '1'):
        print("登录成功")
        cookie = lr.headers['Set-Cookie']
        print("Cookie---->", cookie)
        token = data['data']['token']
        print("Token---->", token)
        isChecking = True
    elif (data['code'] == '3'):
        print("验证码错误")


def checkList():
    for clr in recommendedList:
        check("recommendedCourse", "TJKC", clr)

    for clp in publicList:
        check("publicCourse", "XGXK", clp)


def check(courseType, teachingClassType, id):

    global token, cookie, isChecking
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "language": "zh_cn",
        "pragma": "no-cache",
        "token": token,
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70",
        "x-requested-with": "XMLHttpRequest",
        "Origin": "http://xk.bit.edu.cn",
        "referrer": "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token=" + token
    }
    query = {
        "data": {
            "studentCode": studentCode,
            "campus": "2",
            "electiveBatchCode": electiveBatchCode,
            "isMajor": "1",
            "teachingClassType": teachingClassType,
            "checkConflict": "2",
            "checkCapacity": "2",
            "queryContent": id
        },
        "pageSize": "10",
        "pageNumber": "0",
        "order": ""
    }

    data = "querySetting="+parse.quote(str(query))

    res = requests.post("http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/" +
                        courseType + ".do",  data=data, headers=headers)

    print(res)
    if res.status_code == 401:
        print("登陆失效401")
        isChecking = False
    elif res.status_code == 200:
        data = res.json()
        # print("CHECKING-->"+id+", list_len: " + str(data['totalCount']))
        if data['code'] == "302":
            print("登陆失效302")
            isChecking = False
        elif data['code'] == "1":
            if data['totalCount'] > 0:
                course = data['dataList'][0]

                if teachingClassType == "TJKC":
                    tcList = course['tcList']
                    tc = tcList[0]
                    isFull = tc['isFull']
                    teachingClassId = tc['teachingClassID']
                    numberOfSelected = tc['numberOfSelected']

                    print("CHECKING-->" + id + ", isFull: " +
                          isFull + ", selected:" + numberOfSelected)

                    if not isFull == '1':
                        notifyAndRub(id, teachingClassId, teachingClassType, "课程:" + course['courseName'] +
                                     "\n当前人数:" + numberOfSelected)

                elif teachingClassType == "XGXK":
                    numberOfSelected = course['numberOfSelected']
                    isFull = course['isFull']
                    teachingClassId = course['teachingClassID']
                    print("CHECKING-->" + id + ", isFull: " +
                          isFull + ", selected:" + numberOfSelected)

                    if not isFull == '1':
                        notifyAndRub(id, teachingClassId, teachingClassType, "课程:" + course['courseName'] +
                                     "\n当前人数:" + numberOfSelected)


isToRub = False

rubbedList = []


def notifyAndRub(id, teachingClassId, teachingClassType, msg):
    global isToRub, rubbedList

    if id in rubbedList:
        return

    isToRub = True
    notify(id, msg)
    result = rubCourse(teachingClassId, teachingClassType)
    if result:
        rubbedList.append(id)
        notify(id, "抢课成功!!!!!!!\nOHHHHHHHHHHHHHHHHHHHHHHHHH")


def notify(id, msg):

    content = "抢课！！！\n" + id + "\n" + msg
    print("Notify--->" + content)

    res = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+WC_id+"&corpsecret="+WC_secret)

    if res.status_code == 200:
        data = res.json()
        access_token = data['access_token']
        print("Notify-->", access_token)
        data = {"touser": "@all", "msgtype": "text",
                "agentid": 1000002, "text": {"content": content}, "safe": 0}

        requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token, json=data)


def rubCourse(teachingClassId, teachingClassType):
    url = 'http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'

    FormData = {
        "data": {
            "operationType": "1",
            "studentCode": studentCode,
            "electiveBatchCode": electiveBatchCode,
            "teachingClassId": teachingClassId,
            "isMajor": "1",
            "campus": "2",
            "teachingClassType": teachingClassType,
            "chooseVolunteer": "1"
        }
    }
    strFormData = str(FormData)
    addParam = "addParam="+parse.quote(strFormData)

    header = {
        'token': token,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookie
    }

    for i in range(100):
        r = requests.post(url, data=addParam, headers=header)
        result = json.loads(r.text)
        if result["code"] == '1':
            print("第" + str(i) + "次尝试：" + result["msg"])
            return True
            break
        else:
            print("第" + str(i) + "次尝试：" + result["msg"])

    return False


if __name__ == '__main__':

    err_cnt = 0
    while True:

        if isChecking:
            err_cnt = 0
            checkList()
            time.sleep(1)
        else:
            if err_cnt < 10:
                if not isToRub:
                    login()
                err_cnt += 1
            else:
                print("连续10次登录错误, Bye")
                break
