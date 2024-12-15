import base64
import json
import time
import httpx
import gmalg
from typing_extensions import Tuple

from zzupy.utils import sm4_decrypt_ecb


class eCard:
    def __init__(self, parent):
        self._parent = parent
        self._eCardAccessToken = ""
        self._JSessionID = ""
        self._tid = ""

    def _get_eacrd_access_token(self):
        cookies = {
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.get(
            "https://ecard.v.zzu.edu.cn/server/auth/host/open",
            params=params,
            cookies=cookies,
            headers=headers,
            follow_redirects=False,
        )
        self._JSessionID = response.headers["set-cookie"].split("=")[1].split(";")[0]
        self._tid = response.headers["location"].split("=")[1].split("&")[0]
        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/auth/getToken",
            cookies=cookies,
            headers=headers,
            json=data,
        )
        self._eCardAccessToken = json.loads(response.text)["resultData"]["accessToken"]

    def recharge_electricity(
        self, room: str, paypasswd: str, amt: int
    ) -> Tuple[bool, str]:
        """
        为 room 充值电费

        :param str room: 宿舍房间。理论上空调和照明均支持.格式应为 “areaid-buildingid--unitid-roomid”，可通过get_area_dict(),get_building_dict(),get_unit_dict(),get_room_dict()获取
        :param str paypasswd: 支付密码
        :param int amt: 充值金额
        :returns: Tuple[bool, str]

            - **success** (bool) – 充值是否成功
            - **msg** (str) – 服务端返回信息。
        :rtype: Tuple[bool,str]
        """
        cookies = {
            "JSESSIONID": self._JSessionID,
        }

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
        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/auth/getEncrypt",
            cookies=cookies,
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
            "password": paypasswd,
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
        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/pay",
            cookies=cookies,
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
        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            cookies=cookies,
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
        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            cookies=cookies,
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
        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            cookies=cookies,
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
        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/location",
            cookies=cookies,
            headers=headers,
            json=data,
        )
        RoomDict = {}
        for i in range(len(json.loads(response.text)["resultData"]["locationList"])):
            RoomDict[
                json.loads(response.text)["resultData"]["locationList"][i]["id"]
            ] = json.loads(response.text)["resultData"]["locationList"][i]["name"]
        return RoomDict

    def get_remaining_power(self, room: str) -> float:
        """
        获取剩余电量

        :param str room: 格式应为 “areaid-buildingid--unitid-roomid”，可通过get_area_dict(),get_building_dict(),get_unit_dict(),get_room_dict()获取
        :return: 剩余电量
        :rtype: float
        """
        # bind 请求，似乎不必要还会花费大量时间
        """
        AreaDict=self.get_area_dict()
        BuildingDict=self.get_building_dict(room.split("--")[0].split("-")[0])
        UnitDict=self.get_unit_dict(room.split("--")[0].split("-")[0],room.split("--")[0].split("-")[1])
        RoomDict=self.get_room_dict(room.split("--")[0].split("-")[0],room.split("--")[0].split("-")[1],room.split("--")[1].split("-")[0])

        cookies = {
            'JSESSIONID': self._JSessionID,
            'userToken': self._parent._userToken,
            'Domain': '.zzu.edu.cn',
            'Path': '/',
        }


        headers = {
            'User-Agent':  self._parent._DeviceParams["userAgentPrecursor"]+'SuperApp',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'sec-ch-ua-platform': '"Android"',
            'Authorization': self._eCardAccessToken,
            'sec-ch-ua': '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://ecard.v.zzu.edu.cn',
            'X-Requested-With': 'com.supwisdom.zzu',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://ecard.v.zzu.edu.cn/?tid={_tid}&orgId=2',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
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

        response = httpx.post('https://ecard.v.zzu.edu.cn/server/utilities/bind', cookies=cookies, headers=headers,json=json_data)
        """

        cookies = {
            "JSESSIONID": self._JSessionID,
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
        }

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

        response = httpx.post(
            "https://ecard.v.zzu.edu.cn/server/utilities/account",
            cookies=cookies,
            headers=headers,
            json=data,
        )
        return json.loads(response.text)["resultData"]["templateList"][3]["value"]
