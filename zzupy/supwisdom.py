import base64
import datetime
import json
import random
import time
import httpx

from zzupy.utils import get_sign


class Supwisdom:
    def __init__(self, parent):
        self._parent = parent

    def get_courses(self, start_date: str) -> str:
        """
        获取课程表

        :param str start_date: 课表的开始日期，格式必须为 %Y-%m-%d ，且必须为某一周周一，否则课表会时间错乱
        :return: 返回 Json 格式的课程表数据
        :rtype: str
        """
        cookies = {
            "userToken": self._parent._userToken,
            "Domain": ".zzu.edu.cn",
            "Path": "/",
            "SVRNAME": "ws1",
        }

        headers = {
            "User-Agent": self._parent._DeviceParams["userAgentPrecursor"] + "SuperApp",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "sec-ch-ua-mobile": "?1",
            "token": self._parent._dynamicToken,
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
            "biz_type_id": "1",
            "end_date": (
                datetime.datetime.strptime(start_date, "%Y-%m-%d")
                + datetime.timedelta(days=6)
            ).strftime("%Y-%m-%d"),
            "random": int(random.uniform(10000, 99999)),
            "semester_id": "152",
            "start_date": start_date,
            "timestamp": int(round(time.time() * 1000)),
            "token": self._parent._userToken,
        }

        params = ""
        for key in data.keys():
            params += f"{key}={data[key]}&"
        params = params[:-1]
        sign = get_sign(self._parent._dynamicSecret, params)
        data["sign"] = sign

        response = httpx.post(
            "https://jw.v.zzu.edu.cn/app-ws/ws/app-service/student/course/schedule/get-course-tables",
            cookies=cookies,
            headers=headers,
            data=data,
        )
        coursesJson = (
            base64.b64decode(json.loads(response.text)["business_data"])
        ).decode("utf-8")
        sorted_courses_json = sorted(
            json.loads(coursesJson),
            key=lambda x: (
                x["date"],
                datetime.datetime.strptime(x["start_time"], "%H:%M"),
            ),
        )
        return json.dumps(sorted_courses_json).encode("utf-8").decode("unicode_escape")
