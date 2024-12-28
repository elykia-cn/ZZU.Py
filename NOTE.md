# Note
<font color=gray size=3> 一些逆向过程的笔记</font>

### 充值电费
ZZU 的电费充值过程中对请求体进行了加密，这本没有问题，抽象的是他居然选择的是国密算法，SM2 和 SM4。  
甚至他使用的 `sm-crypto` 对于 SM2 算法的实现根本就不够规范，完全不带处理 `04` 头的，整的我懵了半天  

以下为`server/utilities/pay`中`params`的原文结构（格式化后）
```json
{
    "utilityType": "electric",
    "payCode": "06",
    "password": "XXXXX",
    "amt": "10",
    "timestamp": 233,
    "bigArea": "",
    "area": "XX",
    "building": "XX",
    "unit": "",
    "level": "XX",
    "room": "XX-XX--XX-XXX",
    "subArea": "",
    "customfield": {
    }
}
```
使用 SM2 算法 (CipherMode: C1C3C2) 对其进行加密（加密时需将其压缩），需自行删去 `04` 头，公钥由`server/auth/getEncrypt`中的`publicKey`进行 SM4 解密后得到，SM4 密钥为`773638372d392b33435f48266a655f35 (Hex)`

### Sign
树维教务的很多请求里都有个 `sign` 值，很好理解，拿来校验的嘛。然而树维教务根本不对 `sign` 值进行校验，甚至没有都没关系  
Man, what can I say?  
具体逻辑忘了，直接放 Python 实现吧
```Python
def get_sign(dynamicSecret, params):
    """
    获取sign值

    :param str dynamicSecret: login后自动获取，来自 login-token 请求
    :param str params: URL请求参数
    :return: sign值
    :rtype: str
    """
    paramsDict = {}
    for param in params.split("&"):
        if param.split("=")[0] == "timestamp":
            timestamp = param.split("=")[1]
        elif param.split("=")[0] == "random":
            random = param.split("=")[1]
        else:
            paramsDict[param.split("=")[0]] = param.split("=")[1]
    paramsDict = dict(sorted(paramsDict.items()))
    original = f"{dynamicSecret}|"
    for key in paramsDict:
        original += f"{paramsDict[key]}|"
    original += f"{timestamp}|{random}"
    sign = hashlib.md5(original.encode("utf-8")).hexdigest().upper()
    return sign
```

### 自助服务系统
先不提自助服务系统那隐藏了的、神奇的、为空的验证码，他还有个 `checkcode`。  
我一开始还以为它是哪里算出来的，最后发现其实它的值直接写在网页里了....