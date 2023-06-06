class aa:
    def __init__(self) -> None:
        self.test = 5


class bb:
    def __init__(self):
        pass

    def change_test(self):
        self.test = 888


class cc(aa, bb):
    def __init__(self) -> None:
        aa.__init__(self)
        bb.__init__(self)



abc = cc()
abc.change_test()

print(abc.test)