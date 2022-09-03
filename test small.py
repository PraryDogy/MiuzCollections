class One(list):
    def __init__(self):
        [self.append(i) for i in range(0, 15)]


class Two(str):
    def __init__(self):
        self.text = 'aaa'


class Test(One, Two):
    def __init__(self):
        One.__init__(self)
        print(self)

        Two.__init__(self)
        print(self)


Test()