import base64
import random
import httpx
from fake_useragent import UserAgent

from zzupy.utils import get_ip_by_interface


class Network:
    def __init__(self, parent):
        self._parent = parent

    def portal_auth(
        self, interface: str = "", baseurl="http://10.2.7.8:801", ua=UserAgent()
    ):
        """
        进行校园网认证

        :param str interface: 网络接口名
        :param str baseurl: PortalAuth Server URL。一般无需修改
        :param str ua: User-Agent
        """
        if interface == "":
            local_client = httpx.Client()
        else:
            transport = httpx.HTTPTransport(
                local_address=get_ip_by_interface(interface)
            )
            local_client = httpx.Client(transport=transport)
        self._chkstatus(local_client, baseurl, ua)
        self._loadConfig(local_client, interface, baseurl, ua)
        self._auth(local_client, interface, baseurl, ua)

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
            ("user_account", f",0,{self._parent.userCode}"),
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
        return interface, response.text

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
        client.get(f"{baseURL}/drcom/chkstatus", params=params, headers=headers)

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
