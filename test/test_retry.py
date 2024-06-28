from spider_utils.utils import retry


@retry(4)
def test_1():
    raise Exception("Error")


@retry(4, exception=RuntimeError)
def test_2():
    raise RuntimeError("Error")


@retry(4, delay=2)
def test_3():
    raise Exception("Error")


@retry(4, delay=2, exception=RuntimeError)
def test_4():
    raise Exception("Error")


try:
    test_1()
except Exception as e:
    print(e)

try:
    test_2()
except Exception as e:
    print(e)

try:
    test_3()
except Exception as e:
    print(e)

try:
    test_4()
except Exception as e:
    print(e)
