import base64
import json
import threading
import time
import warnings

import httpx
import gmalg
from typing_extensions import Tuple
from loguru import logger

from zzupy.exception import LoginException
from zzupy.utils import sm4_decrypt_ecb


class eCard:
    def __init__(self, parent):
        self._parent = parent
        self._eCardAccessToken = ""
        self._JSessionID = ""
        self._tid = ""
        self._start_token_refresh_timer()

    def _start_token_refresh_timer(self):
        self._get_ecard_access_token()
        # 每 45 分钟（2700 秒）执行一次
        self._timer = threading.Timer(2700, self._start_token_refresh_timer)
        self._timer.start()

    def _get_ecard_access_token(self):
        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Upgrade-Insecure-Requests": "1",
            "x-id-token": self._parent._userToken,
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        params = {
            "host": "11",
            "org": "2",
            "token": self._parent._userToken,
        }
        logger.debug("尝试获取 JSessionID 和 tid")
        response = self._parent._client.get(
            "https://ecard.v.zzu.edu.cn/server/auth/host/open",
            params=params,
            headers=headers,
            follow_redirects=False,
        )
        logger.debug(f"/auth/host/open 请求响应头：{response.headers}")
        try:
            self._JSessionID = (
                response.headers["set-cookie"].split("=")[1].split(";")[0]
            )
            self._tid = response.headers["location"].split("=")[1].split("&")[0]
        except Exception as exc:
            logger.error("从 /auth/host/open 请求中提取 JSessionID 和 tid 失败")
            raise LoginException from exc

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "tid": self._tid,
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/auth/getToken",
            headers=headers,
            json=data,
        )
        logger.debug(f"/auth/getToken 请求响应体：{response.text}")
        self._eCardAccessToken = json.loads(response.text)["resultData"]["accessToken"]
        self._eCardRefreshToken = json.loads(response.text)["resultData"][
            "refreshToken"
        ]

    def recharge_energy(
        self, payment_password: str, amt: int, room: str | None = None
    ) -> Tuple[bool, str]:
        """
        为 room 充值电费

        :param str room: 宿舍房间。理论上空调和照明均支持.格式应为 “areaid-buildingid--unitid-roomid”，可通过get_area_dict(),get_building_dict(),get_unit_dict(),get_room_dict()获取
        :param str payment_password: 支付密码
        :param int amt: 充值金额
        :returns: Tuple[bool, str]

            - **success** (bool) – 充值是否成功
            - **msg** (str) – 服务端返回信息。
        :rtype: Tuple[bool,str]
        """
        if room is None:
            headers = {
                "User-Agent": self._parent._DeviceParams["userAgentPrecursor"]
                + "SuperApp",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": '"Android"',
                "Authorization": self._eCardAccessToken,
                "sec-ch-ua": '"Not(A:Brand";v="99", "Android WebView";v="133", "Chromium";v="133"',
                "sec-ch-ua-mobile": "?1",
                "Origin": "https://ecard.v.zzu.edu.cn",
                "X-Requested-With": "com.supwisdom.zzu",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            }

            data = {
                "utilityType": "electric",
            }

            response = self._parent._client.post(
                "https://ecard.v.zzu.edu.cn/server/utilities/config",
                headers=headers,
                json=data,
            )
            logger.debug(f"/utilities/config 请求响应体：{response.text}")
            logger.debug("尝试获取默认 room")
            room = json.loads(response.text)["resultData"]["location"]["room"]

        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": self._eCardAccessToken,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "Pragma": "no-cache",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/auth/getEncrypt",
            headers=headers,
        )
        pay_id = json.loads(response.text)["resultData"]["id"]
        encrypted_public_key = json.loads(response.text)["resultData"]["publicKey"]
        # 解密被加密的公钥
        public_key = sm4_decrypt_ecb(
            base64.b64decode(encrypted_public_key),
            bytes.fromhex("773638372d392b33435f48266a655f35"),
        )
        # 请求体明文
        json_data = {
            "utilityType": "electric",
            "payCode": "06",
            "password": payment_password,
            "amt": str(amt),
            "timestamp": int(round(time.time() * 1000)),
            "bigArea": "",
            "area": room.split("--")[0].split("-")[0],
            "building": room.split("--")[0].split("-")[1],
            "unit": "",
            "level": room.split("--")[1].split("-")[0],
            "room": room,
            "subArea": "",
            "customfield": {},
        }
        json_string = json.dumps(json_data, separators=(",", ":"))
        # 加密 params
        sm2 = gmalg.SM2(pk=bytes.fromhex(public_key))
        encrypted_params = sm2.encrypt(json_string.encode())
        data = {"id": pay_id, "params": (encrypted_params.hex())[2:]}
        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/pay",
            headers=headers,
            json=data,
        )
        return (
            json.loads(response.text)["success"],
            json.loads(response.text)["message"],
        )

    def get_balance(self) -> float:
        """
        获取校园卡余额

        :return: 校园卡余额
        :rtype: float
        """

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"]
            + "uni-app Html5Plus/1.0 (Immersed/38.666668)",
            "Connection": "Keep-Alive",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Device-Info": self._parent._DeviceParams["deviceInfo"],
            "X-Device-Infos": self._parent._DeviceParams["deviceInfos"],
            "X-Id-Token": self._parent._userToken,
            "X-Terminal-Info": "app",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = httpx.get(
            "https://info.s.zzu.edu.cn/portal-api/v1/thrid-adapter/get-person-info-card-list",
            headers=headers,
        )
        return float(json.loads(response.text)["data"][1]["amount"])

    def get_area_dict(self) -> dict:
        """
        获取区域的字典

        :return: 区域字典
        :rtype: dict
        """

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "Authorization": self._eCardAccessToken,
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "utilityType": "electric",
            "locationType": "bigArea",
            "bigArea": "",
            "area": "",
            "building": "",
            "unit": "",
            "level": "",
            "room": "",
            "subArea": "",
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            headers=headers,
            json=data,
        )
        AreaDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            AreaDict[
                json.loads(response.text)["resultData"]["locationList"][i]["id"]
            ] = json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return AreaDict

    def get_building_dict(self, areaid: str) -> dict:
        """
        获取建筑的字典

        :param str areaid: 通过get_area_dict()获取
        :return: 建筑字典
        :rtype: dict
        """

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "Authorization": self._eCardAccessToken,
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "utilityType": "electric",
            "locationType": "building",
            "bigArea": "",
            "area": areaid,
            "building": "",
            "unit": "",
            "level": "",
            "room": "",
            "subArea": "",
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            headers=headers,
            json=data,
        )
        BuildingDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            BuildingDict[
                json.loads(response.text)["resultData"]["locationList"][i]["id"]
            ] = json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return BuildingDict

    def get_unit_dict(self, areaid: str, buildingid: str) -> dict:
        """
        获取照明/空调的字典

        :param str areaid: 通过get_unit_dict()获取
        :param str buildingid: 通过get_building_dict()获取
        :return: 照明/空调字典
        :rtype: dict
        """

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "Authorization": self._eCardAccessToken,
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "utilityType": "electric",
            "locationType": "unit",
            "bigArea": "",
            "area": areaid,
            "building": buildingid,
            "unit": "",
            "level": "",
            "room": "",
            "subArea": "",
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            headers=headers,
            json=data,
        )
        UnitDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            UnitDict[
                json.loads(response.text)["resultData"]["locationList"][i]["id"]
            ] = json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return UnitDict

    def get_room_dict(self, areaid: str, buildingid: str, unitid: str) -> dict:
        """
        获取房间的字典

        :param str areaid: 通过get_area_dict()获取
        :param str buildingid: 通过get_building_dict()获取
        :param str unitid: 通过get_unit_dict()获取
        :return: 房间字典
        :rtype: dict
        """
        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "Authorization": self._eCardAccessToken,
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "utilityType": "electric",
            "locationType": "room",
            "bigArea": "",
            "area": areaid,
            "building": buildingid,
            "unit": "",
            "level": unitid,
            "room": "",
            "subArea": "",
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            headers=headers,
            json=data,
        )
        RoomDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            RoomDict[
                json.loads(response.text)["resultData"]["locationList"][i]["id"]
            ] = json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return RoomDict

    def get_remaining_energy(self, room: str | None = None) -> float:
        """
        获取剩余电量

        :param str room: 格式应为 “areaid-buildingid--unitid-roomid”，可通过get_area_dict(),get_building_dict(),get_unit_dict(),get_room_dict()获取
        :return: 剩余电量
        :rtype: float
        """
        if room is None:
            headers = {
                "User-Agent": self._parent._DeviceParams["userAgentPrecursor"]
                + "SuperApp",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": '"Android"',
                "Authorization": self._eCardAccessToken,
                "sec-ch-ua": '"Not(A:Brand";v="99", "Android WebView";v="133", "Chromium";v="133"',
                "sec-ch-ua-mobile": "?1",
                "Origin": "https://ecard.v.zzu.edu.cn",
                "X-Requested-With": "com.supwisdom.zzu",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            }

            data = {
                "utilityType": "electric",
            }

            response = self._parent._client.post(
                "https://ecard.v.zzu.edu.cn/server/utilities/config",
                headers=headers,
                json=data,
            )
            logger.debug(f"/utilities/config 请求响应体：{response.text}")
            logger.debug("尝试获取默认 room")
            room = json.loads(response.text)["resultData"]["location"]["room"]

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": '"Android"',
            "Authorization": self._eCardAccessToken,
            "sec-ch-ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ecard.v.zzu.edu.cn",
            "X-Requested-With": "com.supwisdom.zzu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://ecard.v.zzu.edu.cn/?tid={self._tid}&orgId=2",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        data = {
            "utilityType": "electric",
            "bigArea": "",
            "area": room.split("--")[0].split("-")[0],
            "building": room.split("--")[0].split("-")[1],
            "unit": "",
            "level": room.split("--")[1].split("-")[0],
            "room": room,
            "subArea": "",
        }

        response = self._parent._client.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/account",
            headers=headers,
            json=data,
        )
        return float(
            json.loads(response.text)["resultData"]["templateList"][3]["value"]
        )

    def get_remaining_power(self, room: str | None = None) -> float:
        logger.warning("get_remaining_power() 已废弃，请使用 get_remaining_energy()")
        warnings.warn(
            "get_remaining_power() is deprecated, please use get_remaining_energy()",
            DeprecationWarning,
        )
        return self.get_remaining_energy(room)

    def recharge_electricity(
        self, payment_password: str, amt: int, room: str | None = None
    ) -> Tuple[bool, str]:
        logger.warning("recharge_electricity() 已废弃，请使用 recharge_energy()")
        warnings.warn(
            "recharge_electricity() is deprecated, please use recharge_energy()",
            DeprecationWarning,
        )
        return self.recharge_energy(payment_password, amt, room)
