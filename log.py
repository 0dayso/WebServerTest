#!/usr/bin/env python
#coding:utf-8

import time
#from common import  *

#关键信息统计
def  counter(file_name,*counter_value):

	try:

		counter_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) + ',' 

		for counter_item in counter_value:
			counter_str += str(counter_item) + ','

		else:
			counter_str = counter_str[:-1] + '\n'

		with open('./temp/' + file_name ,'a') as counter_log:
			counter_log.write(counter_str)
	except Exception as ex:
		#如果有异常，记录
		error_str = file_name + ',' + str(ex) + '\n'
		with open('./temp/error','a') as error_log:
			error_log.write(error_str)


#关键信息统计
def  counter_print(file_name,*counter_value):

	try:

		print (counter_value)

		counter_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()) + ',' 

		for counter_item in counter_value:
			counter_str += str(counter_item) + ','

		else:
			counter_str = counter_str[:-1] + '\n'

		with open('./temp/' + file_name ,'a') as counter_log:
			counter_log.write(counter_str)
		
	except Exception as ex:
		#如果有异常，记录
		error_str = file_name + ',' + str(ex) + '\n'
		with open('./temp/error','a') as error_log:
			error_log.write(error_str)

def debug_save(content, name='', mod='wb'):
	try:
		filename = './temp/' + name + ' ' +  str(time.time())
		with open(filename, mod) as file_log:
			file_log.write(content)
	except Exception as ex:
		print('保存调试日志失败',ex)
		pass


