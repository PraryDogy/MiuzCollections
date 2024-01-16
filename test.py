import os

path = "smb://sbc01/shares/Marketing/Photo/_Collections/1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"
# path = "\\192.168.10.105\\shares\\Marketing\\General\\9. ТЕКСТЫ\\2023\\7. PR-рассылка\\10. Октябрь\\Royal"

class PathFinder(list):
    def __init__(self, path: str):
        list.__init__(self)
        pre_paths = ["/Volumes/Shares/Marketing", ] # from json

        path = path.replace("\\", os.sep).strip().strip(os.sep)
        path_list = path.split(os.sep)
        path_versions = []

        for pre_path in pre_paths:
            for i in range(len(path_list)):
                path_versions.append(os.path.join(pre_path, *path_list[i:]))

        for i in path_versions:
            if os.path.exists(i):
                self.append(i)
                break

    def __str__(self) -> str:
        try:
            return self[0]
        except Exception:
            return False

a = PathFinder(path=path)
print(str(a))