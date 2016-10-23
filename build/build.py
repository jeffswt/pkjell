
import json
import os
import pandoc
import re

""" Opens file, relative to source folder. """
def open_file(file_name, *args, **kwargs):
    return open(file_name, *args, **kwargs)

""" Reads file content, relative to source folder. """
def read_file(file_name, *args, **kwargs):
    f = open_file(file_name, *args, **kwargs)
    s = f.read()
    f.close()
    return s


""" Main function. """
def main():
    return 0

if __name__ == '__main__':
    ret_code = main()
    exit(ret_code)
