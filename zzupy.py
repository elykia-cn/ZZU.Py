import random
import httpx
import json
import base64
import datetime
import hashlib
import time
from rich import print


def info(text):
    print(f"[bold green][INFO]:[/bold green] {text}")


def error(text):
    print(f"[bold red][ERROR]:[/bold red] {text}")
    quit()


def warn(text):
    print(f"[bold yellow][WARN]:[/bold yellow] {text}")


def getSign(dynamicSecret, params):
    """
    获取sign值
    :param str dynamicSecret: login后自动获取，来自 login-token 请求
    :param str params: URL请求参数
    :return: sign值
    :return_type: str
    """
    paramsDict = {}
    for param in params.split("&"):
        if param.split("=")[0] == "timestamp":
            timestamp = param.split("=")[1]
        elif param.split("=")[0] == "random":
            random = param.split("=")[1]
        else:
            paramsDict[param.split("=")[0]] = param.split("=")[1]
    paramsDict = dict(sorted(paramsDict.items()))
    original = f"{dynamicSecret}|"
    for key in paramsDict:
        original += f"{paramsDict[key]}|"
    original += f"{timestamp}|{random}"
    sign = hashlib.md5(original.encode("utf-8")).hexdigest().upper()
    return sign


class ZZUPy:
    def __init__(self, forceDeviceParams=False):
        """
        初始化
        :param bool forceDeviceParams: 是否忽略设备参数的设置。设为 True 将不再触发 "Recommended set device parameters" 的警告
        """
        self.forceDeviceParams = forceDeviceParams
        self.userToken = None
        self.dynamicSecret = "supwisdom_eams_app_secret"
        self.dynamicToken = None
        self.refreshToken = None
        self.name = None
        self.userAgentPrecursor = None
        self.isLogged = False
        self.DeviceParamsSet = False
        self.deviceName = ""
        self.deviceId = ""
        self.deviceInfo = ""
        self.deviceInfos = ""
        self.userAgentPrecursor = ""
        self.userCode = ""

    def setParamsFromPasswordLogin(self, res):
        try:
            self.userToken = json.loads(res)["data"]["idToken"]
            # 我也不知道 refreshToken 有什么用，但先存着吧
            self.refreshToken = json.loads(res)["data"]["refreshToken"]
        except:
            error("LoginFailed")

    def setParamsFromLoginToken(self, res):
        try:
            self.dynamicSecret = json.loads(base64.b64decode(json.loads(res)["business_data"]))["secret"]
            self.dynamicToken = json.loads(base64.b64decode(json.loads(res)["business_data"]))["token"]
            self.name = json.loads(base64.b64decode(json.loads(res)["business_data"]))["user_info"]["user_name"]
        except:
            error("LoginFailed")

    def setDeviceParams(self, deviceName="", deviceId="", deviceInfo="", deviceInfos="", userAgentPrecursor=""):
        """
        设置设备参数.
        :param str deviceName: 设备名 ，需要抓包获取,位于 "passwordLogin" 请求的 User-Agent 中，组成为 '{appVersion}({deviceName})' ，但也可随便填或空着，目前没有观察到相关风控机制。
        :param str deviceId: 设备 ID ，需要抓包获取，但也可随便填或空着，目前没有观察到相关风控机制
        :param str deviceInfo: 设备信息，需要抓包获取，位于名为 "X-Device-Info" 的请求头中。但也可随便填或空着，目前没有观察到相关风控机制
        :param str deviceInfos: 设备信息，需要抓包获取，位于名为 "X-Device-Infos" 的请求头中。但也可随便填或空着，目前没有观察到相关风控机制
        :param str userAgentPrecursor: 设备 UA 前体 ，需要抓包获取，但也可随便填或空着，目前没有观察到相关风控机制。只需要包含 "SuperApp" 或 "uni-app Html5Plus/1.0 (Immersed/38.666668)" 前面的部分
        """
        self.deviceName = deviceName
        self.deviceId = deviceId
        self.deviceInfo = deviceInfo
        self.deviceInfos = deviceInfos
        if userAgentPrecursor.endswith(" "):
            self.userAgentPrecursor = userAgentPrecursor
        else:
            self.userAgentPrecursor = userAgentPrecursor + " "
        self.DeviceParamsSet = True

    def loginByPassword(self, userCode, password, appVersion="SWSuperApp/1.0.33",
                        appId="com.supwisdom.zzu", osType="android"):
        """
        通过学号和密码登录
        :param str userCode: 学号
        :param str password: 密码
        :param str appVersion: APP 版本 ，一般类似 "SWSuperApp/1.0.33" ，可自行更新版本号，但详细数据需要抓包获取,位于 "passwordLogin" 请求的 User-Agent 中，也可随便填或空着，目前没有观察到相关风控机制。
        :param str appId: APP 包名，一般不需要修改
        :param str osType: 系统类型，一般不需要修改
        :return: [self.usercode,self.name] 即由学号和姓名组成的列表
        :rtype: list
        """
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        headers = {
            'User-Agent': f'{appVersion}({self.deviceName})',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        response = httpx.post(
            f'https://token.s.zzu.edu.cn/password/passwordLogin?username={userCode}&password={password}&appId={appId}&geo&deviceId={self.deviceId}&osType={osType}&clientId&mfaState',
            headers=headers,
        )
        self.setParamsFromPasswordLogin(response.text)

        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
            'SVRNAME': 'ws1',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + "SuperApp",
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Origin': 'https://jw.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://jw.v.zzu.edu.cn/app-web/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/; SVRNAME=ws1',
        }
        data = {
            'random': int(random.uniform(10000, 99999)),
            'timestamp': int(round(time.time() * 1000)),
            'userToken': self.userToken
        }
        # 计算 sign 并将其加入 data
        params = ""
        for key in data.keys():
            params += f"{key}={data[key]}&"
        params = params[:-1]
        sign = getSign(self.dynamicSecret, params)
        data["sign"] = sign

        response = httpx.post(
            'https://jw.v.zzu.edu.cn/app-ws/ws/app-service/super/app/login-token',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        self.setParamsFromLoginToken(response.text)
        self.userCode = userCode
        self.isLogged = True
        return [self.userCode, self.name]

    def getCoursesJson(self, start_date):
        """
        获取课程表
        :param str start_date: 课表的开始日期，必需为本周周一，否则课表会时间错乱
        :return: 返回课程表数据，格式为json
        :return_type: str
        """
        if not self.isLogged:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
            'SVRNAME': 'ws1',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + "SuperApp",
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            'sec-ch-ua-mobile': '?1',
            'token': self.dynamicToken,
            'sec-ch-ua-platform': '"Android"',
            'Origin': 'https://jw.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://jw.v.zzu.edu.cn/app-web/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/; SVRNAME=ws1',
        }

        data = {
            'biz_type_id': '1',
            'end_date': (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=6)).strftime(
                "%Y-%m-%d"),
            'random': int(random.uniform(10000, 99999)),
            'semester_id': '152',
            'start_date': start_date,
            'timestamp': int(round(time.time() * 1000)),
            'token': self.userToken,
        }
        params = ""
        for key in data.keys():
            params += f"{key}={data[key]}&"
        params = params[:-1]
        sign = getSign(self.dynamicSecret, params)
        data["sign"] = sign

        response = httpx.post(
            'https://jw.v.zzu.edu.cn/app-ws/ws/app-service/student/course/schedule/get-course-tables',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        coursesJson = (base64.b64decode(json.loads(response.text)["business_data"])).decode('utf-8')
        return coursesJson

    def getBalance(self):
        """
        获取校园卡余额
        :return: 校园卡余额
        :return_type: float
        """
        if not self.isLogged:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        headers = {
            'User-Agent': self.userAgentPrecursor + "uni-app Html5Plus/1.0 (Immersed/38.666668)",
            'Connection': 'Keep-Alive',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Device-Info': self.deviceInfo,
            'X-Device-Infos': self.deviceInfos,
            'X-Id-Token': self.userToken,
            'X-Terminal-Info': 'app',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = httpx.get('https://info.s.zzu.edu.cn/portal-api/v1/thrid-adapter/get-person-info-card-list',
                             headers=headers)
        return float(json.loads(response.text)["data"][1]["amount"])

    def getAreaDict(self):
        """
        获取区域的字典
        :return: 区域字典
        :rtype: dict
        """
        if not self.isLogged:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'x-id-token': self.userToken,
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        params = {
            'host': '11',
            'org': '2',
            'token': self.userToken,
        }

        response = httpx.get('https://ecard.v.zzu.edu.cn/server/auth/host/open', params=params, cookies=cookies,
                             headers=headers, follow_redirects=False)
        JSESSIONID = response.headers['set-cookie'].split("=")[1].split(";")[0]
        tid = response.headers['location'].split('=')[1].split("&")[0]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'tid': tid,
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/auth/getToken', cookies=cookies, headers=headers,
                              json=data)
        accessToken = json.loads(response.text)["resultData"]["accessToken"]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'utilityType': 'electric',
            'locationType': 'bigArea',
            'bigArea': '',
            'area': '',
            'building': '',
            'unit': '',
            'level': '',
            'room': '',
            'subArea': '',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/location', cookies=cookies,
                              headers=headers, json=data)
        AreaDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            AreaDict[json.loads(response.text)["resultData"]["locationList"][i]["id"]] = \
                json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return AreaDict

    def getBuildingDict(self, areaid):
        """
        获取建筑的字典
        :param areaid: 通过getAreaDict()获取
        :return: 建筑字典
        :rtype: dict
        """
        if self.isLogged == False:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'x-id-token': self.userToken,
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        params = {
            'host': '11',
            'org': '2',
            'token': self.userToken,
        }

        response = httpx.get('https://ecard.v.zzu.edu.cn/server/auth/host/open', params=params, cookies=cookies,
                             headers=headers, follow_redirects=False)
        JSESSIONID = response.headers['set-cookie'].split("=")[1].split(";")[0]
        tid = response.headers['location'].split('=')[1].split("&")[0]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'tid': tid,
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/auth/getToken', cookies=cookies, headers=headers,
                              json=data)
        accessToken = json.loads(response.text)["resultData"]["accessToken"]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'utilityType': 'electric',
            'locationType': 'building',
            'bigArea': '',
            'area': areaid,
            'building': '',
            'unit': '',
            'level': '',
            'room': '',
            'subArea': '',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/location', cookies=cookies,
                              headers=headers, json=data)
        BuildingDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            BuildingDict[json.loads(response.text)["resultData"]["locationList"][i]["id"]] = \
                json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return BuildingDict

    def getUnitDict(self, areaid, buildingid):
        """
        获取照明/空调的字典
        :param areaid: 通过getAreaDict()获取
        :param buildingid: 通过getBuildingDict()获取
        :return: 照明/空调字典
        :rtype: dict
        """
        if self.isLogged == False:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'x-id-token': self.userToken,
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        params = {
            'host': '11',
            'org': '2',
            'token': self.userToken,
        }

        response = httpx.get('https://ecard.v.zzu.edu.cn/server/auth/host/open', params=params, cookies=cookies,
                             headers=headers, follow_redirects=False)
        JSESSIONID = response.headers['set-cookie'].split("=")[1].split(";")[0]
        tid = response.headers['location'].split('=')[1].split("&")[0]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'tid': tid,
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/auth/getToken', cookies=cookies, headers=headers,
                              json=data)
        accessToken = json.loads(response.text)["resultData"]["accessToken"]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'utilityType': 'electric',
            'locationType': 'unit',
            'bigArea': '',
            'area': areaid,
            'building': buildingid,
            'unit': '',
            'level': '',
            'room': '',
            'subArea': '',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/location', cookies=cookies,
                              headers=headers, json=data)
        UnitDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            UnitDict[json.loads(response.text)["resultData"]["locationList"][i]["id"]] = \
                json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return UnitDict

    def getRoomDict(self, areaid, buildingid, unitid):
        """
        获取房间的字典
        :param areaid: 通过getAreaDict()获取
        :param buildingid: 通过getBuildingDict()获取
        :param unitid: 通过getUnitDict()获取
        :return: 房间字典
        :rtype: dict
        """
        if self.isLogged == False:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'x-id-token': self.userToken,
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        params = {
            'host': '11',
            'org': '2',
            'token': self.userToken,
        }

        response = httpx.get('https://ecard.v.zzu.edu.cn/server/auth/host/open', params=params, cookies=cookies,
                             headers=headers, follow_redirects=False)
        JSESSIONID = response.headers['set-cookie'].split("=")[1].split(";")[0]
        tid = response.headers['location'].split('=')[1].split("&")[0]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'tid': tid,
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/auth/getToken', cookies=cookies, headers=headers,
                              json=data)
        accessToken = json.loads(response.text)["resultData"]["accessToken"]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'utilityType': 'electric',
            'locationType': 'room',
            'bigArea': '',
            'area': areaid,
            'building': buildingid,
            'unit': '',
            'level': unitid,
            'room': '',
            'subArea': '',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/location', cookies=cookies,
                              headers=headers, json=data)
        RoomDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            RoomDict[json.loads(response.text)["resultData"]["locationList"][i]["id"]] = \
                json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return RoomDict

    def getRemainingPower(self, roomid):
        """
        获取剩余电量
        :param str roomid: 格式应为 “areaid-buildingid--unitid-roomid”，可通过getAreaDict(),getBuildingDict(),getUnitDict(),getRoomDict()获取
        :return: 剩余电量
        :rtype: float
        """
        if self.isLogged == False:
            error("RequireLogined")
        if not self.DeviceParamsSet and not self.forceDeviceParams:
            warn("Recommended set device parameters")
        cookies = {
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'x-id-token': self.userToken,
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        params = {
            'host': '11',
            'org': '2',
            'token': self.userToken,
        }

        response = httpx.get('https://ecard.v.zzu.edu.cn/server/auth/host/open', params=params, cookies=cookies,
                             headers=headers, follow_redirects=False)
        JSESSIONID = response.headers['set-cookie'].split("=")[1].split(";")[0]
        tid = response.headers['location'].split('=')[1].split("&")[0]
        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'tid': tid,
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/auth/getToken', cookies=cookies, headers=headers,
                              json=data)
        accessToken = json.loads(response.text)["resultData"]["accessToken"]

        # bind 请求，似乎不必要还会花费大量时间

        '''
        AreaDict=self.getAreaDict()
        BuildingDict=self.getBuildingDict(room.split("--")[0].split("-")[0])
        UnitDict=self.getUnitDict(room.split("--")[0].split("-")[0],room.split("--")[0].split("-")[1])
        RoomDict=self.getRoomDict(room.split("--")[0].split("-")[0],room.split("--")[0].split("-")[1],room.split("--")[1].split("-")[0])

        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }


        headers = {
            'User-Agent':  self.userAgentPrecursor+'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        json_data = {
            'bigArea': '',
            'bigAreaName': '',
            'area': room.split("--")[0].split("-")[0],
            'areaName': AreaDict[room.split("--")[0].split("-")[0]],
            'building': room.split("--")[0].split("-")[1],
            'buildingName': BuildingDict[room.split("--")[0].split("-")[1]],
            'unit': '',
            'unitName': None,
            'level': room.split("--")[1].split("-")[0],
            'levelName': UnitDict[room.split("--")[1].split("-")[0]],
            'room': room,
            'roomName': RoomDict[room],
            'subArea': '',
            'subAreaName': None,
            'utilityType': 'electric',
            'locationType': 'room',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/bind', cookies=cookies, headers=headers,
                                 json=json_data)
        '''

        cookies = {
            'JSESSIONID': JSESSIONID,
            'userToken': self.userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }

        headers = {
            'User-Agent': self.userAgentPrecursor + 'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': accessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'JSESSIONID={JSESSIONID}; userToken={self.userToken}; Domain=.zzu.edu.cn; Path=/',
        }

        data = {
            'utilityType': 'electric',
            'bigArea': '',
            'area': roomid.split("--")[0].split("-")[0],
            'building': roomid.split("--")[0].split("-")[1],
            'unit': '',
            'level': roomid.split("--")[1].split("-")[0],
            'room': roomid,
            'subArea': '',
        }

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/account', cookies=cookies,
                              headers=headers, json=data)
        return json.loads(response.text)["resultData"]["templateList"][3]["value"]
