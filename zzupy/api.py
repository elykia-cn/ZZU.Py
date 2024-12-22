import random
import httpx
import json
import base64
import time
from typing_extensions import Unpack, Tuple

from zzupy.log import logger
from zzupy.typing import DeviceParams
from zzupy.utils import get_sign, _kget
from zzupy.supwisdom import Supwisdom
from zzupy.ecard import eCard
from zzupy.network import Network


class ZZUPy:
    def __init__(self, usercode: str, password: str, log: bool = False):
        """
        初始化一个 ZZUPy 对象

        :param str usercode: 学号
        :param str password: 密码
        :param bool log: 是否启用日志
        """
        self._userToken = None
        self._dynamicSecret = "supwisdom_eams_app_secret"
        self._dynamicToken = None
        self._refreshToken = None
        self._name = None
        self._isLogged = False
        self._logEnabled = log
        self._DeviceParams = {}
        self._DeviceParams["deviceName"] = ""
        self._DeviceParams["deviceId"] = ""
        self._DeviceParams["deviceInfo"] = ""
        self._DeviceParams["deviceInfos"] = ""
        self._DeviceParams["userAgentPrecursor"] = ""
        self._userCode = usercode
        self._password = password
        # 初始化类
        self.Network = Network(self)
        self.eCard = eCard(self)
        self.Supwisdom = Supwisdom(self)

    def _set_params_from_password_login(self, res: str):
        try:
            self._userToken = json.loads(res)["data"]["idToken"]
            # 我也不知道 refreshToken 有什么用，但先存着吧
            self._refreshToken = json.loads(res)["data"]["refreshToken"]
        except:
            logger.error("LoginFailed")

    def _set_params_from_login_token(self, res: str):
        try:
            self._dynamicSecret = json.loads(
                base64.b64decode(json.loads(res)["business_data"])
            )["secret"]
            self._dynamicToken = json.loads(
                base64.b64decode(json.loads(res)["business_data"])
            )["token"]
            self._name = json.loads(base64.b64decode(json.loads(res)["business_data"]))[
                "user_info"
            ]["user_name"]
        except:
            logger.error("LoginFailed")

    def set_device_params(self, **kwargs: Unpack[DeviceParams]):
        """
        设置设备参数。这些参数都需要抓包获取，但其实可有可无，因为目前并没有观察到相关风控机制

        :param str deviceName: 设备名 ，位于 "passwordLogin" 请求的 User-Agent 中，组成为 '{appVersion}({deviceName})'
        :param str deviceId: 设备 ID ，
        :param str deviceInfo: 设备信息，位于名为 "X-Device-Info" 的请求头中
        :param str deviceInfos: 设备信息，位于名为 "X-Device-Infos" 的请求头中
        :param str userAgentPrecursor: 设备 UA 前体 ，只需要包含 "SuperApp" 或 "uni-app Html5Plus/1.0 (Immersed/38.666668)" 前面的部分
        """
        self._DeviceParams["deviceName"] = _kget(kwargs, "deviceName", "")
        self._DeviceParams["deviceId"] = _kget(kwargs, "deviceId", "")
        self._DeviceParams["deviceInfo"] = _kget(kwargs, "deviceInfo", "")
        self._DeviceParams["deviceInfos"] = _kget(kwargs, "deviceInfos", "")
        self._DeviceParams["userAgentPrecursor"] = _kget(kwargs, "deviceInfos", "")
        if self._DeviceParams["userAgentPrecursor"].endswith(" "):
            self._DeviceParams["userAgentPrecursor"] = self._DeviceParams[
                "userAgentPrecursor"
            ]
        else:
            self._DeviceParams["userAgentPrecursor"] = (
                self._DeviceParams["userAgentPrecursor"] + " "
            )
        # self.DeviceParamsSet = True

    def login(
        self,
        appVersion: str = "SWSuperApp/1.0.33",
        appId: str = "com.supwisdom.zzu",
        osType: str = "android",
    ) -> Tuple[str, str]:
        """
        通过学号和密码登录

        :param str appVersion: APP 版本 ，一般类似 "SWSuperApp/1.0.33" ，可自行更新版本号，但详细数据需要抓包获取,位于 "passwordLogin" 请求的 User-Agent 中，也可随便填或空着，目前没有观察到相关风控机制。
        :param str appId: APP 包名，一般不需要修改
        :param str osType: 系统类型，一般不需要修改
        :returns: Tuple[str, str]

            - **usercode** (str) – 学号
            - **name** (str) – 姓名
        :rtype: Tuple[str,str]
        """
        headers = {
            "User-Agent": f'{appVersion}({self._DeviceParams["deviceName"]})',
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
        response = httpx.post(
            f'https://token.s.zzu.edu.cn/password/passwordLogin?username={self._userCode}&password={self._password}&appId={appId}&geo&deviceId={self._DeviceParams["deviceId"]}&osType={osType}&clientId&mfaState',
            headers=headers,
        )
        self._set_params_from_password_login(response.text)
        cookies = {
            "userToken": self._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
            "SVRNAME": "ws1",
        }

        headers = {
            "User-Agent": self._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Origin": "https://jw.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://jw.v.zzu.edu.cn/app-web/",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": f"userToken={self._userToken}; Domain=.zzu.edu.cn; Path=/; SVRNAME=ws1",
        }
        data = {
            "random": int(random.uniform(10000, 99999)),
            "timestamp": int(round(time.time() * 1000)),
            "userToken": self._userToken,
        }
        # 计算 sign 并将其加入 data
        params = ""
        for key in data.keys():
            params += f"{key}={data[key]}&"
        params = params[:-1]
        sign = get_sign(self._dynamicSecret, params)
        data["sign"] = sign

        response = httpx.post(
            "https://jw.v.zzu.edu.cn/app-ws/ws/app-service/super/app/login-token",
            cookies=cookies,
            headers=headers,
            data=data,
        )
        self._set_params_from_login_token(response.text)
        self._isLogged = True
        self.eCard._get_eacrd_access_token()
        return self._userCode, self._name
