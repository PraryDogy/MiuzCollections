def debug_decorator(func):
    print("before func")

    def wrapper(*args):
        func(*args)
        print("after")

    return wrapper

@debug_decorator
def test(str):
    print(str)


test("123")