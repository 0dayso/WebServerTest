#!/usr/bin/env python
#coding:utf-8


from socket import  *
from  multiprocessing import Process,Queue,freeze_support
from log import  *
from common import *
from json import  loads,dumps
import  threading
import  message
import time
import encodings.idna


# 任务监听，保持两个tcp连接
#使用到hostname,server_host和slogin_port三个重要参数
class login_to_server():
	def __init__(self,user_type, server,port,hostname, queue_from_net,queue_to_net):

		self.user_type = user_type
		self.server = server
		self.server_port = port

		#host name和文件名称
		self.hostname = hostname
		self.log_file = self.hostname  + ' ' + time.strftime("%Y-%m-%d",time.localtime())

		self.server_recv_port = -1
		self.server_send_port = -1

		self.queue_from_net = queue_from_net
		self.queue_to_net = queue_to_net

		self.login_queue = Queue(10)


		self.online = False

		#udp还是tcp登录模式
		self.mode = 'udp'


		#启动运行
		self.__start__()



	# 登录线程，并启动本地监听进程
	def __local_init__(self):

		while True:

			# 分配本地udp监听端口
			try:
				self.udp_recv = socket(AF_INET, SOCK_DGRAM)
				self.udp_send = socket(AF_INET, SOCK_DGRAM)

				# 2秒超时即可
				self.udp_send.settimeout(5)
				#self.udp_recv.setblocking(True)

				# 随机分配一个端口
				self.udp_recv.bind(('', 0))
				# 端口
				self.local_recv_port = self.udp_recv.getsockname()[1]

				# 连接服务器，IP更新
				self.heart =  message.msg_encode({
					'task_type': 'login',
					'handle_type': 'online',
					'user_info': {
						'hostname': self.hostname,
						'user_type': self.user_type,
						'client_port': self.local_recv_port,
					}
				},message.HEADER_HEART)

				break

			except Exception as ex:
				print_error('本地端口分配失败', ex)
				counter(self.log_file,'INIT_ERROR',ex)
				time.sleep(5)
				continue

		print_success('01 本地端口分配成功',self.local_recv_port)



	# 发送自身的端口号，已经获取服务器为本次登录分配的端口号
	def __send_local_port__(self):
		# 如果不在线，循环登录直到成功，保持20s的心跳
		self.online = False
		while True:
			counter(self.log_file, 'PORT_TRY', self.server, self.server_port)
			print_infor('03 更新本地端口到服务器', self.server, self.server_port, self.server_recv_port,self.local_recv_port)

			udp_send = socket(AF_INET, SOCK_DGRAM)
			udp_send.settimeout(5)
			if self.server_recv_port and self.server_recv_port > 0:
				# 注册成功过，直接发给用户级监听端口
				try:
					self.udp_recv.sendto(self.heart, (self.server, self.server_recv_port))
				# 发送异常场景下，地址发给登录端口
				except Exception as ex:
					try:
						self.udp_recv.sendto(self.heart, (self.server, self.server_port))
					except Exception as ex:
						print_error('登录发生异常', ex)
						counter(self.log_file,'PORT_SEND_ERROR',self.server_port, ex)
						time.sleep(2)
						continue
			else:
				try:
					self.udp_recv.sendto(self.heart, (self.server, self.server_port))
				except Exception as ex:
					print_error('登录发生异常',ex)
					counter(self.log_file,'PORT_SEND_ERROR',self.server_port, ex)
					time.sleep(2)
					continue
			try:
				data = self.udp_recv.recv(5 * 1024)

				if data.decode() == 'ACK':
					print_success('02 登录发送本地端口成功')
					return True
				else:
					print_warnning('登录响应失败')

			except Exception as ex:
				print_warnning('登录发送本地端口，等待2秒之后重新发送',ex)
				time.sleep(2)
				continue


			# 等待5秒
			time.sleep(2)


	def __get_server_port__(self,data):
		try:
			json_temp = message.msg_decode(data, message.HEADER_HEART)
			if not json_temp:
				print_error('登录服务器响应消息非法', data[:20])
				return False
		except Exception as ex:
			print_error('登录服务器响应消息异常',ex)
			return False

		try:
			# 获取服务器端口
			self.server_recv_port = int(json_temp['user_info']['server_recv_port'])
			counter(self.log_file, 'PORT_SUCCESS', self.server_recv_port)
			print_success('登录服务器监听端口初始化成功', self.server_recv_port)
			return True
		except Exception as ex:
			counter(self.log_file, 'PORT_ERROR', ex)
			print_error('登录服务器，服务器响应成功，但解析消息异常', ex)
			return False


	# UDP发送进程，负责传递本地地址到服务器保持最新状态
	def __udp_send__(self):

		while True:
			# 有用户数据需要发送给服务器,没有数据，发送心跳
			try:
				# 20秒钟发送一次心跳
				try:
					json_data = self.queue_to_net.get(True)
				except Exception as ex:
					#print_debug('登录发送进程队列获取异常')
					continue
					#data = b'ffff'
				else:
					# JSON格式编码
					try:
						data = dumps(json_data).encode()
					# 非JSON格式的直接发送
					except:
						data = json_data

				#发送消息最多尝试3次
				count = 0
				while count < 20:
					count += 1

					#如果服务器端口还没有获取成功
					if not self.online or self.server_recv_port < 0:
						time.sleep(3)
						continue

					try:
						self.udp_send.sendto(data,(self.server,self.server_recv_port))
						break
					except Exception as ex:
						time.sleep(1)
						continue
				else:
					#数据恢复到队列
					self.queue_to_net.put(data)
					continue


				try:
					if self.udp_send.recv(512).decode('utf-8') == 'ACK':
						continue
					else:
						counter(self.log_file, 'LISTEN_SEND', 'FAIL')
						continue
				except Exception as ex:
					counter(self.log_file, 'LISTEN_SEND', 'ERROR',ex)
					print_warnning('发送消息到服务器等待响应异常',ex)
					continue
			# 没有数据发送
			except Exception as ex:
				print_error('发送消息到服务器进程异常',ex)
				continue

	# 接收消息的进程
	def __udp_recv__(self):

		print_success('客户端接收进程启动')
		#self.udp_recv.sendto('INIT'.encode(), (self.server,self.server_port))

		self.__send_local_port__()

		self.udp_recv.settimeout(20)
		while True:
			try:
				data,addr_peer = self.udp_recv.recvfrom(300 * 1024)
				self.udp_recv.sendto('ACK'.encode(),addr_peer)

				# 心跳消息，携带有服务器端口地址
				if data[:20] == message.HEADER_HEART:
					if self.__get_server_port__(data):
						print_success('服务器端口开放成功',self.server_recv_port)
						self.online = True

					continue

				# 1s超时
				self.queue_from_net.put(data, True, 1)

			# 异常则退出，重新初始化
			except Exception as ex:
				counter(self.log_file, 'LISTEN_RECV', 'ERROR', ex)
				print_error('接收服务器消息进程异常',ex)
				self.__send_local_port__()
				continue

	"""
	queue队列的值
	'data':{'task_type':'query','handle_type':'start','user_info':user_conf}
	"""

	# 监听控制接口，缓存队列，在线监听
	def __start__(self):

		while True:
			try:
				#本地端口初始化
				self.__local_init__()



				print_success('02 本地监听线程启动')
				recv = threading.Thread(target=self.__udp_recv__)
				recv.start()

				#发送进程启动正常
				time.sleep(0.2)



				send = threading.Thread(target=self.__udp_send__)

				send.start()

				send.join()
				recv.join()

			# 异常之后，迅速重连
			except Exception as ex:
				print_error('与服务器连接异常，10秒后自动重连')
				counter(self.log_file, 'LISTEN_ONLINE', 'ERROR', ex)
				time.sleep(10)


#通信进程
def client_login(user_type,server, server_port, hostname, queue_from_net, queue_to_net):
	# 后台通信进程启动
	login_to_server(user_type= user_type, server=server, port=server_port, hostname=hostname, queue_from_net=queue_from_net,
							queue_to_net=queue_to_net)