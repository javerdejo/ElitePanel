import os

path = './'
name_list = os.listdir(path)
full_list = [os.path.join(path,i) for i in name_list]
time_sorted_list = sorted(full_list, key=os.path.getmtime)

log = [ os.path.basename(i) for i in time_sorted_list]
print log[-1]
