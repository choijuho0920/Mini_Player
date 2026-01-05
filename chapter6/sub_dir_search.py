def search(dirname):
     print(dirname)

search("c:/CODING")
#====================================================
# # C:/doit/sub_dir_search.py
# import os

# def search(dirname):
#     filenames = os.listdir(dirname)
#     for filename in filenames:
#         full_filename = os.path.join(dirname, filename)
#         ext = os.path.splitext(full_filename)[-1]
#         if ext == '.py': 
#             print(full_filename)

# search("c:/python")

# C:/doit/sub_dir_search.py
import os

def search(dirname):
    try:
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            if os.path.isdir(full_filename):
                search(full_filename)
            else:
                ext = os.path.splitext(full_filename)[-1]
                if ext == '.py': 
                    print(full_filename)
    except PermissionError:
        pass

search("c:/CODING")

#============================================================================
#하위 디렉터리 검색을 쉽게 해 주는 os.walk

# oswalk.py
import os

for (path, dir, files) in os.walk("c:/python"):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        if ext == '.py':
            print("%s/%s" % (path, filename))
        


