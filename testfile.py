def test():
    a = 1
    b = 2

    for i in test.__dict__:
        print(i)


test().__dict__