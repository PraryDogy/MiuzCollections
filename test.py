class Foo:
    test = 1

    def testing(self):
        print(__class__.test)


Foo().testing()