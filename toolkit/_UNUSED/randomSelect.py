import random

def randomSelect(input_file_path, output_file_path, num_lines):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()
    random.shuffle(lines)
    # remove the selected lines from the original file
    with open(input_file_path, 'w') as file:
        file.writelines(lines[num_lines:])
    with open(output_file_path, 'w') as file:
        file.writelines(lines[:num_lines])

import os

for file in os.listdir('inputs'):
    print(file)

randomSelect('outputs/importList.txt', 'outputs/random_importList.txt', 3000)