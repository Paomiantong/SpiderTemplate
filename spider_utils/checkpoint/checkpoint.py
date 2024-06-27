import json
from typing import Dict, List, Optional, Union

import inspect

from spider_utils.utils import logger, push_msg
from .checkpoint_iter import CheckPointIter
from .status_enum import EnumEncoder, PrcocessStatus


class CheckPointContext:
    _state: Dict[
        str,
        Union[Dict[str, Dict[str, int]], Dict[str, Dict[str, Union[List, int, str]]]],
    ] = {
        "state": {},
        "data": {},
    }

    def __init__(
        self,
        path: str = "checkpoint.json",
        initial_state: dict = None,
        push_on_exit: Optional[int] = None,
    ):
        self.path = path
        if initial_state is not None:
            self._state["state"] = initial_state
        self.push_on_exit = push_on_exit
        pass

    def __enter__(self):
        logger.info("加载Checkpoint")
        self.load_checkpoint()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_checkpoint()
        logger.info("保存Checkpoint")
        if exc_type is not None:
            logger.error("爬虫异常:")
            if uin := self.push_on_exit:
                push_msg(uin, "爬虫异常！")
        else:
            logger.info("爬完啦！")
            if uin := self.push_on_exit:
                push_msg(uin, "爬完啦！")

    def range(self, key, stop):
        return CheckPointIter(self._state["state"], key, stop)

    def save(self):
        self.save_checkpoint()

    def load_checkpoint(self):
        try:
            with open(self.path, "r") as f:
                self._state = json.load(f)
                for v in self._state["data"].values():
                    v["status"] = PrcocessStatus(v["status"])
        except FileNotFoundError:
            pass

    def save_checkpoint(self):
        with open(self.path, "w") as f:
            return json.dump(self._state, f, cls=EnumEncoder)

    def get_chekpoint(self, key, initValue=0):
        if not (pt := self._state["data"].get(key, None)):
            pt = {"status": PrcocessStatus.Processing, "current": initValue, "data": []}
            self._state["data"][key] = pt
        return pt

    def finish(self, key):
        self._state["data"][key]["status"] = PrcocessStatus.Finished

    def __getitem__(self, item):
        return self._state[item]

    def __setitem__(self, key, value):
        self._state[key] = value

    def check_point(ctx, keyParaName: str, currentParaName: str, inner_loop=True):
        def wrapper(func):
            params = inspect.signature(func).parameters
            assert keyParaName in params, f"{keyParaName} not in {params}"
            assert currentParaName in params, f"{currentParaName} not in {params}"

            def decorator(*args, **kvargs):
                # 获取检查点
                key = func.__name__ + str(kvargs[keyParaName])
                pt = ctx.get_chekpoint(key, kvargs.get(currentParaName, 0))
                if pt["status"] == PrcocessStatus.Finished:
                    return pt["data"]
                # 注入参数
                kvargs[currentParaName] = pt["current"]
                if "cpt" in params:
                    kvargs["cpt"] = pt
                # 提取最大行数
                if (
                    max_rows := kvargs.get("max_rows", None)
                ) and "max_rows" not in params:
                    del kvargs["max_rows"]

                ret = func(*args, **kvargs)
                status = PrcocessStatus.Processing

                if isinstance(ret, tuple):
                    assert len(ret) != 2, "invalid tuple"
                    ret, status = ret

                if ret is None:
                    logger.error(
                        f"token可能失效，或格式错误！key={key}, current={pt['current']}"
                    )
                    raise RuntimeError("token可能失效，或格式错误！")

                if len(ret) != 0:
                    pt["current"] += 1
                    pt["data"] += ret
                    rows = len(pt["data"])
                    logger.info(
                        f"[{func.__name__}]当前数据数目:{rows} current={pt['current']} max_rows={max_rows}"
                    )
                    if max_rows is not None and rows >= max_rows:
                        logger.info(f"达到最大行数，结束爬取")
                        tmp = pt["data"]
                        ctx.finish(key)
                        return tmp

                if len(ret) == 0 or status == PrcocessStatus.Finished:
                    logger.info(f"爬取结束")
                    tmp = pt["data"]
                    ctx.finish(key)
                    return tmp

            if inner_loop:

                def loop(*args, **kvargs):
                    while not (data := decorator(*args, **kvargs)):
                        pass
                    return data

                return loop
            else:
                return decorator

        return wrapper
