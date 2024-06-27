from .ckpt import my_checkpoint


@my_checkpoint.check_point("key", "current")
def test(key, current):
    if current == 10:
        return []
    print(key, current)
    return [current + 1]


with my_checkpoint:
    data = test(key="test", current=0)
    print(data)
