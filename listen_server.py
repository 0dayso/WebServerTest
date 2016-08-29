#!/usr/bin/env python
#coding:utf-8


#网络请求处理
from socket import *
#from socketserver import TCPServer, BaseRequestHandler
from json import dumps,loads
import ctypes
import threading
#from net_threading import http_get_threading
#进程
from  multiprocessing import Process,Queue,freeze_support,Manager
from threading_pool import Threading_pool
#from time import sleep,time
import time
import os
import pickle

from struct import pack,unpack
from user import *
from net import send_with_ack
from log import counter,counter_print
from common import *

import encodings.idna
import  message

yzmfx_log  = 'yzm ' + time.strftime("%Y-%m-%d",time.localtime())



host = ''

#车牌号保存地址
plate_path = './plate/'
login_path = './login/'


server_log = 'SERVER '  +  time.strftime("%Y-%m-%d",time.localtime())
password = 'afdjiajfoeijieojiffoa87712121'
config_path = './config/'
type_user = '.user'
login_path = './login/'




def __send_to_local__(json_data):
	result = False
	try:
		tcp = socket(AF_INET, SOCK_STREAM)
		tcp.settimeout(0.5)
		tcp.connect(('127.0.0.1',61234))
		tcp.send(dumps(json_data).encode())
		if tcp.recv(512).decode('utf-8') == 'ACK':
			result = True
	except Exception as ex:
		counter(server_log,'SEND_LOCAL','ERROR',ex)
	finally:
		return result

def __send_data_to_local__(data):
	result = False
	try:
		tcp = socket(AF_INET, SOCK_STREAM)
		tcp.settimeout(0.5)
		tcp.connect(('127.0.0.1', 61234))
		tcp.send(data)
		if tcp.recv(512).decode('utf-8') == 'ACK':
			result = True
	except Exception as ex:
		counter(server_log, 'SEND_LOCAL', 'ERROR', ex)
	finally:
		return result









#客户端登录TCP长连接场景
class __client__():

	#构造函数
	def __init__(self,queue_in,queue_out,hostname,user_type, addr_client):
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.hostname = hostname
		self.user_type = user_type
		self.addr_client = addr_client

		self.online = False
		#运行状态正常，False需要退出相关循环
		self.run_enable = True

		manager = Manager()
		self.queue_to_client = manager.Queue(100)
		self.queue_from_client = manager.Queue(100)


	#控制中心消息转发给客户端
	def __manager_msg__(self):
		while True:
			try:

				data = self.queue_in.get(True)
				#print_debug('接收到 发送到客户端的队列消息',data[:20])

				if data[:20] == message.HEADER_HEART:
					try:
						json_data = message.msg_decode(data,message.HEADER_HEART)
						if not json_data:
							continue

						self.addr_client =  tuple(json_data['user_info'].get('addr_client'))#(json_data['user_info'].get('addr_client'),json_data['user_info'].get('client_port'))
						print_success('客户端信息信息更新成功',self.hostname,self.addr_client)
						# 本地端口也发送给对端
						self.__send_server_port__()

					except Exception as ex:
						print_warnning('客户端进程处理登录消息异常',ex)

					continue

				if not self.online:
					continue

				self.queue_to_client.put(data,True,1)
			except Exception as ex:
				print_error('客户端进程处理管理进程消息异常',ex)
				counter(server_log,'客户端进程处理管理进程消息异常', ex)


	def start(self):

		if self.__udp_init__():
			print_infor('01 客户端资源初始化成功',self.hostname)


		print_infor('02 客户端监听线程启动',self.hostname)
		recv = threading.Thread(target=self.__udp_recv__)
		recv.start()
		time.sleep(0.1)




		print_infor('04 客户端信箱线程启动', self.hostname)
		# 发送给用户的消息监听线程
		manager_msg_handle = threading.Thread(target=self.__manager_msg__)
		manager_msg_handle.start()

		print_infor('05 客户端消息处理线程启动', self.hostname)
		# 登录成功之后实体监听
		listen_client = threading.Thread(target=self.__listen_client__)
		listen_client.start()

		print_infor('06 客户端发送线程启动', self.hostname)
		send = threading.Thread(target=self.__udp_send__)
		send.start()

		if self.__send_server_port__():
			print_infor('03 客户端通信成功',self.hostname)
		else:
			print_error('03 客户端通信失败', self.hostname)

		listen_client.join()
		recv.join()
		send.join()
		manager_msg_handle.join()

		print_error('客户端进程异常退出')







	def __udp_init__(self):
		while True:
			try:
				self.udp_recv = socket(AF_INET, SOCK_DGRAM)
				self.udp_send = socket(AF_INET, SOCK_DGRAM)

				self.udp_send.settimeout(5)


				self.udp_recv.bind(('', 0))
				self.server_recv_port = self.udp_recv.getsockname()[1]

				#心跳消息编码
				self.heart = message.msg_encode( {
					'task_type': 'login',
					'handle_type': 'response',
					'user_info': {
						'result': 'success',
						'hostname':self.hostname,
						'server_recv_port': self.server_recv_port,
					}
				},message.HEADER_HEART)

				#print_success('01.客户端资源初始化成功',self.hostname)
				return True

			except Exception as ex:
				print_error('用户端口初始化异常',self.hostname,ex)
				continue



	#服务器端口发送给客户端，直到发送成功为止，期间置客户端离线状态
	def __send_server_port__(self):
		# 上下行端口发送给服务器，上线之后就不发送了
		print_infor('通知客户端分配资源',self.hostname)
		try:
			udp = socket(AF_INET, SOCK_DGRAM)
			udp.settimeout(1)
			udp.sendto(self.heart, self.addr_client)
			data = udp.recv(512)
			if data.decode() == 'ACK':
				print_success('客户端在现状态检查成功',self.hostname)
				time.sleep(0.2)
				self.__online__()
				return True
			else:
				print_warnning('客户端在线状态检查失败', self.hostname, data.decode())
				time.sleep(0.2)
				self.__offline__()
				return False

		except Exception as ex:
			print_warnning('客户端状态异常',self.hostname,self.addr_client, ex)
			time.sleep(0.2)
			self.__offline__()
			return False

	# 监听
	def __udp_recv__(self):

		print_success('服务器端接收进程启动',self.hostname,self.server_recv_port)
		while True:
			try:
				# 验证码图片有300k吧
				data,addr_client = self.udp_recv.recvfrom(300 * 1024)

				try:
					self.udp_recv.sendto('ACK'.encode(),addr_client)
				except Exception as ex:
					print_error('服务器接收进程响应ACK异常',self.hostname, ex)


				# 心跳消息，客户端软件重启等场景下，IP和端口可能需要更新
				if data[:20] == message.HEADER_HEART:
					try:
						json_data = message.msg_decode(data,message.HEADER_HEART)
						if not json_data:
							continue

						#主要是更新IP
						self.addr_client = addr_client
						self.__send_server_port__()
						continue
					except Exception as ex:
						print_warnning('客户端进程处理登录消息异常',ex)

					continue

				# 如果IP变化，直接更新
				elif addr_client[0] != self.addr_client[0]:
					self.addr_client = (addr_client[0],self.addr_client[1])

				# 所有消息透传到处理进程
				self.queue_from_client.put(data, True, 3)

			#服务器保持端口监听，不下线
			except Exception as ex:
				counter(server_log, 'ERROR_RECV', self.hostname, ex)
				print_warnning('客户端接收进程异常',self.hostname,ex)
				time.sleep(2)
				continue

	#udp发送
	def __udp_send__(self):

		self.udp_send.settimeout(1)
		while True:
			try:
				# 透传给用户,10秒发送一次心跳
				json_data = self.queue_to_client.get(True, 20)
			except Exception as ex:
				data = self.heart
			else:
				# JSON格式编码
				try:
					data = dumps(json_data).encode()
				# 非JSON格式的直接转发
				except:
					data = json_data


			#不在线状态下不发送
			if not self.online:
				continue

			count = 0
			while count < 3:
				count += 1

				try:
					self.udp_send.sendto(data,self.addr_client)
				except Exception as ex:
					#print_warnning('发送消息到客户端失败，可能已经掉线',self.hostname,self.addr_client)
					#self.__send_server_port__()
					continue

				try:
					if self.udp_send.recv(512).decode() == 'ACK':
						break
					#有可能对方解析错误等原因
					else:
						continue

				except Exception as ex:
					counter(server_log, 'SEND', 'ERROR_SEND_ACK', self.hostname, self.addr_client, ex)
					#self.__send_server_port__()
					#print_warnning('客户端实体发送进程处理异常', self.hostname, self.addr_client, ex)
					continue
			else:
				counter(server_log, 'SEND', 'SEND_FAIL', self.hostname, self.addr_client, ex)

	#下线
	def __offline__(self):

		self.online = False

		try:

			#不是UI，实体均需要更新状态
			#if self.user_type != client.UI.value:
			json_offline = {
				'task_type':'host',
				'handle_type':'update',
				'user_info':{
					'hostname':self.hostname,'status':'offline',
				},
			}

			try:
				__send_to_local__(json_offline)
			except Exception as ex:
				counter(server_log,'CLIENT','OFFLINE_QUEUE_PUT_ERROR',self.hostname,ex)

		except Exception as ex:
			counter(server_log,'CLIENT','OFFLINE_ERROR','ERROR',self.hostname,ex)
			print_warnning('客户端实体离线异常',self.hostname,ex)

	# 上线
	def __online__(self):

		self.online = True

		try:

			# 不是UI，实体均需要更新状态
			# if self.user_type != client.UI.value:
			json_online = {
				'task_type': 'host',
				'handle_type': 'update',
				'user_info': {
					'hostname': self.hostname, 'status': 'online',
				},
			}

			try:
				__send_to_local__(json_online)
			except Exception as ex:
				counter(server_log, 'CLIENT', 'OFFLINE_QUEUE_PUT_ERROR', self.hostname, ex)

		except Exception as ex:
			counter(server_log, 'CLIENT', 'OFFLINE_ERROR', 'ERROR', self.hostname, ex)
			print_warnning('客户端实体离线异常', self.hostname, ex)

	# 监听客户端实体发送过来的信息
	def __listen_client__(self):

		while True:
			try:
				data_from_net = self.queue_from_client.get(True)

				# 验证码图片，不进行json解码
				if data_from_net[0:20] == b'0' * 20:
					self.__yzm_transfer__(data_from_net)
					continue
				else:
					try:
						json_data = loads(data_from_net.decode())
					except Exception as ex:
						print_error('解析非验证码数据异常', self.hostname, data_from_net[:20] ,ex)
						continue

				task_type = json_data.get('task_type', '')
				handle_type = json_data.get('handle_type', '')
				# user_type分三种，一种是client (client_query和client_select是只支持查询或者约号的客户端)，一种是ui，一种是服务器本地创建的任务
				print_infor('客户端任务请求', task_type, handle_type)

				if 'user_info' in json_data.keys():
					if 'user_type' in json_data['user_info'].keys():
						user_type = json_data['user_info'].get('user_type')
					else:
						user_type = 'local'
				else:
					user_type = 'local'

			except Exception as ex:
				counter(server_log, '__listen_client__: error', ex)
				print_error('客户端消息解析异常', self.hostname, ex)
				continue

			try:

				# 客户端实体在线信息处理
				if task_type == 'login':

					self.__login__handle__(json_data)

				# 约号用户操作，主要是界面发送过来的任务请求
				elif task_type == 'user':
					self.__user_handle__(json_data)

				# 验证码，主要是select用户的验证码远程监控对错
				elif task_type == 'yzm':
					self.__yzm_handle__(json_data)

				#如果是UI请求，一般是查询host列表
				elif task_type == 'host':
					json_data['hostname'] = self.hostname
					__send_to_local__(json_data)

				# 触发select用户重新登录等信息
				elif task_type == 'select':
					#self.__send_select__(json_data)
					__send_to_local__(json_data)
				else:
					print_warnning('未知的任务类型', task_type, handle_type)

			except Exception as ex:
				counter(server_log, 'ClIENT','LISTEN_CLIENT_ERROR',self.hostname, ex)
				print_error('客户端实体监听进程异常', self.hostname, ex)


	#登录处理函数
	def __login__handle__(self,json_data):
		task_type = json_data.get('task_type', '')
		handle_type = json_data.get('handle_type', '')
		user_type = json_data['user_info'].get('user_type','')

		json_response = {
			'task_type': task_type,
			'handle_type': 'response',
			'user_info': '',
		}

		# 下线操作
		if handle_type == 'offline':
			try:
				# 下线记录
				self.__offline__()
			except Exception as ex:
				counter(server_log, 'CLIENT', 'LOGIN_HANDLE_OFFLINE_ERROR', ex)
				print_error('下线异常', self.hostname,ex)
			return

		# 上线和心跳操作
		# 根据心跳时间更新，需要广播出去
		elif handle_type == 'heart':
			self.time = json_data['user_info']['time']
			# 客户端实体心跳信息，可以广播出去，也可以不广播
			# 目前广播一下，保证状态同步正常，后续优化
			if user_type != client.UI.value:
				__send_to_local__(json_data)
		else:
			pass




	#select用户资料相关处理
	def __user_handle__(self,json_data):


		task_type = json_data.get('task_type', '')
		handle_type = json_data.get('handle_type', '')
		user_type = json_data['user_info'].get('user_type', '')

		json_response = {
			'task_type': task_type,
			'handle_type': 'response',
			'user_info': '',
		}

		# 查询用户列表
		if handle_type == 'all' or handle_type == 'running' or handle_type == 'idle' or \
						handle_type == 'success':

			users = get_user_list(handle_type)

			json_response['handle_type'] = 'list'
			json_response['user_info'] = users

			self.queue_to_client.put(json_response,True,1)
			counter(server_log, 'CLIENT', 'GET', 'USERS', handle_type)
			print_infor('UI请求查询用户信息', handle_type)

		# 删除用户行为，广播给所有客户端
		elif handle_type == 'delete':

			result = save_user_info(json_data.get('user_info'), handle='delete')

			json_response['handle_type'] = 'delete'
			json_response['user_info'] = {
				'clsbdh': json_data['user_info'].get('clsbdh'),
			}

			self.queue_to_client.put(json_response, True, 1)
			counter(server_log, 'CLIENT', task_type, handle_type, 'DELETE',
					json_data['user_info'].get('clsbdh'))
			print_infor('UI请求删除用户信息', json_data['user_info'].get('clsbdh'))

		# 单个用户信息更新
		elif handle_type == 'update':

			result = save_user_info(json_data.get('user_info'), handle='update')
			if not result:
				pass

			json_response['handle_type'] = 'update'
			json_response['user_info'] = get_user_info(json_data['user_info'].get('clsbdh'))

			# 约号用户信息更新，需要广播给所有UI
			json_response['user_type'] = client.UI.value
			__send_to_local__(json_response)

			counter(server_log, 'CLIENT', task_type, handle_type, 'UPDATE',
					json_data['user_info'].get('clsbdh'))
			print_infor('UI请求更新用户信息', json_data['user_info'].get('clsbdh'))



		# 启动或者停止任务
		elif handle_type == 'start' or handle_type == 'stop':

			counter(server_log, 'CLIENT', 'USER', handle_type,
					json_data['user_info'].get('clsbdh'))
			print_infor('UI请求改变任务状态', json_data['user_info'].get('clsbdh'), handle_type)

			json_data['user_info']['status'] = 'running'

			if handle_type == 'start':
				status = 'running'
			elif handle_type == 'stop':
				status = 'idle'
			else:
				counter(server_log, 'UILISTEN', 'FAIL_TYPE', task_type, handle_type,
						json_data['user_info'].get('clsbdh'))
				print_warnning('UI任务操作的类型不对', json_data['user_info'].get('clsbdh'), handle_type)
				status = ''

			if status != '':
				json_handle = {
					'clsbdh': json_data['user_info']['clsbdh'],
					'status': status,
				}

				result = save_user_info(json_handle, handle=handle_type)
				if result:
					json_response['handle_type'] = 'update'
					json_response['user_info'] = {
						'clsbdh': json_data['user_info']['clsbdh'],
						'status': status,
					}

					#发送给实体
					result['user_type'] = client.CLIENT.value
					__send_to_local__(result)

					#发送给UI
					json_response['user_type'] = client.UI.value
					__send_to_local__(json_response)
		else:
			pass

	#验证码图片流透传
	def __yzm_transfer__(self,data):
		if data[0:20] == b'0'*20:
			__send_data_to_local__(data)
			return

	# select用户资料相关处理
	def __yzm_handle__(self, json_data):

		task_type = json_data.get('task_type', '')
		handle_type = json_data.get('handle_type', '')
		user_type = json_data['user_info'].get('user_type', '')

		json_response = {
			'task_type': task_type,
			'handle_type': 'response',
			'user_info': '',
		}

		# change代码验证码需要更新直接发送给select用户
		#需要携带hostname
		if handle_type == 'change':
			clsbdh = json_data['user_info'].get('clsbdh','')
			user_info = get_user_info(clsbdh)
			hostname_select =  user_info.get('hostname')

			#查找select用户运行的hostname
			json_data['hostname'] = hostname_select
			__send_to_local__(json_data)
		else:
			print_warnning('未知的任务类型', task_type, handle_type)



#客户端监听程序启动
def __client_start__(queue_in,queue_out,hostname,user_type, addr_client):
	client = __client__(queue_in,queue_out,hostname,user_type,addr_client)
	client.start()

#客户端管理，每个客户端都需要建立进程，这样客户端之间就不受影响
class __client_manager__():

	def __init__(self,port,queue_transfer,queue_data):
		#端口信息
		self.port = port

		#中转消息处理
		self.queue_transfer = queue_transfer
		#中转消息处理，目前主要是验证码，码流格式
		self.queue_data = queue_data
		#客户端信息
		self.hosts = {}

	def __offline__(self,hostname):
		if hostname in self.hosts.keys():
			try:
				self.hosts[hostname]['queue_in'].close()
			except Exception as ex:
				pass

			try:
				self.hosts[hostname]['queue_out'].close()
			except Exception as ex:
				pass


			try:
				#直接杀死进程
				self.hosts[hostname]['listen'].terminate()
				counter(server_log, 'OFFLINE', 'SUCCESS', hostname)
			except Exception as ex:
				counter(server_log,'OFFLINE','ERROR',hostname,ex)

	# 广播消息或者单播消息
	def __send__(self, json_data, hostname=None):

		count = 0
		if hostname in self.hosts.keys():
			try:
				#离线客户端不发送数据
				if self.hosts[hostname].get('status') != 'online':
					return

				self.hosts[hostname]['queue_in'].put(json_data)
				count += 1
			except Exception as ex:
				counter(server_log,'SEND','ERROR',hostname,ex)
		elif hostname is None:
			for hostname_send in self.hosts.keys():
				try:

					# 离线客户端不发送数据
					if self.hosts[hostname_send].get('status') != 'online':
						continue

					self.hosts[hostname_send]['queue_in'].put(json_data)
					count += 1
				except Exception as ex:
					counter(server_log, 'SEND', 'ERROR', hostname_send, ex)
					continue
		else:
			pass

		counter(server_log, 'SEND', 'SUCCESS', count)

	def __send_type__(self,json_data,user_type):
		count = 0
		for hostname_send in self.hosts.keys():
			try:
				if user_type == self.hosts[hostname_send].get('user_type','') and \
					self.hosts[hostname_send].get('status') == 'online':

					self.hosts[hostname_send]['queue_in'].put(json_data)
					count += 1
			except Exception as ex:
				counter(server_log, 'SEND', 'ERROR', hostname_send, ex)
				continue
		else:
			counter(server_log,'SEND_TYPE','SUCCESS',count)

	# 客户端实体和UI都使用该接口登录，任务分发，UDP方式登录为好
	def __login_handle__(self):

		try:
			udp = socket(AF_INET, SOCK_DGRAM)
			print_success('服务器客户端管理进程启动', self.port)
			udp.bind(('', self.port))
		except Exception as ex:
			print_error('服务器客户端管理进程启动异常，请重启',self.port)
			return

		while True:
			try:
				data, addr_client = udp.recvfrom(5*1024)
				udp.sendto('ACK'.encode(),addr_client)

			except Exception as ex:
				counter(server_log,'CLIENT_MANAGER', 'RECV_DATA', 'ERROR', ex)

			try:
				json_data = message.msg_decode(data, message.HEADER_HEART)
				if not json_data:
					counter(server_log, 'CLIENT_MANAGER', 'LOAD_DATA', 'FAIL', data[:20])
					print_warnning('服务器客户端管理进程接收到异常消息',data[0:20])
					continue

				hostname = json_data['user_info'].get('hostname', '')
				user_type = json_data['user_info'].get('user_type', '')
			except Exception as ex:
				counter(server_log, 'CLIENT_MANAGER', 'LOAD_DATA', 'ERROR', ex)
				continue


			#实体已经创立
			if hostname in self.hosts:
				try:
					#IP添加进去
					json_data['user_info']['addr_client'] = addr_client
					self.hosts[hostname]['queue_in'].put(message.msg_encode(json_data,message.HEADER_HEART))
					print_infor('客户端更新', hostname, user_type, addr_client )

				except Exception as ex:
					print_error('客户端更新异常',hostname,ex)
					counter(server_log, 'CLIENT_MANAGER', 'LOGIN_REFRESH_ERROR', hostname, ex)

			#新建实体
			else:

				# 保存客户端登录信息
				self.hosts[hostname] = {
					'hostname': hostname,
					'user_type': user_type,
					'queue_in':Queue(100),	#输入队列
					'queue_out':Queue(100), #输出队列
					'status':'offline',
					'cxtj':''
				}


				try:
					self.hosts[hostname]['listen'] = Process(target=__client_start__,
						  args=(self.hosts[hostname]['queue_in'],self.hosts[hostname]['queue_out'],
								hostname,user_type,addr_client,))

					self.hosts[hostname]['listen'].start()

					print_infor('客户端登录',hostname,user_type,addr_client)
					#counter(server_log, 'CLIENT_MANAGER', 'LOGIN', hostname,user_type,addr_client)
				except Exception as ex:
					print_infor('客户端登录异常', hostname, ex)
					counter(server_log, 'CLIENT_MANAGER', 'LOGIN', hostname, ex)

				if user_type != client.UI.value:
					try:
						# 广播给所有的UI更新状态
						self.__send_type__(message.msg_encode(json_data, message.HEADER_NULL), client.UI.value)
					except Exception as ex:
						print_warnning('客户端登录状态通知到UI界面发生异常，可能会影响任务管理',ex)



	#客户端中间中转消息,不进行复杂处理，保证运行速度
	def __transfer__(self):
		while True:
			try:
				json_data = self.queue_transfer.get(True)
			except Exception as ex:
				print_error('中转进程获取消息失败')
				counter(server_log,'TRANSFER','GET_ERROR',ex)
			else:
				print_infor('中转进程有消息需要处理')

			try:
				task_type = json_data.get('task_type')
				handle_type = json_data.get('handle_type')
				user_type = json_data.get('user_type')
				hostname = json_data.get('hostname')

				#host在线状态，唯一需要客户端管理模块处理的消息
				if task_type == 'host':
					if handle_type == 'query':
						print_debug('host查询消息',hostname)
						json_send = self.__get_hosts__()
						self.__send__(dumps(json_send).encode(),hostname)

					#更新本地保存信息,一般都是只有一个客户端
					elif handle_type == 'update':
						try:
							host_data = json_data.get('user_info')
							if 'hostname' in host_data:

								hostname_temp = host_data['hostname']
								if 'status' in host_data:
									self.hosts[hostname_temp]['status'] = host_data['status']

								if 'cxtj' in host_data:
									self.hosts[hostname_temp]['cxtj'] = host_data['cxtj']

								if self.hosts[hostname_temp].get('user_type') != client.UI.value:
									# 广播给UI
									self.__send_type__(dumps(json_data).encode(), client.UI.value)

						except Exception as ex:
							print_warnning('服务器更新客户端信息存在问题')
							pass




				#按照用户类型广播
				elif 'user_type' in json_data:
					self.__send_type__(dumps(json_data).encode(), user_type)

				#按照客户端名称单播
				elif 'hostname' in json_data:
					self.__send__(dumps(json_data).encode(),json_data['hostname'])

				#广播给所有用户
				else:
					self.__send__(dumps(json_data).encode())

			except Exception as ex:
				counter(server_log,'TRANSFER','SEND_ERROR',ex)
				print_error('服务器中转消息失败')

	#基本上透传消息，非Json数据格式的消息
	def __transer_data__(self):
		while True:
			try:
				#发送给所有的客户端，后续优化
				data = self.queue_data.get(True)
				#验证码发送给所有UI客户端
				if data[0:20] == b'0'* 20:
					self.__send_type__(data,client.UI.value)
				else:
					pass
			except Exception as ex:
				print_error('服务器中转数据失败')


	def __get_hosts__(self):

		json_response = {
			'task_type': host,
			'handle_type': 'response',
			'user_info': {},
		}

		for item in self.hosts:
			user_type_host = self.hosts[item].get('user_type')
			if user_type_host != client.UI.value:
				status = self.hosts[item].get('status', '')
				hostname_pc = self.hosts[item].get('hostname', '')
				json_response['user_info'][hostname_pc] = {
					'hostname': status,
					'status':hostname_pc
				}

		return json_response


	#启动进程
	def start(self):
		try:
			transfer = threading.Thread(target=self.__transfer__)
			transfer.setDaemon(True)
			transfer.start()

			transfer_data = threading.Thread(target=self.__transer_data__)
			transfer_data.setDaemon(True)
			transfer_data.start()

			login_handle = threading.Thread(target=self.__login_handle__)
			login_handle.setDaemon(True)
			login_handle.start()

			login_handle.join()
			transfer.join()
		except Exception as ex:
			print_error('客户端管理进程异常',ex)
			counter(server_log,'CLIENT_MANAGER_START_ERROR',ex)




def __client_manager_start__(port,queue_transfer,queue_data):
	cient_manager = __client_manager__(port,queue_transfer,queue_data)
	cient_manager.start()

def __msg_handle__(queue_from_net,queue_transfer):
	# 启动的时候加载文件列表
	print_success('公共消息处理进程启动成功')
	counter(server_log, 'MSG_MANAGER', 'MSG_HANDLE', 'SUCCESS')
	while True:
		try:

			json_data = queue_from_net.get(True)

			task_type = json_data.get('task_type')
			handle_type = json_data.get('handle_type')


			# 如果选好成功，刷新
			if task_type == 'order':
				# 号牌选择成功
				if handle_type == 'response':
					# 约号成功消息处理
					if json_data['user_info']['result'] == 'success':
						config_temp = {
							'clsbdh': json_data['user_info']['clsbdh'],
							'xzhm': json_data['user_info']['xzhm'],
							# 'yxzt':'1',
							'status': 'success',
						}
					# 其他场景未定义
					else:
						continue

					counter(server_log, 'XZHM', json_data['user_info']['clsbdh'],
							json_data['user_info']['xzhm'])
					print_success('约号成功', '用户', json_data['user_info']['clsbdh'], '号码',
								  json_data['user_info']['xzhm'])

					# 保存配置，发送失败怎么办？
					result = save_user_info(config_temp, handle='success')

					# 直接广播停止的消息
					json_offline = {
						'task_type': 'select',
						'handle_type': 'stop',
						'user_info': {
							'clsbdh': json_data['user_info']['clsbdh'],
							'xzhm':json_data['user_info']['xzhm']
						}
					}

					#通知到所有客户端
					queue_transfer.put(json_offline,True,0.1)

				# 记录已经查询到的号牌信息并存档
				elif json_data['handle_type'] == 'report':

					# 分割xzhm
					xzhm = json_data['user_info']['xzhm']

					xzhm_list = []

					xzhm_item = xzhm[:5]
					while xzhm_item != '':
						if not xzhm_item in xzhm_list:
							xzhm_list.append(xzhm_item)

						xzhm = xzhm[5:]
						xzhm_item = xzhm[:5]

					# 记录到当天的结果里面，按照日期归档
					plate_name = time.strftime("%Y-%m-%d", time.localtime())

					# 持久化存档，以车牌号的名称命名，文件操作太频繁了
					with open(plate_path + plate_name, 'a') as fileTemp:
						fileTemp.write(',' + ','.join(xzhm_list))
						fileTemp.close()

				else:
					pass

			# query或者select用户类消息直接转发给hostname电脑或者广播
			# 这个是
			elif task_type == 'query' or task_type == 'select':
				try:
					json_task = deepcopy(json_data)
					queue_transfer.put(json_task,True,0.1)
				except Exception as ex:
					counter(server_log,'MSG_HANDLE','QUERY_OR_SELECT_ERROR',ex)
					print_error('公共消息进程处理实体任务异常',ex)

			#日志消息
			elif task_type == 'log':
				if handle_type == 'report':
					json_log = deepcopy(json_data)
					json_log['user_type'] =  client.UI.value
					queue_transfer.put(json_log,True,0.1)
				else:
					print_error('无法识别的日志类型', task_type, handle_type)
			else:
				try:
					queue_transfer.put(json_data,True,0.1)
				except Exception as ex:
					print_error('公共消息进程到客户端管理进程转发异常',ex)

		except Exception as ex:
			print_error('开放接口消息处理异常', ex)
			counter(server_log, 'MSG_HANDLE', 'ERROR', ex)


# 消息监听进程,速度更快，多开一个端口，避免占用
def __msg_listen__(port, queue_from_net,queue_data):
	try:
		tcp = socket(AF_INET, SOCK_STREAM)
		addr = ('', port)
		tcp.bind(addr)
		tcp.listen(5)
	except Exception as ex:
		print_error('无连接开放监听进程启动异常',ex)
		counter(server_log,'LISTEN_MSG','ERROR',ex)

	print_success('无连接开放监听进程启动成功', port)
	while True:
		try:
			counter(server_log, 'LISTEN_MSG', 'RUNNING', port)
			tcp_pip, addr = tcp.accept()
			data = tcp_pip.recv(300 * 1024)

			#验证码，直接发送给客户端管理进程
			if data[0:20] == b'0' * 20:
				queue_data.put(data,True,0.1)
				continue

			tcp_pip.send('ACK'.encode())
			# json解析
			json_data = loads(data.decode())

			# 接收到的数据放入队列缓存
			queue_from_net.put(json_data, True, 0.5)

		except Exception as ex:
			counter(server_log, 'LISTEN_MSG', 'ERROR', ex)
			print_error('无连接开放监听进程运行异常', ex)
		finally:
			pass

# UDP监听，主要针对select用户直接传递给服务器的信息处理，包括上线和成功选中号牌的通知
def __select_listen__(port,queue_transfer):

	udp = socket(AF_INET, SOCK_DGRAM)
	addr = ('', port)  #61237
	udp.bind(addr)
	print_success('约号用户登录监控线程启动成功', port)
	select_users = {}
	#10s超时，不能设置太长

	while True:
		try:
			#阻塞模式
			udp.settimeout(None)
			# 约号用户打洞地址
			try:
				data, addr_src = udp.recvfrom(10 * 1024)
				json_data = loads(data.decode('utf-8'))
			except Exception as ex:
				print_error('解析约号用户登录消息异常')
				counter(server_log,'SELECT_LISTEN','LOAD_MSG_ERROR',ex)

			udp.settimeout(10)
			# select用户上线
			if json_data.get('task_type') == 'login' and json_data.get('handle_type') == 'online':

				json_response = {
					'task_type': 'login',
					'handle_type': 'response',
					'user_info': 'fail',
				}

				#clsbdh为空
				clsbdh = json_data['user_info'].get('clsbdh', '')
				if clsbdh == '':
					json_response['user_info'] = 'null_clsbdh'
					udp.sendto(dumps(json_response).encode(), addr_src)
					continue

				# select地址用户信息保存
				select_users[clsbdh] = addr_src


				#成功响应消息给SELECT用户
				try:
					json_response['user_info'] = 'success'
					udp.sendto(dumps(json_response).encode(), addr_src)
				except Exception as ex:
					print_error('响应约号用户异常',ex)
					counter(server_log,'SELECT_LISTEN','RESPONSE_ERROR',ex)
					continue

				# 广播给所有PC，包括查询预约实体，以及UI实体
				# 更新select用户的udp打洞地址信息
				try:
					json_select_user = deepcopy(json_data)
					json_select_user['user_info']['select_addr'] = addr_src
					queue_transfer.put(json_select_user, True, 0.1)
				except Exception as ex:
					print_warnning('约号用户信息更新信息加入队列异常',ex)
					counter(server_log,'SELECT_LISTEN','QUEUE_PUT_ERROR',ex)


				print_infor('约号用户信息更新成功', clsbdh,addr_src)
				counter(server_log, 'SELECT_LISTEN', 'SUCCESS', clsbdh, addr_src)

			else:
				try:
					json_response['user_info'] = 'no_hostname_login_on_server_first'
					udp.sendto(dumps(json_response).encode(), addr_src)
				except Exception as ex:
					pass

		except Exception as ex:
			counter(server_log, 'SELECT_LISTEN',  'ERROR', ex)
			print_error('约号用户信息更新失败', ex)



#服务器中心控制
def __token__(limit,period,port,max=100):
	addr_yzm = ('',port)
	tcp = socket(AF_INET,SOCK_STREAM)
	tcp.bind(addr_yzm)
	tcp.listen(5)

	query_user_limit = limit
	time_list = []

	time_hphm_list = []
	for index in range(0,max):
		time_hphm_list.append(0.0)

	time_query_list = []
	for index in range(0,max):
		time_query_list.append(0.0)

	print_success('查询用户令牌进程启动成功',port,limit,max)
	#每秒钟最高的发送查号请求数，形成一个队列
	while  True:
		try:
			tcp_pip,addr = tcp.accept()
			data = tcp_pip.recv(5*1024).decode()

			#获取hphm时token启动统计
			"""if port == 62261:
				try:
					json_data = loads(data)
					index = int(json_data.get('index',-1))
					hphm =  float(json_data.get('hphm',0))
					plate = float(json_data.get('plate', 0))

					#滤波计算
					if index > 0 and index <= max:
						if hphm > 0:
							time_hphm_list[index-1] = time_hphm_list[index-1]  * 0.5 + hphm*0.5

						if plate > 0:
							time_query_list[index-1] = time_query_list[index-1]  * 0.5 + plate*0.5

						if hphm > 0 or plate > 0:
							sum = 0
							count = 0
							for i in time_hphm_list:
								if i > 0:
									sum += i
									count += 1

								if count > 0:
									time_avg_hphm = float(sum/count)
								else:
									time_avg_hphm = 0

							sum = 0
							count = 0
							for i in time_query_list:
								if i > 0:
									sum += i
									count += 1

								if count > 0:
									time_avg_plate = float(sum/count)
								else:
									time_avg_plate = 0

							counter(server_log, 'TOKEN', '%2s' % index, '%7.3f' % time_avg_plate,  '%7.3f' % time_avg_hphm, '%7.3f' % plate, '%7.3f' % hphm )

				except Exception as ex:
					counter(server_log, 'ERROR', ex)
					pass"""

			cur_time = time.time()

			#最近少于限制的用户获取token
			if len(time_list) < query_user_limit:
				tcp_pip.send('ACK'.encode())
				time_list.append(cur_time)
				#print_debug('用户查询启动')
				#counter(listen_log_file,'QUERY_TOKEN','NEW',cur_time,data)
			#最近的用户已经间隔超过1s
			elif cur_time - min(time_list) > period:
				tcp_pip.send('ACK'.encode())
				#counter(listen_log_file,'QUERY_TOKEN','UPDATE',cur_time,min(time_list),data)
				time_list.remove(min(time_list))
				time_list.append(cur_time)
				#print_debug('用户查询启动')

			else:
				#counter(listen_log_file,'QUERY_TOKEN','WAIT',cur_time,data)
				tcp_pip.send('NACK'.encode())

			tcp_pip.close()

		except Exception as ex:
			#print_warnning('查询用户令牌进程运行异常,'+str(ex))
			continue


#查询结果记录
def __query_result__(port):
	addr_yzm = ('', port)
	tcp = socket(AF_INET, SOCK_STREAM)
	tcp.bind(addr_yzm)
	tcp.listen(5)

	print_success('查询结果跟踪进程启动成功', port, )
	# 每秒钟最高的发送查号请求数，形成一个队列
	while True:
		try:
			tcp_pip, addr = tcp.accept()
			data = tcp_pip.recv(5 * 1024).decode()

			tcp_pip.send('ACK'.encode())
			try:
				json_data = loads(data)
			except Exception as ex:
				print_warnning('加载结果数据异常')
				continue

			print_infor('查询',json_data['user_info'].get('count_all'),'过滤',json_data['user_info'].get('count_hit'))

			tcp_pip.close()

		except Exception as ex:
			continue


#验证码分析进程，取分析队列中的验证码，分析完成之后返回
#queue_yzm_fx字典格式 {}
def __yzm_fx__(queue_yzm_fx,index):

	while True:

		try:

			try:
				#本地加载dll，验证码识别模块初始化
				lm_dll = ctypes.CDLL('./config/lm.dll')
				#加载进来，然后生成共享的函数
				model_path = ctypes.c_char_p(b'./config/model_4chuang_0701')
				#path_bytes = ctypes.c_int(len('./config/model_4chuang_0701'))
				load_result = lm_dll.LoadModel(model_path,ctypes.c_int(100))
				#本地引用获取验证码函数
				cget_yzm = lm_dll.LM_REC_2
			except Exception as ex:
				counter(yzmfx_log, 'YZM_FX', 'LOAD','ERROR',ex, index)
				print_warnning('验证码控件加载异常，稍后重试' + str(ex))
				time.sleep(5)
				continue

			print_success('验证码分析进程加载成功')
			counter(yzmfx_log,'YZM_FX','START',index)


			addr = None
			#tcp接口监听，接收到消息立即放入队列缓存
			udp = socket(AF_INET, SOCK_DGRAM)
			#设置超时定时器
			udp.settimeout(0.1)
			while True:

				#队列处理
				time_start = time.time()
				json_data = queue_yzm_fx.get(True)


				try:
					#地址传入
					addr = json_data.get('addr')
					if addr is None:
						counter(yzmfx_log,'YZM_FX','ERROR_ADDR',index)
						continue

					data = json_data.get('data')
					if data is None:
						counter(yzmfx_log,'YZM_FX','ERROR_DATA',index)
						continue

					result_buf = ctypes.c_char_p(b'')
					cget_yzm(ctypes.c_char_p(data),ctypes.c_int(len(data)),result_buf,ctypes.c_int(20))

					#value是b'\xd1\xb8xr\xbc\xa4'格式，需要GBK解码
					yzm_data =result_buf.value
					udp.sendto(yzm_data,addr)


					print_infor(yzm_data.decode('gbk'))

					time_end = time.time()
					"""counter(yzmfx_log, 'YZM_SEND', yzm_data.decode('gbk'),addr,
							time_end - json_data.get('time',time_start), time_end - time_start)"""

				except Exception as ex:
					counter(yzmfx_log, 'YZM_FX', 'SEND','ERROR', ex, addr, index)

				finally:
					pass
					#udp.shutdown(SHUT_RDWR)
					#udp.close()

		except Exception as ex:
			#udp.sendto(''.encode(), addr)
			#异常之后关闭UDP重新初始化
			udp.shutdown(SHUT_RDWR)
			udp.close()
			counter(yzmfx_log,'YZM_FX','ERROR',ex,addr,index)
			print_error('验证码分析进程运行异常' + str(ex))

		finally:
			lm_dll.DestroyModel()

#验证码监听进程，常驻内存，将待处理的验证码放入队列
def __yzm_listen_query__(port,queue_yzm_fx):
	#外层循环用于发生异常之后，自动重启监听

	#udp端口监听
	addr_yzm = ('',port)

	try:
		udp = socket(AF_INET,SOCK_DGRAM)
		udp.bind(addr_yzm)
		#udp.listen(5)
	except Exception as ex:
		print_error('验证码缓存进程启动异常' + str(ex))
		counter(yzmfx_log,'YZM_RECV','FAIL_LISTEN',port)
		return

	print_success('验证码缓存进程启动成功')
	while True:

		try:
			#udp接口监听，接收到消息立即放入队列缓存
			while True:


				data,addr = udp.recvfrom(300*8*1024)

				json_data = {
					'data':data,
					'addr':addr,
					'time':time.time(),
				}

				queue_yzm_fx.put(json_data,True,2)
				#counter(yzmfx_log, 'YZM_RECV', addr)

		except Exception as ex:
			counter(yzmfx_log,'YZM_RECV','ERROR',port,ex)
			print_warnning('验证码缓存进程运行异常，自动恢复' + str(ex))
	#达到不到的分支
	else:
		pass



if __name__ == "__main__":


	freeze_support()

	configInfo = {}

	try:
		# 主程序端口contro_port
		# 验证码端口yzm_fx_port
		# 服务器域名或者IPserver_host
		with open('./config/config.ini', 'r') as config_file:
			for line in config_file:
				if '=' in line:
					config_key = line.split('=')[0].strip()
					config_value = line.split('=')[1].strip()
					if config_key != '' and config_value != '':
						configInfo[config_key] = config_value

	except Exception as ex:
		counter(server_log, 'MAIN', 'CONFIG', 'ERROR', ex)
		print_error('加载配置文件异常', ex)


	#管理中心建立进程
	task_list = []

	queue_from_net = Queue(1000)
	queue_transfer = Queue(1000)
	queue_data = Queue(50)

	# query验证码分析队列
	queue_yzm_fx = Queue(100)

	# 中控监听
	task_list.append(Process(target=__yzm_listen_query__,
							 args=(int(configInfo.get('yzm_fx_server_port', '62238')), queue_yzm_fx,),
							 name='yzm_listen1'))

	yzm_fx_num = int(configInfo.get('yzm_fx_server_num', '3'))

	for index in range(1, yzm_fx_num + 1):
		task_list.append(Process(target=__yzm_fx__, args=(queue_yzm_fx, index,), name='yzm_fx'))


	# 查询token
	task_list.append(Process(target=__token__, args=(int(configInfo.get('query_user_limit','2')),
														float(configInfo.get('query_user_period', '1')), 61260,100,)))

	#结果打印记录
	task_list.append(Process(target=__query_result__,args=(61261,)))

	#客户端和用户管理，主要是接收客户端请求，建立进程
	try:
		client_manager = Process(target=__client_manager_start__,args=(61230,queue_transfer,queue_data,))
		client_manager.start()
		task_list.append(client_manager)
	except Exception as ex:
		print_error('客户端管理进程启动异常', ex)
		counter(server_log, '客户端管理进程启动异常', ex)

	#公共消息处理
	try:
		msg_handle = Process(target=__msg_handle__,args=(queue_from_net,queue_transfer,))
		task_list.append(msg_handle)
		msg_handle.start()
	except Exception as ex:
		print_error('公共消息处理进程启动异常', ex)
		counter(server_log, '公共消息处理进程启动异常', ex)

	#公共消息监听
	try:
		msg_listen = Process(target=__msg_listen__,args=(61234,queue_from_net,queue_data,))
		task_list.append(msg_listen)
		msg_listen.start()
	except Exception as ex:
		print_error('公共消息监听进程启动异常',ex)
		counter(server_log,'公共消息监听进程启动异常', ex)

	try:
		select_listen = Process(target=__select_listen__,args=(61237,queue_transfer,))
		select_listen.start()
		task_list.append(select_listen)
	except Exception as ex:
		print_error('约号用户监听进程启动异常',ex)
		counter(server_log,'约号用户监听进程启动异常', ex)

	#守护进程，保持进程一直运行，间隔5s检测一次
	while True:
		try:
			for task in task_list:
				if not task.is_alive():
					try:
						task.terminate()
					except Exception as ex:
						pass
					task.start()
					#print_warnning('进程异常，自动重启')
		except Exception as ex:
			print_warnning('进程监控发生异常',ex)
			time.sleep(10)
			continue
		finally:
			time.sleep(10)