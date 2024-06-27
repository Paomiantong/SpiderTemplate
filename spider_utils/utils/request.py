import requests

PERIOD = (0, 0)


def get_proxy():
    return requests.get("http://demo.spiderpy.cn/get/?type=https").json()


class ProxyPool:
    def __init__(self, useTimes=1):
        self.useTimes = useTimes
        self.counter = 0
        self.proxy = get_proxy().get("proxy")
        pass

    def proxies(self):
        if self.counter % self.useTimes == 0:
            self.proxy = get_proxy().get("proxy")
        self.counter += 1
        return {"http": "http://{}".format(self.proxy)}


class CookiePool:

    def __init__(self, cookies):
        self.pool = [(cookie, ProxyPool.proxies()) for cookie in cookies]
        self.current_cookie_idx = -1

    def add(self, cookie):
        self.pool.append((cookie, ProxyPool.proxies()))

    @property
    def cookie(self):
        if len(self.pool) == 0:
            raise RuntimeError("Cookie Pool Is Empty!!")
        self.current_cookie_idx = (self.current_cookie_idx + 1) % len(self.pool)
        ret = self.current_cookie_idx, *self.pool[self.current_cookie_idx]
        return ret

    @property
    def period(self):
        cookies_size = len(self.pool)
        if cookies_size <= 1:
            return PERIOD
        else:
            return (PERIOD[0] / (cookies_size - 1), PERIOD[1] / (cookies_size - 1))

    def del_current_cookie(self):
        self.del_cookie(self.current_cookie_idx)

    def del_cookie(self, idx):
        if len(self.pool) == 0:
            raise RuntimeError("Cookie Pool Is Empty!!")
        print(f"Delete Cookie [{idx}]")
        del self.pool[idx]
        if self.current_cookie_idx >= idx:
            self.current_cookie_idx -= 1

    pass


class RemoteCookiePool(CookiePool):

    def __init__(self, url):
        super().__init__([])
        self.id_map = {}
        self._url = url
        self.pool = self.get_cookies()

    def get_cookies(self):
        data = requests.get(self._url).json()
        ret = []
        for idx, (key, cookie) in enumerate(data.items()):
            self.id_map[idx] = key
            ret.append((cookie, ProxyPool.proxies()))
        return ret

    def del_current_cookie(self):
        self.del_cookie(self.current_cookie_idx)

    def del_cookie(self, idx):
        if len(self.pool) == 0:
            raise RuntimeError("Cookie Pool Is Empty!!")
        print(f"Delete Cookie [{idx}]")
        del self.pool[idx]
        if self.current_cookie_idx >= idx:
            self.current_cookie_idx -= 1
        if len(self.pool) == 0:
            requests.delete(self._url)

    pass
