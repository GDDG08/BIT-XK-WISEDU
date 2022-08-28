import time
import requests
import base64
import json
from urllib import parse
import threading


from .notify import notifyThrouthWeCom, notifyThrouthWin, notifyThrouthEmail
from .QRCode import collectQRcode



from .userconfig import * 




# 课程类型：TJKC 系统推荐课程 FANKC 方案内课程 XGXK 校公选课 TYKC 体育课程


stuCode = studentCode
stuPwd = stuPwd
electiveBatchCode = electiveBatchCode
recommendedList = recommendedList
publicList = publicList


"""settings"""
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70"
token = ""
cookie = ""
notifyWay = notifyWay
notifyWays = {
    "1": notifyThrouthWeCom,
    "2": notifyThrouthWin,
    '3': notifyThrouthEmail
}


readyToRub = []

class subRunThread(threading.Thread):
    
    def __init__(self, event_obj, name):
        threading.Thread.__init__(self, name=name)
        self.isChecking = False
        self.isToRub = False
        self.isSuccess = False
        self.event = event_obj
        
            
    def run(self):
        self.checkList()
        # err_cnt = 0
        # while True:
        #     if self.isChecking:
        #         err_cnt = 0
        #         self.checkList()
        #         time.sleep(1)
        #     else:
        #         if err_cnt < 10:
        #             if not self.isToRub:
        #                 login()
        #             err_cnt += 1
        #         else:
        #             print("连续10次登录错误, Bye")
        #             break


    
    def rubCourse(self, teachingClassId, teachingClassType):
        url = 'http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
        FormData = {
            "data": {
                "operationType": "1",
                "studentCode": stuCode,
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
            else:
                print("第" + str(i) + "次尝试：" + result["msg"])

        return False


    def checkList(self):
        for clr in recommendedList:
            if clr is not None:
                self.checkSingleCourseList("recommendedCourse", "TJKC", clr)

        for clp in publicList:
            if clp is not None:
                self.checkSingleCourseList("publicCourse", "XGXK", clp)

    def checkSingleCourseList(self, courseType, teachingClassType, id):
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
        data = "querySetting=%7B%22data%22%3A%7B%22studentCode%22%3A%22"+ stuCode+ "%22%2C%22campus%22%3A%222%22%2C%22electiveBatchCode%22%3A%22a02791301d6447c5a6a003fda48e9cba%22%2C%22isMajor%22%3A%221%22%2C%22teachingClassType%22%3A%22" + \
            teachingClassType + "%22%2C%22checkConflict%22%3A%222%22%2C%22checkCapacity%22%3A%222%22%2C%22queryContent%22%3A%22" + \
            id + "%22%7D%2C%22pageSize%22%3A%2210%22%2C%22pageNumber%22%3A%220%22%2C%22order%22%3A%22%22%7D"

       
        res = requests.post("http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/elective/" +
                            courseType + ".do",  data=data, headers=headers)

        if res.status_code == 401:
            print("登陆失效401")
            self.event.clear()
            self.event.wait() 
        elif res.status_code == 200:
            data = res.json()
            
            if data['code'] == "302":
                print("登陆失效302")
                self.event.clear()
                self.event.wait() 
            elif data['code'] == "1":
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
        notifyWays[str(notifyWay)](id, msg)
        result = self.rubCourse(teachingClassId, teachingClassType)
        if result:
            notifyWays[str(notifyWay)](id, "抢课成功!!!!!!!\nOHHHHHHHHHHHHHHHHHHHHHHHHH")
            # recommendedList.remove(teachingClassId)


def login():
    print("======Try to decode Code======")
    vtoken, code = collectQRcode()
    print("vtoken: " + vtoken + " code:" + code)

    print("======Try to Login======")

    params = {
        "timestrap": 1661576950457,
        "loginName": stuCode,
        "loginPwd": stuPwd,
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
        cookie = cookie  # get cookie
        print("Cookie---->", cookie)
        token = data['data']['token']  # get token
        print("Token---->", token)
        return True
    elif (data['code'] == '3'):
        print("验证码错误")
        return False
    return False

"""============================================================================="""


def comLogin():
    err_cnt = 0
    while(not login()):
        err_cnt += 1
        if err_cnt >= 10:
            print("连续10次登录失败, BYE====================")
            exit(1)



if __name__ == "__main__":
    event_obj = threading.Event()  # 创建一个事件
    event_obj.set()  # True
    comLogin()
    runThread1 = subRunThread(event_obj, name="subThread1")
    runThread2 = subRunThread(event_obj, name='subThread2')
    runThread1.start()
    runThread2.start()
    
    
    
    while(True):
        if not event_obj.is_set():  # 如果阻塞
            comLogin()
            print(threading.currentThread().name + ": " + "relogin")
            event_obj.set()  # 不阻塞
    