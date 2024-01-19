import os
import string

# path = "\\192.168.10.105\\shares\\Marketing\\General\\9. ТЕКСТЫ\\2023\\7. PR-рассылка\\10. Октябрь\\Royal"
# path = "/Users/Morkowik/Downloads/Геохимия видео"

class Prepaths:
    lst = ["/Volumes/Shares/Marketing", ""] # from json


class PathFinderBase(object):
    def __init__(self, src_path: str):
        pre_paths = [self.normalize_path(path=i)
                    for i in Prepaths.lst]

        src_path = self.normalize_path(path=src_path)
        path_list = src_path.split(os.sep)

        self.path_versions = [
            os.path.join(pre_path, *path_list[i:])
            for pre_path in pre_paths
            for i in range(len(path_list))
            ]

        for i in self.path_versions:
            if os.path.exists(i):
                self.path = i
                return

    def normalize_path(self, path: str):
        path = path.replace("\\", os.sep).strip().strip(os.sep)
        path = path.split(os.sep)
        return os.path.join(os.sep, *path)


class NearlyPath(PathFinderBase):
    def __init__(self, src_path: str):
        PathFinderBase.__init__(self, src_path=src_path)

        if hasattr(self, "path"):
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

        for i in new_paths:
            if os.path.exists(i):
                self.nearly_path = i
                self.path = i
                return
   

class MistakeFinder(NearlyPath):
    def __init__(self, src_path: str):
        NearlyPath.__init__(self, src_path=src_path)

        if not hasattr(self, "nearly_path"):
            return
        
        improved_path = self.improve_path(src_path=src_path)

        if os.path.exists(improved_path):
            self.nearly_path = improved_path


    def improve_path(self, src_path: str):
        mistaked_tail = None
        for i in range(len(self.nearly_path)):
            if self.nearly_path[i:] in src_path:
                mistaked_tail = src_path.split(self.nearly_path[i:])[-1]
                break
        mistaked_tail = [i for i in mistaked_tail.split(os.sep) if i]

        mistake = self.normalize_name(mistaked_tail[0])

        dirs = {self.normalize_name(i): i
                for i in os.listdir(self.nearly_path)}

        if mistake in dirs:
            return os.path.join(self.nearly_path, dirs[mistake])

    def normalize_name(self, name: str):
        name, ext = os.path.splitext(p=name)
        return name.translate(str.maketrans("", "", string.punctuation + " "))


class PathFinder(MistakeFinder):
    def __init__(self, path: str):
        MistakeFinder.__init__(self, src_path=path)

    def __str__(self) -> str:
        return self.path

path = "smb://sbc01/shares/Marketing/Photo/_Collections/1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"
path = "smb://sbc01/shares/Marketing/Photo/_Collections/_____1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"

a = PathFinder(path=path)