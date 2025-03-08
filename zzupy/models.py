from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json


class Room(BaseModel):
    """教室信息模型"""

    address: str
    """教室地址"""
    building: str
    """所在建筑"""
    code: str
    """教室代码"""
    id: int
    """教室ID"""
    latitude: str = Field(default="")
    """纬度"""
    longitude: str = Field(default="")
    """经度"""
    name: str
    """教室名称"""


class Teacher(BaseModel):
    """教师信息模型"""

    code: str
    """教师代码"""
    id: int
    """教师ID"""
    name: str
    """教师姓名"""


class Course(BaseModel):
    """单个课程信息模型"""

    course_code: str
    """课程代码"""
    course_name: str
    """课程名称"""
    date: str
    """上课日期，格式为YYYY-MM-DD"""
    end_time: str
    """下课时间，格式为HH:MM"""
    end_unit: int
    """结束节次"""
    lesson_id: int
    """课程ID"""
    lesson_no: str
    """课程编号"""
    rooms: List[Room]
    """教室信息列表"""
    start_time: str
    """上课时间，格式为HH:MM"""
    start_unit: int
    """开始节次"""
    teachclass_std_count: int
    """班级学生数量"""
    teachers: List[Teacher]
    """教师信息列表"""
    weeks: str
    """周次"""
    weekstate: str
    """周状态"""

    def dump_json(self, indent: Optional[int] = None) -> str:
        """格式化为JSON字符串"""
        return json.dumps(self.model_dump(), ensure_ascii=False, indent=indent)


class Courses(BaseModel):
    """课程列表模型"""

    courses: List[Course] = Field(default_factory=list, description="课程列表")

    def __len__(self) -> int:
        return len(self.courses)

    def __getitem__(self, index):
        return self.courses[index]

    def __iter__(self):
        return iter(self.courses)

    @classmethod
    def from_list(cls, courses_list: List[Dict[str, Any]]) -> "Courses":
        """从课程列表创建Courses对象"""
        return cls(courses=[Course(**course) for course in courses_list])

    def dump_json(self, indent: Optional[int] = None) -> str:
        """格式化为JSON字符串"""
        return json.dumps(
            [course.model_dump() for course in self.courses],
            ensure_ascii=False,
            indent=indent,
        )

    def group_by_date(self) -> Dict[str, List[Course]]:
        """按日期分组课程"""
        result = {}
        for course in self.courses:
            if course.date not in result:
                result[course.date] = []
            result[course.date].append(course)
        return result


class DeviceParams(BaseModel):
    """设备参数模型"""

    deviceName: str
    """设备名称"""
    deviceId: str
    """设备ID"""
    deviceInfo: str  
    """设备信息"""
    deviceInfos: str
    """设备详细信息"""
    userAgentPrecursor: str
    """用户代理前缀"""


class OnlineDevice(BaseModel):
    """在线设备信息模型"""

    brasid: str
    """BRAS ID"""
    downFlow: str
    """下行流量"""
    hostName: str = ""
    """主机名"""
    ip: str
    """IP地址"""
    loginTime: str
    """登录时间，格式为YYYY-MM-DD HH:MM:SS"""
    mac: str
    """MAC地址"""
    sessionId: str
    """会话ID"""
    terminalType: str
    """终端类型"""
    upFlow: str
    """上行流量"""
    useTime: str
    """使用时间（秒）"""
    userId: int
    """用户ID"""

    def dump_json(self, indent: Optional[int] = None) -> str:
        """格式化为JSON字符串"""
        return json.dumps(self.model_dump(), ensure_ascii=False, indent=indent)


class OnlineDevices(BaseModel):
    """在线设备列表模型"""

    devices: List[OnlineDevice] = Field(
        default_factory=list, description="在线设备列表"
    )

    def __len__(self) -> int:
        return len(self.devices)

    def __getitem__(self, index):
        return self.devices[index]

    def __iter__(self):
        return iter(self.devices)

    @classmethod
    def from_list(cls, devices_list: List[Dict[str, Any]]) -> "OnlineDevices":
        """从设备列表创建OnlineDevices对象"""
        return cls(devices=[OnlineDevice(**device) for device in devices_list])

    def dump_json(self, indent: Optional[int] = None) -> str:
        """格式化为JSON字符串"""
        return json.dumps(
            [device.model_dump() for device in self.devices],
            ensure_ascii=False,
            indent=indent,
        )
