#!/usr/bin/env python
#coding:utf-8

from socket import *
from json import dumps,loads

#加载车牌号查询和选择进程
from car_process import query_task
#线程
#from net_threading import http_get_threading
from threading_pool import Threading_pool
#进程
from  multiprocessing import Process,Queue
#from Queue import Queue

from time import sleep
from net import sender,login_heart
import ctypes



"""
// rtn code > 0 succeed
DLLAPI int LoadModel(const char* model_path, unsigned int path_bytes);
DLLAPI int LoadModel_2(const unsigned char* model_data, unsigned int data_bytes);
DLLAPI void DestroyModel();
"""


#本地加载dll，验证码识别模块初始化
lm_dll = ctypes.CDLL("./config/lm.dll")	
#加载进来，然后生成共享的函数
model_path = ctypes.c_char_p('./config/model_4chuang_0701')
path_bytes = ctypes.c_int(len('./config/model_4chuang_0701'))
load_result = lm_dll.LoadModel(model_path,path_bytes)
#本地引用获取验证码函数
cget_yzm = lm_dll.LM_REC_2


#验证码监听进程，常驻内存
def __yzm_listen(port):
	#外层循环用于发生异常之后，自动重启监听

	#UDP端口监听
	host = ''
	addr = (host,port)

	udp = socket(AF_INET,SOCK_DGRAM)
	udp.bind(addr)

	while True:


		try:


			#udp接口监听，接收到消息立即放入队列缓存
			while True:	
				#print 'listen_task.py -> __yzm_listen: yzm is listenning'
				data,addr_src = udp.recvfrom(300*8*1024)

				result_buf = ctypes.c_char_p('')
				buf_bytes = ctypes.c_int(20)	

				cget_yzm(ctypes.c_char_p(data),ctypes.c_int(len(data)),result_buf,buf_bytes)
				#yzm = unicode( result_buf.value,'gbk').decode('utf-8')
				yzm =result_buf.value

				#print 'listen_task.py -> __yzm_listen: yzm is ' , yzm
				#udp.settimeout(2)
				udp.sendto(yzm,addr_src)

		except Exception,ex:
			print 'listen_task.py -> __yzm_listen: error ' , ex
		finally: 
			print 'listen_task.py -> __yzm_listen: reset '
			#udp.close()
			lm_dll.DestroyModel()

if __name__ == '__main__':

	#消息队列处理线程注册，线程池开启5个，实际使用3个，冗余两个
	#threading_listen = Threading_pool(5,10)

	task_list = []
	#任务管理监听
	task_list.append(Process(target=__yzm_listen,args=(62235,),name='yzm_listen'))

	def task_observer():
		for task in task_list:
			#print 'listen_task.py -> task_observer:',task.name,'alive state is',task.is_alive()
			if not task.is_alive():
				task.start()

	#守护进程，保持进程一直运行，间隔5s检测一次
	while True:
		try:
			task_observer()
		except Exception,ex:
			continue
		finally:
			sleep(10)

	print 'list_task.py -> the main task listen is error exit'
