class Foo:
    test = 1

    def go(self):
        setattr(self, "test", 9000)


a = Foo()
print(a.test)
a.go()
print(a.test)