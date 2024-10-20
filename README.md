# ZZU.Py
<font color=gray size=3>a Python library for interacting with the Zhengzhou University (ZZU) Supwisdom Course Management Information System API.</font>

## Install

```shell
pip install zzupy --upgrade
```

## Use

Web documentation is not available at this time, please use PyCharm for a better in-development documentation experience.

## Example

```Py
from zzupy import *
import datetime


def this_monday():
    today = datetime.datetime.strptime(str(datetime.datetime.now().strftime('%Y-%m-%d')), "%Y-%m-%d")
    return datetime.datetime.strftime(today - datetime.timedelta(today.weekday()), "%Y-%m-%d")


# 设置为 True 以避免触发“建议设置设备参数”的警告。如果有能力，你也可以通过 setDeviceParams() 设置设备参数
me = ZZUPy(True)
# me.setDeviceParams()
info = me.loginByPassword("fakeusercode", "fakepassword")
print(f"{info[0]} {info[1]} 登录成功")
print("校园卡余额：", str(me.getBalance()))
print("剩余照明电费：", str(me.getRemainingPower("yourroomid")))
print("课表JSON：", me.getCoursesJson(this_monday()))
```

## License

License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)