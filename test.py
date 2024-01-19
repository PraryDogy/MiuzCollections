import os


# path = "\\192.168.10.105\\shares\\Marketing\\General\\9. ТЕКСТЫ\\2023\\7. PR-рассылка\\10. Октябрь\\Royal"
# path = "/Users/Morkowik/Downloads/Геохимия видео"

class Prepaths:
    lst = ["/Volumes/Shares/Marketing", ""] # from json


class PathFinderBase(object):
    def __init__(self, path: str):
        pre_paths = [self.normalize_path(path=i)
                    for i in Prepaths.lst]

        path = self.normalize_path(path=path)
        path_list = path.split(os.sep)

        self.path_versions = [
            os.path.join(pre_path, *path_list[i:])
            for pre_path in pre_paths
            for i in range(len(path_list))
            ]

        self.path = None
        for i in self.path_versions:
            if os.path.exists(i):
                self.path = i
                return

    def normalize_path(self, path: str):
        path = path.replace("\\", os.sep).strip().strip(os.sep)
        path = path.split(os.sep)
        return os.path.join(os.sep, *path)


class NearlyPath(PathFinderBase):
    def __init__(self, path: str):
        PathFinderBase.__init__(self, path=path)

        if self.path:
            return

        new_paths = []
        for path_ver in self.path_versions:
            path_ver = path_ver.split(os.sep)
            for i in reversed(range(len(path_ver))):
                try:
                    new_paths.append(os.path.join(os.sep, *path_ver[:i]))
                except TypeError:
                    pass
        new_paths.sort(key=len, reverse=True)

        self.nearly = False
        self.path = None
        for i in new_paths:
            if os.path.exists(i):
                self.path = i
                self.nearly = True
                return
   

class MistakeFinder(NearlyPath):
    def __init__(self, path: str):
        NearlyPath.__init__(self, path=path)

        print(self.nearly)



class PathFinder(MistakeFinder):
    def __init__(self, path: str):
        MistakeFinder.__init__(self, path=path)

    def __str__(self) -> str:
        return self.path

path = "smb://sbc01/shares/Marketing/Photo/_Collections/1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"
# path = "smb://sbc01/shares/Marketing/Photo/_Collections/_____1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"

a = str(PathFinder(path=path))
