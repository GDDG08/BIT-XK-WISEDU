import requests
import json
import time
import base64
import os

from .userconfig import *
   
def collectQRcode():
    queryQRcodeUrl = "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/student/4/vcode.do"
    header = {
        "Content-Type": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    r = requests.get(queryQRcodeUrl, params={"timestamp": int(
        round(time.time() * 1000))}, headers=header)
    vtoken = r.json().get('data').get('token')  # get user vtoken

    getQRcodeImgUrl = "http://xk.bit.edu.cn/xsxkapp/sys/xsxkapp/student/vcode/image.do"
    rr = requests.get(getQRcodeImgUrl, params={
                    'vtoken': vtoken}, headers=header)  
    root_path = "./qrcode/"
    if not os.path.exists(root_path):
        os.mkdir(root_path)
    with open("./qrcode/last_code.jpeg", 'wb') as file:
        file.write(rr.content)
        file.flush
    file.close()
    
    base64_data = base64.b64encode(rr.content)
    b64 = base64_data.decode()
    code = thirdPartyQrcodeDetect(b64)
    return vtoken, code


def thirdPartyQrcodeDetect(b64Image):
        data = {"username": TT_user, "password": TT_pwd,    # 第三方api 配置
                "typeid": "3", "image": b64Image}
        result = json.loads(requests.post(
            "http://api.ttshitu.com/predict", json=data).text)
        code = ""
        if result['success']:
            code = result["data"]["result"]
            thirdPartyQrcodeError(result['data']["id"])          
        else:
            print("TTSHITU Error"+result["message"])
            
       
        return code  # error return ''
        
def thirdPartyQrcodeError(reportid):
    reportresult = json.loads(requests.post("http://api.ttshitu.com/reporterror.json", 
                                                json={"id": reportid}).text)
    if reportresult['success']:
        return "report success"
    else:
        return reportresult['message'] 
