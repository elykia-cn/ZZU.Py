import base64
import random
import httpx
import re
import json
from fake_useragent import UserAgent
from typing_extensions import Tuple

from zzupy.utils import get_ip_by_interface, get_default_interface


class Network:
    def __init__(self, parent):
        self._parent = parent
        self.account = self._parent._userCode

    def portal_auth(
        self,
        interface: str = get_default_interface(),
        baseurl="http://10.2.7.8:801",
        ua=UserAgent().random,
        isp="campus",
    ) -> Tuple[str, bool, str]:
        """
        进行校园网认证

        :param str interface: 网络接口名
        :param str baseurl: PortalAuth Server URL。一般无需修改
        :param str ua: User-Agent
        :param str isp: 运营商。可选项：campus,cmcc
        :returns: Tuple[str, bool, str]

            - **interface** (str) – 本次认证调用的网络接口。
            - **success** (bool) – 认证是否成功。(不可信，有时失败仍可正常上网)
            - **msg** (str) – 服务端返回信息。
        :rtype: Tuple[str,bool,str]
        """
        if isp == "campus":
            self.account = self._parent._userCode
        elif isp == "cmcc":
            self.account = self._parent._userCode + "@cmcc"
        else:
            self.account = self._parent._userCode
        transport = httpx.HTTPTransport(local_address=get_ip_by_interface(interface))
        local_client = httpx.Client(transport=transport)
        self._chkstatus(local_client, baseurl, ua)
        self._loadConfig(local_client, interface, baseurl, ua)
        return self._auth(local_client, interface, baseurl, ua)

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
            f"{re.sub(r':\d+', '', baseURL)}/drcom/chkstatus",
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
