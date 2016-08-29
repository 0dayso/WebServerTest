#!/usr/bin/env python
#coding:utf-8

from socket import *
from json import dumps,loads

#线程
import threading
#进程
from  multiprocessing import Process,Queue,freeze_support

import time
import ctypes

#加载车牌号查询和选择进程
from car_process import query_task
from net import *
from log import counter,counter_print
from ui import *
from PIL import Image,ImageTk
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


listen_log_file = 'LISTEN ' + time.strftime("%Y-%m-%d",time.localtime())


#消息队列处理函数，主要是消息分发，任务创建
def __listen_handle__(queue_from_net,queue_to_net):

	#进程间通信
	#查询和约号任务队列
	query_queue = Queue(10)
	#查询和约号任务进程,界面窗口处理队列传递进来
	query_task_process = Process(target=query_task,args=(query_queue,),name='query')
	#查询任务监控队列直接启动
	query_task_process.start()


	while True:
		try:
			data = queue_from_net.get(True)

			#采用队列方式
			status,info = 200,'ok'
			json_data = loads(data.decode())
			json_data['user_info']['send_ip'] = '127.0.0.1'

			task_type = json_data.get('task_type','')

			#查询任务及其他更新等等任务
			if json_data['task_type'] == 'query' or \
				json_data['task_type'] == 'select' or json_data['task_type'] == 'order' or \
				json_data['task_type'] == 'yzm_response' or json_data['task_type'] == 'login' or \
				json_data['task_type'] == 'yzm':
				#第二个参数等待阻断，第三个参数是超时时间，3s
				query_queue.put(json_data,True,3)

				#约号相关的任务，传递给UI
				if json_data.get('task_type') == 'select':
					pass

				#任务记录
				counter(listen_log_file,'LISTEN_HANDLE',json_data['task_type'],json_data['handle_type'])

			else:
				counter(listen_log_file,'LISTEN_HANDLE','ERROR','UNKNOW_TYPE',json_data['task_type'])
		except Exception as ex:
			counter(listen_log_file,'LISTEN_HANDLE','ERROR',ex)

		

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
				counter(listen_log_file, 'YZM_FX', 'LOAD','ERROR',ex, index)
				print_warnning('验证码控件加载异常，稍后重试' + str(ex))
				time.sleep(5)
				continue

			print_success('验证码分析进程加载成功')
			counter(listen_log_file,'YZM_FX','START',index)


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
						counter(listen_log_file,'YZM_FX','ERROR_ADDR',index)
						continue

					data = json_data.get('data')
					if data is None:
						counter(listen_log_file,'YZM_FX','ERROR_DATA',index)
						continue

					result_buf = ctypes.c_char_p(b'')
					cget_yzm(ctypes.c_char_p(data),ctypes.c_int(len(data)),result_buf,ctypes.c_int(20))

					#value是b'\xd1\xb8xr\xbc\xa4'格式，需要GBK解码
					yzm_data =result_buf.value
					udp.sendto(yzm_data,addr)
					time_end = time.time()
					"""counter(listen_log_file, 'YZM_SEND', yzm_data.decode('gbk'),addr,
							time_end - json_data.get('time',time_start), time_end - time_start)"""

				except Exception as ex:
					counter(listen_log_file, 'YZM_FX', 'SEND','ERROR', ex, addr, index)

				finally:
					pass
					#udp.shutdown(SHUT_RDWR)
					#udp.close()

		except Exception as ex:
			#udp.sendto(''.encode(), addr)
			#异常之后关闭UDP重新初始化
			udp.shutdown(SHUT_RDWR)
			udp.close()
			counter(listen_log_file,'YZM_FX','ERROR',ex,addr,index)
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
		counter(listen_log_file,'YZM_RECV','FAIL_LISTEN',port)
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
				#counter(listen_log_file, 'YZM_RECV', addr)

		except Exception as ex:
			counter(listen_log_file,'YZM_RECV','ERROR',port,ex)
			print_warnning('验证码缓存进程运行异常，自动恢复' + str(ex))
	#达到不到的分支
	else:
		pass


#验证码监听进程，常驻内存，将待处理的验证码放入队列
def __yzm_listen_select__(port,queue_to_net=None):
	#外层循环用于发生异常之后，自动重启监听

	#tcp端口监听
	addr_yzm = ('',port)

	try:
		tcp = socket(AF_INET,SOCK_STREAM)
		tcp.bind(addr_yzm)
		tcp.listen(5)
	except Exception as ex:
		counter(listen_log_file,'YZM_LISTEN','FAIL_LISTEN',port)
		print_error('约号验证码启动异常' + str(ex))
		return


	while True:
		try:
			try:
				#本地加载dll，验证码识别模块初始化
				lm_dll = ctypes.CDLL("./config/lm.dll")
				#加载进来，然后生成共享的函数
				model_path = ctypes.c_char_p(b'./config/model_4chuang_0701')
				#path_bytes = ctypes.c_int(len('./config/model_4chuang_0701'))
				load_result = lm_dll.LoadModel(model_path,ctypes.c_int(100))
				#本地引用获取验证码函数
				cget_yzm = lm_dll.LM_REC_2
			except Exception as ex:
				counter(listen_log_file,'YZM_LISTEN_SELECT','LOAD','ERROR',ex)
				print_warnning('验证码控件加载异常，稍后重试恢复' + str(ex))
				time.sleep(5)
				continue
			
			counter(listen_log_file,'YZM_LISTEN_SELECT','START',port)

			print_success('约号验证码启动正常')
			#tcp接口监听，接收到消息立即放入队列缓存
			while True:	


				tcp_pip,addr = tcp.accept()
				time_start = time.time()

				#验证码二进制字符串，不解码
				data = tcp_pip.recv(300*8*1024)#.decode('utf-8')

				result_buf = ctypes.c_char_p(b'')
				buf_bytes = ctypes.c_int(20)

				#需要吐给窗口界面处理，select用户的验证码，需要解析出clsbdh和码1或者码2属性
				#file_flag =  file_in['data'][0:17] +  file_in['data'][17:18] + '$'
				#前面17位是车架号，紧跟1位是码1还是码2，后面data是图片数据
				#clsbdh = data[0:17]
				#yzm_type = data[17:18]
				#data = data[19:] 
				#counter(listen_log_file,'YZM_LISTEN','SELECT',data[0:17].decode(),data[17:18].decode())
				cget_yzm(ctypes.c_char_p(data[18:]),ctypes.c_int(len(data)),result_buf,buf_bytes)

				time_end = time.time()
				#yzm = unicode( result_buf.value,'gbk').decode('utf-8')
				#二进制结果
				#yzm =result_buf.value
				yzm_data = result_buf.value

				#counter(listen_log_file, 'YZM_LISTEN', 'SELECT',  data[0:17].decode(), data[17:18].decode(),yzm_data,time_end - time_start)
				tcp_pip.send(yzm_data)
				tcp_pip.close()	

				json_temp = {
					'task_type':'yzm',
					'handle_type':'refresh',
					'user_info':{
						'yzm':result_buf.value,
						#'data':data.decode('utf-8'),
					}
				}

				#20个0标识头
				yzm_head = b'0'*20
				id_fmt = '!20s'
				#body_head = pack(id_fmt,dumps(json_temp).encode())
				yzm_value = pack(id_fmt, result_buf.value)

				queue_to_net.put(yzm_head+yzm_value+data,True,2)
					

		except Exception as ex:
			counter(listen_log_file,'YZM_LISTEN','ERROR',port,ex)
			print_warnning('验证码缓存进程运行异常，自动恢复' + str(ex))
		finally:
			lm_dll.DestroyModel()


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

			#counter(listen_log_file, 'TOKEN', data)

			#获取hphm时token启动统计
			if False and port == 62261:
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

							counter(listen_log_file, 'TOKEN', '%2s' % index, '%7.3f' % time_avg_plate,  '%7.3f' % time_avg_hphm, '%7.3f' % plate, '%7.3f' % hphm )

				except Exception as ex:
					counter(listen_log_file, 'ERROR', ex)
					pass

			cur_time = time.time()

			#最近少于限制的用户获取token
			if len(time_list) < query_user_limit:
				tcp_pip.send('ACK'.encode())
				time_list.append(cur_time)
				#counter(listen_log_file,'QUERY_TOKEN','NEW',cur_time,data)
			#最近的用户已经间隔超过1s
			elif cur_time - min(time_list) > period:
				tcp_pip.send('ACK'.encode())
				#counter(listen_log_file,'QUERY_TOKEN','UPDATE',cur_time,min(time_list),data)
				time_list.remove(min(time_list))
				time_list.append(cur_time)

			else:
				#counter(listen_log_file,'QUERY_TOKEN','WAIT',cur_time,data)
				tcp_pip.send('NACK'.encode())

			tcp_pip.close()

		except Exception as ex:
			print_warnning('查询用户令牌进程运行异常,'+str(ex))
			continue



def main_start():
	pass

if __name__ == '__main__':


	freeze_support()





	configInfo = {}

	try:
		#主程序端口contro_port
		#验证码端口yzm_fx_port
		#服务器域名或者IPserver_host
		with open('./config/config.ini','r') as config_file:
			for line in config_file:
				if '=' in line:
					config_key = line.split('=')[0].strip()
					config_value = line.split('=')[1].strip()
					if config_key != '' and config_value != '':
						configInfo[config_key] = config_value

	except Exception as ex:
		counter(listen_log_file,'MAIN','CONFIG','ERROR',ex)
		print_error('加载配置文件异常',ex)


	#初始化IP
	while True:

		if configInfo.get('net_flag') != 'true' and configInfo.get('net_flag') != 'True':
			break

		result = rasdial(configInfo=configInfo)
		# 如果换IP失败，等待5s重新尝试更换
		if not result:
			print_success('宽带连接初始化失败，2秒后重试')
			time.sleep(2)
			continue
		# IP更换成功，需要重新启动相关任务
		else:
			print_success('宽带连接初始化成功')
			break
	else:
		pass




	task_list = []

	try:

		#query验证码分析队列
		queue_yzm_fx = Queue(100)

		# 登录token
		task_list.append(
			Process(target=__token__, args=(int(configInfo.get('login_user_limit', '2')),
											float(configInfo.get('login_user_period', '1')),62259,
											int(configInfo.get('max_query', '30')),), name='qeury_token'))

		#查询token
		task_list.append(Process(target=__token__,args=(int(configInfo.get('query_user_limit','2')),
														float(configInfo.get('query_user_period', '1')),62260,
														int(configInfo.get('max_query', '30')),),name='qeury_token'))

		#hphm下载token
		"""task_list.append(Process(target=__token__,args=(int(configInfo.get('hphm_user_limit','2')),
														float(configInfo.get('hphm_user_period', '1')),62261,
														int(configInfo.get('max_query', '30')),),name='hphm_token'))"""

		# http_get下载token
		"""task_list.append(Process(target=__token__, args=(int(configInfo.get('http_get_limit', '2')),
														 float(configInfo.get('http_get_period', '1')), 62262,
														 int(configInfo.get('max_query', '30')),), name='hphm_token'))

		# http_post下载token
		task_list.append(Process(target=__token__, args=(int(configInfo.get('http_post_limit', '2')),
														 float(configInfo.get('http_post_period', '1')), 62263,
														 int(configInfo.get('max_query', '30')),), name='hphm_token'))"""


		#网络消息送达的任务管理监听
		queue_from_net = Queue(100)
		queue_to_net = Queue(100)
		server = configInfo.get('server_host', 'www.wuyoubar.cn')
		server_port = int(configInfo.get('slogin_port', '61236'))
		hostname = configInfo.get('hostname', gethostname())
		select_flag = configInfo.get('select_flag')
		query_flag = configInfo.get('query_flag')

		user_type = client.CLIENT.value
		"""if (select_flag  == 'True' or select_flag  == 'true') and query_flag:
			user_type = client.CLIENT.value
		elif select_flag:
			user_type = client.SELECT.value
		elif query_flag:
			user_type = client.QUERY.value
		else:
			print_error('客户端类型参数配置错误，请检查配置文件')"""

		#user_type,server, server_port, hostname, queue_from_net, queue_to_net
		task_list.append(Process(target=client_login,args=(user_type,server,server_port,hostname ,queue_from_net,queue_to_net,)))
		task_list.append(Process(target=__listen_handle__,args=(queue_from_net,queue_to_net,),name='__listen_handle__'))


		#约号用户专用
		if configInfo.get('select_flag') == 'True' or configInfo.get('select_flag') == 'true':
			#约号用户专用验证码分析进程和视窗界面
			task_list.append(Process(target=__yzm_listen_select__,\
				args=(int(configInfo.get('yzm_fx_port_select','62237')),queue_to_net,),name='yzm_listen'))


			

		#验证码可以多开启几个进程,增强并发性能，特别是有query任务场景
		if configInfo.get('query_flag') == 'True' or configInfo.get('query_flag') == 'true':

			yzm_fx_num = int(configInfo.get('yzm_fx_num','3'))

			#中控监听
			task_list.append(Process(target=__yzm_listen_query__,args=(int(configInfo.get('yzm_fx_port_query','62238')),queue_yzm_fx,),name='yzm_listen1'))

			for index in range(1,yzm_fx_num + 1):			
				task_list.append(Process(target=__yzm_fx__,args=(queue_yzm_fx,index,),name='yzm_fx'))

		

	except Exception as ex:
		counter(listen_log_file,'MAIN','RUNNING','ERROR',ex)
		print_error('启动过程中发生异常',ex)


	def task_start():
		for task in task_list:
			if not task.is_alive():
				task.start()

	def task_observer():
		for task in task_list:
			if not task.is_alive():
				task.terminate()
				task.start()


	task_start()
	#守护进程，保持进程一直运行，间隔5s检测一次
	while True:
		try:
			pass
			task_observer()
		except Exception as ex:
			continue
		finally:
			time.sleep(10)

	counter(listen_log_file,'MAIN','EXIT','ERROR')
	print_error('程序异常退出')



