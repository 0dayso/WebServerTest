#!/usr/bin/env python
#coding:utf-8

"""
网络并发获取图片或者其他内容的一个线程池
"""
#多线程
import threading
from  multiprocessing import Queue
from log import  *

threading_log_file = 'THREAD ' + time.strftime("%Y-%m-%d",time.localtime())

#线程池
class Threading_pool(object):

	#theading_queue = Queue(20)
	#线程相关，最大线程数max_threading_size，队列满等待时间timeout
	def __init__(self,max_threading_size=0,timeout=60,daemon=True):
		self.timeout = timeout
		#为线程建立一个队列
		self.threading_queue = Queue(max_threading_size)
		self.daemeon = daemon
		self.threading_list = []

	def add(self,func,args,name='test'):
		try:
			#排队获取队列权限
			self.threading_queue.put(name,True,self.timeout)
			new_threading_item = threading_item(threading_queue=self.threading_queue,func=func,\
				args=args,name=name)
			#线程独立运行		
			new_threading_item.setDaemon(self.daemeon)

			new_threading_item.start()
			#不等待程序结束
			self.threading_list.append(new_threading_item)
			return new_threading_item
		#队列满
		except Exception as ex:
			counter_print(threading_log_file, 'THREAD', 'ADD', 'ERROR', getattr(func, '__name__'), ex)
			#pass


	def count(self):
		return self.threading_queue.qsize()


	#心跳进程
	def join_all(self):
		try:
			for index in range(0,len(self.threading_list)):
				counter_print(threading_log_file, 'THREAD', 'DOING', 'WAIT', index)
				self.threading_list[index].join()
				counter_print(threading_log_file, 'THREAD', 'FINISH', 'SUCCESS', index)
			else:
				counter_print(threading_log_file, 'THREAD', 'FINISH', 'SUCCESS', len(self.threading_list))
		except Exception as ex:
			counter_print(threading_log_file, 'THREAD', 'FINISH', 'ERROR', ex)




class threading_item(threading.Thread):

	def __init__(self,threading_queue,func,args,name):
		threading.Thread.__init__(self)
		self.func = func
		self.args = args
		self.name = name

		#线程队列
		self.threading_queue = threading_queue

	def run(self):

		try:
			self.func(*self.args)
		except Exception as ex:
			counter_print(threading_log_file,'THREAD','RUN','ERROR',getattr(self.func,'__name__'),ex)
		finally:
			#线程队列消耗，执行成功则清除一个
			self.threading_queue.get(True)



