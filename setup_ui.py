#coding:utf-8

"""
window的exe程序制作
"""

from distutils.core import setup
import py2exe
from os import listdir
import  sys

#生成所有需要用到的文件
data_files = []

path_list = ["config","temp"]
for path in path_list:
	file_list = ["./" + path + '/' + file_item for file_item in  listdir( "./" + path)]

	all_file = (path,list(file_list))
	data_files.append(all_file)



setup(console=["ui.py"],data_files = data_files,zipfile=None)