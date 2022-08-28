import time
import requests
import base64
import json
from urllib import parse

from notify import notifyThrouthWeCom, notifyThrouthShell, notifyThrouthEmail
from QRCode import collectQRcode

from userconfig import * 




# 课程类型：TJKC 系统推荐课程 FANKC 方案内课程 XGXK 校公选课 TYKC 体育课程

class XkApp:
    
    def __init__(self, notifyWay=3):
        self.stuCode = studentCode
        self.stuPwd = stuPwd
        self.electiveBatchCode = electiveBatchCode
        self.recommendedList = recommendedList
        self.publicList = publicList

       
        """settings"""
        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
        self.token = ""
        self.cookie = ""
        self.notifyWay = notifyWay
        self.notifyWays = {
            "1": notifyThrouthWeCom,
            "2": notifyThrouthShell,
            '3': notifyThrouthEmail
        }
        
        self.isChecking = False
        self.isToRub = False
        self.isSuccess = False
       
 
    
    
    def login(self):
        print("======Try to decode Code======")
        vtoken, code = collectQRcode()
        print("vtoken: " + vtoken + " code:" + code)

        print("======Try to Login======")

        params = {
            "timestrap": 1661576950457,
            "loginName": self.stuCode,
            "loginPwd": self.stuPwd,
            "verifyCode": code,
            "vtoken": vtoken
        }
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70",
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
            self.cookie = cookie  # get cookie
            print("Cookie---->", cookie)
            self.token = data['data']['token']  # get token
            print("Token---->", self.token)
            self.isChecking = True
        elif (data['code'] == '3'):
            print("验证码错误")

       
    def rubCourse(self, teachingClassId, teachingClassType):
        url = 'http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
        FormData = {
            "data": {
                "operationType": "1",
                "studentCode": self.stuCode,
                "electiveBatchCode": self.electiveBatchCode,
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
            'token': self.token,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cookie
        }

        for i in range(100):
            r = requests.post(url, data=addParam, headers=header)
            result = json.loads(r.text)
            if result["code"] == '1':
                print("第" + str(i) + "次尝试：" + result["msg"])
                return True
            else:
                print("第" + str(i) + "次尝试：" + result["msg"])

        return False
    
    
    def checkList(self):
        for clr in self.recommendedList:
            self.checkSingleCourseList("recommendedCourse", "TJKC", clr)

        for clp in self.publicList:
            self.checkSingleCourseList("publicCourse", "XGXK", clp)
    
    def checkSingleCourseList(self, courseType, teachingClassType, id):
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "language": "zh_cn",
            "pragma": "no-cache",
            "token": self.token,
            "Cookie": self.cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70",
            "x-requested-with": "XMLHttpRequest",
            "Origin": "http://xk.bit.edu.cn",
            "referrer": "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token=" + self.token
        }
        data = "querySetting=%7B%22data%22%3A%7B%22studentCode%22%3A%22"+ self.stuCode+ "%22%2C%22campus%22%3A%222%22%2C%22electiveBatchCode%22%3A%22a02791301d6447c5a6a003fda48e9cba%22%2C%22isMajor%22%3A%221%22%2C%22teachingClassType%22%3A%22" + \
            teachingClassType + "%22%2C%22checkConflict%22%3A%222%22%2C%22checkCapacity%22%3A%222%22%2C%22queryContent%22%3A%22" + \
            id + "%22%7D%2C%22pageSize%22%3A%2210%22%2C%22pageNumber%22%3A%220%22%2C%22order%22%3A%22%22%7D"

        # data = {
        #     "querySetting": {
        #         "data": {
        #             "studentCode": self.stuCode,
        #             "campus": "2",
        #             "electiveBatchCode": self.electiveBatchCode,
        #             "isMajor": "1",
        #             "teachingClassType": teachingClassType,
        #             "checkConflict": "2",
        #             "checkConflict": "2",
        #             "checkCapacity": "2",
        #             "queryContent": str(id)
        #         },
        #         "pageSize": "10",
        #         "pageNumber": "0",
        #         "order":""
        #     }
        # }
        res = requests.post("http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/" +
                            courseType + ".do",  data=data, headers=headers)

        if res.status_code == 401:
            print("登陆失效401")
            self.isChecking = False
        elif res.status_code == 200:
            data = res.json()
           
            if data['code'] == "302":
                print("登陆失效302")
                self.isChecking = False
            elif data['code'] == "1":
                print(data['totalCount'])
                if data['totalCount'] > 0:
                    course = data['dataList'][0]

                    if teachingClassType == "TJKC":
                        tcList = course['tcList']
                        tc = tcList[0]
                        isFull = tc['isFull']
                        teachingClassId = tc['teachingClassID']
                        numberOfSelected = tc['numberOfSelected']
                        numberOfCapacity = tc['classCapacity']

                        print("CHECKING-->" + id + ", isFull: " +
                            isFull + ", selected:" + numberOfSelected + "/" + numberOfCapacity)

                        if not isFull == '1':
                            msg = "课程:" + course['courseName'] + "\n当前人数:" + numberOfSelected + "\n课容量:" + numberOfCapacity
                            self.notifyAndRub(id, teachingClassId, teachingClassType, msg)

                    elif teachingClassType == "XGXK":
                        numberOfSelected = course['numberOfSelected']
                        isFull = course['isFull']
                        teachingClassId = course['teachingClassID']
                        print("CHECKING-->" + id + ", isFull: " +
                            isFull + ", selected:" + numberOfSelected)

                        if not isFull == '1':
                            msg = "课程:" + course['courseName'] +"\n当前人数:" + numberOfSelected
                            self.notifyAndRub(id, teachingClassId, teachingClassType, msg)

    def notifyAndRub(self, id, teachingClassId, teachingClassType, msg):
        self.isToRub = True
        self.notifyWays[str(self.notifyWay)](id, msg)
        result = self.rubCourse(teachingClassId, teachingClassType)
        if result:
            self.notifyWays[str(self.notifyWay)](id, "抢课成功!!!!!!!\nOHHHHHHHHHHHHHHHHHHHHHHHHH")
            # self.recommendedList.remove(teachingClassId)
    
    def run(self):
        err_cnt = 0
        while True:
            if self.isChecking:
                err_cnt = 0
                self.checkList()
                time.sleep(1)
            else:
                if err_cnt < 10:
                    if not self.isToRub:
                        self.login()
                    err_cnt += 1
                else:
                    print("连续10次登录错误, Bye")
                    break

