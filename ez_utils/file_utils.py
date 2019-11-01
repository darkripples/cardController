# coding:utf8
""" Some Func About 'file' """
# 2019/5/18

import os, glob

def read_in_chunks(file_path: str, chunk_size=1024 * 1024):
    """
    Lazy function (generator) to read a file piece by piece.
    """
    file_object = open(file_path, 'rb')
    while True:
        chunk_data = file_object.read(chunk_size)
        if not chunk_data:
            break
        yield chunk_data

def walk_dir(file_path: str, include_dir = True):
    """
    loop dir
    """
    ret = []
    for root, dirs, files in os.walk(file_path, topdown=True):
        for name in files:
            # 文件
            ret.append(os.path.join(root, name))
        if include_dir:
            for name in dirs:
                # 文件夹
                ret.append(os.path.join(root, name))
    return ret

def glob_dir(file_path: str):
    """
    loop file
    """
    
    return glob.glob(file_path)

def help(num='①'):
    print(num + "关于文件操作")
    print("\t" + read_in_chunks.__doc__)

