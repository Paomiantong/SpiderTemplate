import time
import jwt
import requests

SECRET_KEY = ""


def create_token(uid):
    global SECRET_KEY
    """基于jwt创建token的函数"""
    headers = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time() + 30)
    payload = {"uid": uid, "exp": exp}
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
        headers=headers,
    )  # 返回生成的token
    return token


def push_msg(uid: int, msg: str):
    requests.get(
        "http://39.106.51.185:8080/push",
        params={"msg": msg},
        headers={"X-Token": create_token(uid)},
    )
