class ZZUPyException(Exception):
    """ZZUPy项目的基类异常"""

    pass


class LoginException(ZZUPyException):
    """登录相关异常"""

    pass


class DefaultRoomException(ZZUPyException):
    """默认房间相关异常"""

    pass


class ECardTokenException(ZZUPyException):
    """校园卡 Token 相关异常"""

    pass


class PermissionException(ZZUPyException):
    """校园卡 Token 相关异常"""

    pass
