import os 

path = input("enter the path of the file ")
size = os.path.getsize(path)
print(size)

stats = os.stat(path)
print(stats.st_size)