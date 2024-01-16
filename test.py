import os

path = "smb://sbc01/shares/Marketing/Photo/_Collections/1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"
# path = "\\192.168.10.105\\shares\\Marketing\\General\\9. ТЕКСТЫ\\2023\\7. PR-рассылка\\10. Октябрь\\Royal"
path = "/Users/Morkowik/Downloads/Геохимия видео"


class PathFinder(object):
    def __init__(self, path: str):
        pre_paths = ["/Volumes/Shares/Marketing", ] # from json
        pre_paths = [self.normalize_path(path=i)
                    for i in pre_paths]

        path = self.normalize_path(path=path)

        path_list = path.split(os.sep)

        path_versions = (os.path.join(pre_path, *path_list[i:])
                         for pre_path in pre_paths
                         for i in range(len(path_list)))

        self.path_exists = None
        for i in path_versions:
            if os.path.exists(i):
                self.path_exists = i
                return
            
    def normalize_path(self, path: str):
        path = path.replace("\\", os.sep).strip().strip(os.sep)
        path = path.split(os.sep)
        return os.path.join(os.sep, *path)



a = PathFinder(path=path)

print(a.path_exists)