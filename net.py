#!/usr/bin/env python
#coding:utf-8


from socket import *
from json import dumps,loads
from  multiprocessing import Queue
from threading_pool import Threading_pool
from struct import pack,unpack
import time,pickle
from os import system,popen
from copy import deepcopy
from log import  *
from common import *

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

#发送邮件
import  smtplib
from email.mime.text import  MIMEText

log_file = 'NET ' + time.strftime("%Y-%m-%d",time.localtime())



timeout_send = 5
#队列长度最大可以同时开启多少个线程，队列满的时候等待
queue_send_max_size = 10

#消息发送队列进程池
threading_send = Threading_pool(queue_send_max_size,timeout_send)

#重传次数
harq=4
#buf_size = 4096

class SourceAddressAdapter(HTTPAdapter):

	def __init__(self, source_address, **kwargs):
		self.source_address = source_address
		super(SourceAddressAdapter, self).__init__(**kwargs)


	"""def init_poolmanager(self, connections, maxsize, block=False):
		self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       source_address=self.source_address)"""


#data需要是json格式
def send_with_ack(addr,json_data):

	result = False
	try:
		tcp = socket(AF_INET,SOCK_STREAM)

		tcp.connect(addr)
		tcp.send(dumps(json_data).encode())
		if tcp.recv(512).decode('utf-8') == 'ACK':
			result = True

	except Exception as ex:
		print_warnning ('发送公共消息异常', ex)
	finally:
		#tcp.close()
		return result

def send_mail(json_data):
	try:
		#sender = 'yinshunyao@qq.com'
		#to = 'yinshunyao@163.com'

		sender = 'yinshunyao@163.com'
		to = 'yinshunyao@qq.com'

		#pwd='raptzgjmuvdvbhjd
		#pwd = 'iresaeneznmtbhee'
		pwd='luoyuge090213'

		msg = MIMEText(dumps(json_data))
		msg['Subject'] = '约号结果'
		msg['From'] = sender
		msg['To'] = to

		s = smtplib.SMTP_SSL('smtp.163.com',465)
		s.login(sender,pwd)
		s.sendmail(sender,to,msg.as_string())
		s.quit()
	except Exception as ex:
		counter(log_file, 'RESULT', json_data,ex)

BROADCAST_PORT = 62555
def boadcast(json_data):
	try:
		udp = socket(AF_INET, SOCK_DGRAM)
		# 超时定时器10ms时间广播出去
		udp.settimeout(0.01)
		# dumps data转换成网络数据发送格式
		udp.sendto(dumps(json_data).encode(), ('127.0.0.1',BROADCAST_PORT))

		if udp.recv(512).decode('utf-8') == 'ACK':
			return True
		else:
			return False
	except Exception as ex:
		return False


#换IP不能换得太频繁，设定换一个时间，最短5分钟换1次
def rasdial(configInfo):

	#转码成gbk
	name =  '0123456789'
	username = configInfo['net_user'].encode().decode('gbk')
	password = configInfo['net_pass'].encode().decode('gbk')



	if name == '' or username == '' or password == '':
		counter_print(log_file,'CHANGE','USERNAME_OR_PASSWORD_NULL',name,username,password)
		return True
	else:
		counter(log_file, 'CHANGE', 'NETWORK', 'START',name,username,password)

	def get_ip(name):
		#system('ipconfig > ip.temp')
		addr_data = popen('ipconfig','r')
		name_flag = False
		for line in addr_data:
			#中文windows编码以bgk方式
			ipconfig_line = line
			if name in ipconfig_line or 'PPP adapter' in ipconfig_line:
				name_flag = True

			if name_flag and ('IP Address' in ipconfig_line or 'IPv4' in ipconfig_line):
				return True, ipconfig_line.split(':')[1].strip()
		else:
			return  True,''


	name_flag,ip_addr_start = get_ip(name)
	if not name_flag:
		print_error('网络参数配置错误或者查询失败，无法更换IP')
		counter_print(log_file, 'CHANGE', 'NET_CARD_NOT_FOUND', name, username, password)
		return  False

	print_warnning('准备断开网络')
	#断开
	disconnect = "rasdial /disconnect"
	system(disconnect)

	#更换IP间隔5s，防止更换太频繁，导致IP没有改变
	time.sleep(5)

	print_warnning( '准备重新拨号')
	#重拨
	dial = "rasdial %s %s %s /PHONEBOOK:.\\config\\adsl" % (name,username,password)
	system(dial)

	name_flag,ip_addr_change = get_ip(name)
	if name_flag:
		if ip_addr_start == ip_addr_change or ip_addr_change == '':
			print_error( 'IP更换失败',ip_addr_start,ip_addr_change)
			counter(log_file, 'CHANGE', 'SUCCESS_BUT_IP_IS＿USED',ip_addr_start,ip_addr_change)
			return False
		else:
			print_success( 'IP更换成功',ip_addr_start,ip_addr_change)
			counter(log_file, 'CHANGE', 'SUCCESS', ip_addr_start,ip_addr_change)
			return True

	else:
		print_error( 'IP更换失败')
		counter(log_file, 'CHANGE', 'NEW_IP_IS_UNKNOWN',  ip_addr_start,ip_addr_change)
		return False









