from itertools import count
import os
from pathlib import Path

folder_path = 'chunked_data'
count = 0
with open('parquet_files_test.txt', 'r+') as data_file:
    file_paths = data_file.read()
    file_paths = file_paths.split(',')
    print(file_paths)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.parquet') and file_path not in file_paths:
                file_paths.append(file_path)
                data_file.write(file_path + ',')
                count+=1
                print(f'Added new file: {file_path}')
            else:
                print(f'File already exists: {file_path}')

with open('results_test.txt', 'w') as results_file:
    if count != 0:
        results_file.write("1\n" + str(count))
    else:
        results_file.write("0\n")