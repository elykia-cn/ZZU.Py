import random

import httpx
import json
import base64
import time
from typing_extensions import Unpack, Tuple
from http.cookies import SimpleCookie
from loguru import logger

from zzupy.typing import DeviceParams
from zzupy.utils import get_sign, _kget
from zzupy.supwisdom import Supwisdom
from zzupy.ecard import eCard
from zzupy.network import Network
from zzupy.exception import LoginException


class ZZUPy:
    def __init__(
        self, usercode: str, password: str, cookie: SimpleCookie | None = None
    ):
        """
        初始化一个 ZZUPy 对象

        :param str usercode: 学号
        :param str password: 密码
        :param SimpleCookie cookie: 统一认证 Cookie。目前必须包含 'userToken'，否则会抛出 ValueError
        :raises ValueError: Cookie 中缺少 'userToken' 时抛出
        """
        self._userToken = None
        # 固定值
        self._dynamicSecret = "supwisdom_eams_app_secret"
        self._dynamicToken = None
        self._refreshToken = None
        self._name = None
        self._isLogged = False
        self._DeviceParams = {
            "deviceName": "",
            "deviceId": "",
            "deviceInfo": "",
            "deviceInfos": "",
            "userAgentPrecursor": "",
        }
        self._usercode = usercode
        self._password = password
        logger.debug(f"已配置账户 {usercode}")
        # 初始化 HTTPX
        self._client = httpx.Client(follow_redirects=True)
        if cookie is SimpleCookie:
            for key, morsel in cookie.items():
                self._client.cookies.set(
                    key, morsel.value, morsel["domain"], morsel["path"]
                )
                if key == "userToken":
                    self._userToken = morsel.value
            if self._userToken is None:
                raise ValueError("Cookie 中缺少 'userToken'")
        logger.debug("已配置 HTTPX 实例")
        # 初始化类
        self.Network = Network(self)
        self.eCard = eCard(self)
        self.Supwisdom = Supwisdom(self)
        logger.debug("已配置类")
        logger.info(f"账户 {usercode} 初始化完成")

    def is_logged_in(self) -> bool:
        """
        判断是否已登录

        :return: 是否已登录
        :rtype: bool
        """
        if self._isLogged:
            return True
        else:
            return False

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
        logger.info("已配置设备参数")

    def login(
        self,
        appVersion: str = "SWSuperApp/1.0.39",
        appId: str = "com.supwisdom.zzu",
        osType: str = "android",
    ) -> Tuple[str, str]:
        """
        登录

        :param str appVersion: APP 版本 ，一般类似 "SWSuperApp/1.0.38" ，可自行更新版本号。
        :param str appId: APP 包名，一般不需要修改
        :param str osType: 系统类型，一般不需要修改
        :returns: Tuple[str, str]

            - **usercode** (str) – 学号
            - **name** (str) – 姓名
        :rtype: Tuple[str,str]
        :raises LoginException: 登录失败时抛出
        """
        logger.info(f"尝试登录账户 {self._usercode}")
        if self._client.cookies.get("userToken") is None:
            headers = {
                "User-Agent": f"{appVersion}({self._DeviceParams['deviceName']})",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
            }
            response = self._client.post(
                f"https://token.s.zzu.edu.cn/password/passwordLogin?username={self._usercode}&password={self._password}&appId={appId}&geo&deviceId={self._DeviceParams['deviceId']}&osType={osType}&clientId&mfaState",
                headers=headers,
            )
            logger.debug(f"/passwordLogin 请求响应体: {response.text}")
            # 获取 userToken 和 refreshToken
            try:
                self._userToken = json.loads(response.text)["data"]["idToken"]
                # 我也不知道 refreshToken 有什么用，但先存着吧
                self._client.cookies.set(
                    "userToken", self._userToken, ".zzu.edu.cn", "/"
                )
                self._refreshToken = json.loads(response.text)["data"]["refreshToken"]
            except Exception as exc:
                logger.error(
                    "从 /passwordLogin 请求中提取 userToken 和 refreshToken 失败"
                )
                raise LoginException("登录失败, 通过 DEBUG 日志获得更多信息") from exc
        else:
            logger.info(f"userToken 已设置，跳过帐密登录")

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

        response = self._client.post(
            "https://jw.v.zzu.edu.cn/app-ws/ws/app-service/super/app/login-token",
            headers=headers,
            data=data,
        )
        logger.debug(f"/login-token 请求响应体: {response.text}")
        try:
            self._dynamicSecret = json.loads(
                base64.b64decode(json.loads(response.text)["business_data"])
            )["secret"]
            self._dynamicToken = json.loads(
                base64.b64decode(json.loads(response.text)["business_data"])
            )["token"]
            self._name = json.loads(
                base64.b64decode(json.loads(response.text)["business_data"])
            )["user_info"]["user_name"]
        except Exception as exc:
            logger.error(
                "从 /login-token 请求中提取 dynamicSecret 、 dynamicToken 和用户信息失败"
            )
            raise LoginException("登录失败, 通过 DEBUG 日志获得更多信息") from exc
        self.eCard._start_token_refresh_timer()
        self._isLogged = True
        logger.info(f"账户 {self._usercode} 登录成功")
        return self._usercode, self._name
