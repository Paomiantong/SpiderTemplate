class CheckPointIter:
    def __init__(self, state, key, stop) -> None:
        self.key = key
        self.stop = stop
        assert isinstance(
            state[self.key], int
        ), f"Incompatible value type: {self.key}: {type(state[self.key])}"
        self.state = state
        self.state[self.key] -= 1
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self.state[self.key] + 1 >= self.stop:
            raise StopIteration()  # 当没有更多元素时引发StopIteration异常
        else:
            # 生成下一个元素
            self.state[self.key] += 1
            return self.state[self.key]
