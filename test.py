class Test:
    def __init__(self) -> None:
        self._abc = 000


a = Test()

if hasattr(a, "_abc"):
    print(1)