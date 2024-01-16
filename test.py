import os

path = "smb://sbc01/shares/Marketing/Photo/_Collections/1 Solo/1 IMG/2023-09-22 11-27-28 рабочий файл.tif/"
# path = "\\192.168.10.105\\shares\\Marketing\\General\\9. ТЕКСТЫ\\2023\\7. PR-рассылка\\10. Октябрь\\Royal"

class PathFinder:
    def __init__(self, path: str):
        marketing = "/Volumes/Shares/Marketing"

        path = path.replace("\\", os.sep).strip().strip(os.sep)
        path_list = path.split(os.sep)
        path_versions = []

        for i in range(len(path_list)):
            path_versions.append(
                os.path.join(marketing, *path_list[i:])
                )

        for i in path_versions:
            if os.path.exists(i):
                print(i)
                break