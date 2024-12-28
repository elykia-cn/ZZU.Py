# ZZU.Py
<font color=gray size=3>郑州大学移动校园的 Python API 封装</font>

## 安装

```shell
pip install zzupy --upgrade
```

## Done & To Do
- [x] Supwisdom
  - [x] 获取课表
- [x] Network
  - [x] 校园网认证
- [x] eCard
  - [x] 充值电费 
  - [x] 获取校园卡余额
  - [x] 获取剩余电费

前往 [ZZU.Py Completion Plan](https://github.com/users/Illustar0/projects/1) 查看 To Do

## 文档

[文档](https://illustar0.github.io/ZZU.Py/)

## Note
[Note](https://github.com/Illustar0/ZZU.Py/blob/main/NOTE.md)

## Example

```Py
from zzupy import ZZUPy

me = ZZUPy("usercode","password")
info = me.login()
print(f"{info[0]} {info[1]} 登录成功")
print("校园卡余额：", str(me.eCard.get_balance()))
print("剩余电费：", str(me.eCard.get_remaining_power("roomid")))
print("课表JSON：", me.Supwisdom.get_courses("2024-12-09"))
```

## 许可

License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)