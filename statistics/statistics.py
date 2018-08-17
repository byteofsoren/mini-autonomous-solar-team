#!/usr/bin/env python
import numpy as np
import os

def read_data(file_name, search, column, data_delimiter=",", ros_delimmiter='='):
    """TODO: Docstring for read_data.

    :file_name: The filename to search
    :search: search the file for this string
    :returns: a np.array()

    """
    numbers = ["0", "1","2","3","4","5","6","7","8","9","0",".", data_delimiter]
    if os.path.isfile(file_name):
        fh = open(file_name, "r")
        data_lines = list()
        for line in fh:
            if search in line:
                counter = column
                s = ""
                for char in line[::-1]:
                    if (char in numbers) and (counter < 0):
                        s += char
                    counter += 1

                data_lines.append(s[::-1])
        print(data_lines[0:40])
        fh.close()
    else:
        print("file {f} not found".format(f=file_name))



if __name__ == "__main__":
    ar = read_data("/home/nvidia/.ros/log/tx2_mani.py_13934_1534249595527.log", "ros_labview", 2)


