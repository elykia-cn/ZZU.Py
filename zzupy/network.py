import base64
import random
import time
import httpx
import re
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from typing_extensions import Tuple

from zzupy.utils import get_ip_by_interface, get_default_interface


class Network:
    def __init__(self, parent):
        self._parent = parent
        self.account = self._parent._userCode
        self._JSessionID = ""
        self._checkcode = ""
        self.system_ua = ""
        self.system_loginurl = ""

    def portal_auth(
        self,
        interface: str = get_default_interface(),
        authurl="http://10.2.7.8:801",
        ua=UserAgent().random,
        isp="campus",
    ) -> Tuple[str, bool, str]:
        """
        进行校园网认证

        :param str interface: 网络接口名
        :param str authurl: PortalAuth 服务器。根据情况修改
        :param str ua: User-Agent
        :param str isp: 运营商。可选项：campus,cm
        :returns: Tuple[str, bool, str]

            - **interface** (str) – 本次认证调用的网络接口。
            - **success** (bool) – 认证是否成功。(不可信，有时失败仍可正常上网)
            - **msg** (str) – 服务端返回信息。
        :rtype: Tuple[str,bool,str]
        """
        if isp == "campus":
            self.account = self._parent._userCode
        elif isp == "ct":
            self.account = self._parent._userCode + "@cmcc"
        elif isp == "cu":
            self.account = self._parent._userCode + "@cmcc"
        elif isp == "cm":
            self.account = self._parent._userCode + "@cmcc"
        else:
            self.account = self._parent._userCode
        transport = httpx.HTTPTransport(local_address=get_ip_by_interface(interface))
        local_client = httpx.Client(transport=transport)
        self._chkstatus(local_client, authurl, ua)
        self._loadConfig(local_client, interface, authurl, ua)
        return self._auth(local_client, interface, authurl, ua)

    def _auth(
        self,
        client,
        interface,
        baseURL,
        ua,
    ):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "http://10.2.7.8/",
            "User-Agent": ua,
        }
        params = [
            ("callback", "dr1003"),
            ("login_method", "1"),
            ("user_account", f",0,{self.account}"),
            (
                "user_password",
                base64.b64encode(self._parent._password.encode()).decode(),
            ),
            ("wlan_user_ip", get_ip_by_interface(interface)),
            ("wlan_user_ipv6", ""),
            ("wlan_user_mac", "000000000000"),
            ("wlan_ac_ip", ""),
            ("wlan_ac_name", ""),
            ("jsVersion", "4.2.1"),
            ("terminal_type", "1"),
            ("lang", "zh-cn"),
            ("v", str(random.randint(500, 10499))),
            ("lang", "zh"),
        ]
        response = client.get(
            f"{baseURL}/eportal/portal/login", params=params, headers=headers
        )
        res_json = json.loads(re.findall(r"dr1003\((.*?)\);", response.text)[0])
        if res_json["result"] == 0:
            success = False
        else:
            success = True
        return interface, success, res_json["msg"]

    # 现在发现可有可无好像
    def _chkstatus(self, client, baseURL, ua):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "http://10.2.7.8/a79.htm",
            "User-Agent": ua,
        }

        params = {
            "callback": "dr1002",
            "jsVersion": "4.X",
            "v": str(random.randint(500, 10499)),
            "lang": "zh",
        }
        client.get(
            re.sub(r":\d+", "", baseURL) + "/drcom/chkstatus",
            params=params,
            headers=headers,
        )

    def _loadConfig(self, client, interface, baseURL, ua):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "http://10.2.7.8/",
            "User-Agent": ua,
        }

        params = {
            "callback": "dr1001",
            "program_index": "",
            "wlan_vlan_id": "1",
            "wlan_user_ip": base64.b64encode(
                get_ip_by_interface(interface).encode()
            ).decode(),
            "wlan_user_ipv6": "",
            "wlan_user_ssid": "",
            "wlan_user_areaid": "",
            "wlan_ac_ip": "",
            "wlan_ap_mac": "000000000000",
            "gw_id": "000000000000",
            "jsVersion": "4.X",
            "v": str(random.randint(500, 10499)),
            "lang": "zh",
        }
        client.get(
            f"{baseURL}/eportal/portal/page/loadConfig", params=params, headers=headers
        )

    def login(
        self, loginurl: str = "http://10.2.7.16:8080", ua: str = UserAgent().random
    ):
        """
        登录自助服务平台

        :param str loginurl: 自助服务平台的登录 URL
        :param str ua: User Agent
        """
        self.system_ua = ua
        self.system_loginurl = loginurl
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.system_ua,
        }

        response = httpx.get(
            f"{self.system_loginurl}/Self/login/",
            headers=headers,
            verify=False,
            follow_redirects=False,
        )
        self._JSessionID = response.headers["set-cookie"].split("=")[1].split(";")[0]
        soup = BeautifulSoup(response.text, features="html.parser")
        self._checkcode = soup.find_all("input", attrs={"name": "checkcode"})[0][
            "value"
        ]
        cookies = {
            "JSESSIONID": self._JSessionID,
        }

        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/login/",
            "User-Agent": self.system_ua,
        }

        params = {
            "t": str(random.random()),
        }

        httpx.get(
            f"{self.system_loginurl}/Self/login/randomCode",
            params=params,
            cookies=cookies,
            headers=headers,
            verify=False,
        )

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": f"{self.system_loginurl}",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/login/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.system_ua,
        }

        data = {
            "foo": "",
            "bar": "",
            # 我草，太坏了，这个 checkcode 居然是直接动态写死在网页里的，搞得我扣了半天算法抠不出来
            "checkcode": self._checkcode,
            "account": self._parent._userCode,
            "password": self._parent._password,
            "code": "",
        }
        httpx.post(
            f"{self.system_loginurl}/Self/login/verify;jsessionid={self._JSessionID}",
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )

    def get_online_devices(self) -> str:
        """
        获取全部在线设备

        :return: Json 格式的在线设备数据
        :rtype: str
        """
        cookies = {
            "JSESSIONID": self._JSessionID,
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/dashboard",
            "User-Agent": self.system_ua,
            "X-Requested-With": "XMLHttpRequest",
        }

        params = {
            "t": str(random.random()),
            "order": "asc",
            "_": str(int(time.time())),
        }

        response = httpx.get(
            f"{self.system_loginurl}/Self/dashboard/getOnlineList",
            params=params,
            cookies=cookies,
            headers=headers,
            verify=False,
        )
        return response.text

    def get_total_traffic(self) -> int:
        """
        获取消耗的流量

        :return: 消耗的流量，单位为 MB
        :rtype: int
        """

        cookies = {
            "JSESSIONID": self._JSessionID,
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/login/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.system_ua,
        }

        response = httpx.get(
            f"{self.system_loginurl}/Self/dashboard",
            cookies=cookies,
            headers=headers,
            verify=False,
        )
        soup = BeautifulSoup(response.text, features="html.parser")
        return int(soup.find_all("dt")[1].text.strip().split()[0])

    def get_used_time(self) -> int:
        """
        获取使用时间

        :return int: 使用时间，单位为 分钟
        :rtype: int
        """
        cookies = {
            "JSESSIONID": self._JSessionID,
        }

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/login/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.system_ua,
        }

        response = httpx.get(
            f"{self.system_loginurl}/Self/dashboard",
            cookies=cookies,
            headers=headers,
            verify=False,
        )
        soup = BeautifulSoup(response.text, features="html.parser")
        return int(soup.find_all("dt")[0].text.strip().split()[0])

    def logout_device(self, sessionid: str) -> bool:
        """

        :param str sessionid: sessionid,可通过 get_online_devices() 获取
        :return: 成功或失败
        :rtype: bool
        """
        cookies = {
            "JSESSIONID": self._JSessionID,
        }

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": f"{self.system_loginurl}/Self/dashboard",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        params = {
            "t": str(random.random()),
            "sessionid": sessionid,
        }

        response = httpx.get(
            f"{self.system_loginurl}/Self/dashboard/tooffline",
            params=params,
            cookies=cookies,
            headers=headers,
            verify=False,
        )
        if response.status_code == 200 and json.loads(response.text)["success"]:
            return True
        else:
            # Log
            return False
