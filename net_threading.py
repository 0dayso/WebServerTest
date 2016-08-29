#!/usr/bin/env python
#coding:utf-8

"""
网络并发获取图片或者其他内容的一个线程池
"""
#多线程
import threading


class http_get_threading(threading.Thread):
	status = ''
	body = ''

	def __init__(self,func,args,name=''):
		threading.Thread.__init__(self)
		self.func = func
		self.args = args
		self.name = name


	def run(self):
		self.status,self.body = apply(self.func,self.args)

	def get_result(self):
		return self.status,self.body

