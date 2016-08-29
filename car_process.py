#coding:utf-8

import threading
from  multiprocessing import Queue,Process,Value
from car import *
import time
from net import *
from copy import deepcopy
from log import counter,counter_print
from socket import *


#线程列表
"""
task列表，每个task生成一个出的队列
{'id':'23131321','type':'query|select',task':'线程','listen':'监听线程','queue_from_car':queue_from_car}
"""

queue_to_car_max_size = 10

"""
queue队列的值
'data':{'task_type':'query','handle_type':'start','user_info':user_conf}
"""


error_report = {
	'task_type':'status',
	'handle_type':'report',
	'user_info':None,
}

timeout_sender = 3
timeout_receiver  =60


car_process_log = 'PROCESS ' + time.strftime("%Y-%m-%d",time.localtime())

class car_process(object):


	#初始化函数
	def __init__(self,queue_from_listen_task):
		self.task_select_dict = {}
		self.task_query_list = []
		self.configInfo = {}

		self.queue_from_listen_task = queue_from_listen_task

		#约号测试账号
		self.select_test = None

		self.default_user = {
			'task_type':'query',

			'clsbdh':'query',
			'clxh':'',	#查询进程里面会自动更新
			'rdclxz':'2',#进口车
			'tbFdjh':'CAM1E65F',
			'tbFpbh':'11132122',

			'tbSyr':'adsfz',
			'ddlZjzl':'A',
			'tbZjhm':'513011111111111123',
			'tbZzzh':'',

			'tbDz':'四川省成都市',
			'txtyzbm':'610064',

			'bldd':'510100',
			'blrq':'',#查询进程获取最近一天
			'like':'1,2',
			'hate':'',
			'xxxq':'',
			'gltj':'',
			'pctj':'',


			'ddlXzhq':'510100',

			#select用户列表
			'select_user_dict':{

			},

			'send_ip':'127.0.0.1',

		}
		

		try:
			#min_inter拨号最小间隔（防止频繁的更换IP），单位秒
			with open('./config/config.ini','r') as config_file:
				for line in config_file:
					if '=' in line:
						config_key = line.split('=')[0].strip()
						config_value = line.split('=')[1].strip()
						if config_key != '' and config_value != '':
							self.configInfo[config_key] = config_value


			self.hostname = self.configInfo.get('hostname',gethostname()) 


			#query用户验证码端口
			self.yzm_fx_port_query = int(self.configInfo.get('yzm_fx_port_query','62238'))


			#select用户专用验证码端口
			self.yzm_fx_port_select = int(self.configInfo.get('yzm_fx_port_select','62237'))

			self.yzm_fx_num = int(self.configInfo.get('yzm_fx_num','3'))

			if self.configInfo.get('query_flag','') == 'true' or self.configInfo.get('query_flag','') == 'True':
				self.query_flag = True
			else:
				self.query_flag = False


			if self.query_flag:
				#query并发数
				self.max_query = int(self.configInfo.get('max_query','30'))
			else:
				self.max_query = 0


			self.redial_port = int(self.configInfo.get('redial_port','62235'))

		except Exception as ex:
			self.__counter__('CONFIG','ERROR',ex)
			#print 'car_process.py->query_task: the query_task listen config load error,',ex 

		self.__counter__('INIT','FINISH')




	def __counter__(self,*args):
		car_process_log = 'PROCESS ' + time.strftime("%Y-%m-%d",time.localtime())
		counter(car_process_log,*args)

	#终结select用户进程,user_id为clsbdh
	def __query_stop_select_user__(self,user_id=None):

		try:
			if user_id in self.task_select_dict:
				self.task_select_dict[user_id]['queue_to_car'].close()
				self.task_select_dict[user_id]['task'].terminate()
				self.__counter__('STOP','SELECT','SUCCESS',user_id)

				del self.task_select_dict[user_id]

				print_infor('约号用户停止',user_id)

			else:
				self.__counter__('STOP','SELECT','NOUSER',user_id)
				print_warnning('约号用户停止，找不到用户',user_id)
		except Exception as ex:
			self.__counter__('STOP','SELECT','ERROR',user_id,ex)
			print_error('约号用户异常', user_id)


	#创建select用户的索引，0~50之间，不能重复
	def __get_select_user_new_index__(self):
		index_pool = range(0,50)
		index_used = []
		for key,info in self.task_select_dict.items():
			index_used.append(info['index'])

		index_unused = list(set(index_pool) - set(index_used))
		if len(index_unused) > 0:
			return index_unused[0]
		else:
			return None

	#select用户任务注册启动
	def __query_register_select_user__(self,task_control):
		try:

			if self.hostname != task_control['user_info'].get('hostname'):
				print_warnning('不能在本地启动约号任务',task_control['user_info'].get('clsbdh'),self.hostname,task_control['user_info'].get('hostname'))
				return
			else:
				print_infor('可以本地启动约号任务', task_control['user_info'].get('clsbdh'), self.hostname,
							   task_control['user_info'].get('hostname'))

			#保存原始的信息
			task_control['user_info']['select_like'] = [item.strip() for item in task_control['user_info']['like'].split(',') if item.strip() != '']
			task_control['user_info']['select_hate'] = [item.strip() for item in task_control['user_info']['hate'].split(',') if item.strip() != '']
			task_control['user_info']['select_xxxq'] = [item.strip() for item in task_control['user_info']['xxxq'].split(',') if item.strip() != '']
			task_control['user_info']['select_gltj'] = task_control['user_info'].get('gltj','')
			task_control['user_info']['select_pctj'] = task_control['user_info'].get('pctj','')


			#select_user_dict空值
			task_control['user_info']['select_user_dict'] = {}
			
			#约号用户固定使用验证码分析端口0
			task_control['user_info']['yzm_fx_port'] = self.yzm_fx_port_select

			select_user_clsbdh = task_control['user_info']['clsbdh']

			if select_user_clsbdh in self.task_select_dict:
				#先终止
				self.__query_stop_select_user__(task_control['user_info']['clsbdh'])

			#分配select_listen监听端口
			#约号用户起始端口，不冲突不用更改，会自动上报服务器
			#select_port=63234
			index = self.__get_select_user_new_index__()
			if index is None:
				self.__counter__('REGISTER','NO_INDEX',task_control['user_info']['clsbdh'],task_control['user_info']['task_type'])

			task_control['user_info']['select_listen_port'] = int(self.configInfo.get('select_port','63234')) + index
			task_control['user_info']['select_login_port'] = int(self.configInfo.get('select_port','63234')) + index + 50

			#不管是原来是否存在该任务，直接复制
			queue_to_car = Queue(queue_to_car_max_size)
			self.task_select_dict[select_user_clsbdh] = {
				'index':index,
				'user_info':task_control['user_info'],
				'task':Process(target=query,args=(task_control['user_info'],queue_to_car,),name=task_control['user_info']['clsbdh']),
				'queue_to_car':queue_to_car,		#队列用于发送消息进去
			}		

			#启动进程
			self.task_select_dict[select_user_clsbdh]['task'].start()
			self.__counter__('REGISTER',task_control['user_info']['clsbdh'],task_control['user_info']['task_type'])
		except Exception as ex:

			self.__counter__('REGISTER','ERROR',task_control['user_info']['clsbdh'],task_control['user_info']['task_type'],ex)

	

	#查询启动
	def __query_register_qeury_user__(self):
		try:
			

			query_user_info  = self.default_user


			#初始化上报的select用户字典信息，key为clsbdh，info是select用户信息
			#select_user_dict与car_process的本地定义不一样，这个是传递给query用户的地址信息
			for index in range(0,self.max_query):
				queue_to_car = Queue(queue_to_car_max_size)
				query_user_info['query_index'] = index + 1
				query_user_info['yzm_fx_port'] = self.yzm_fx_port_query

				self.__counter__('REGISTER','YZM_PORT',self.yzm_fx_port_query)

				new_task = {
					'user_info':query_user_info,
					'task':Process(target=query,args=(query_user_info,queue_to_car,),name='query' + str(index+1)),		#用户查询或者预约使用进程，下面监听出口消息采用线程控制
					'queue_to_car':queue_to_car
				}

				self.task_query_list.append(new_task)
				new_task['task'].start()
				#time.sleep(0.1)

			"""count = 1
			for task in self.task_query_list:
				self.__counter__('REGISTER', 'QUERY', 'START', index + 1)
				task['task'].start()
				time.sleep(2)"""

		except Exception as ex:
			self.__counter__('REGISTER','ERROR','query',ex)



	def __query_add_select_report__(self,msg):

		#select用户信息，供query用户引用使用
		select_user_clsbdh = msg['user_info']['clsbdh']

		#上线关键信息需要更新到query用户的
		select_user_info = {
				'like':','.join(msg['user_info']['select_like']),
				'hate':','.join(msg['user_info']['select_hate']),
				'xxxq':','.join(msg['user_info']['select_xxxq']),
				'gltj':msg['user_info']['select_gltj'],
				'pctj':msg['user_info'].get('select_pctj',''),
				'select_addr':tuple(msg['user_info']['select_addr']),
		}	

		query_count = 0 
		select_user_count = 0
		for index in range(0,self.max_query):

			try:

				#如果初值不存在，则初始化
				if not 'select_user_dict' in  self.task_query_list[index]['user_info']:
					self.task_query_list[index]['user_info']['select_user_dict'] = {}

				self.task_query_list[index]['user_info']['select_user_dict'][select_user_clsbdh] = select_user_info

				#构造更新请求,handle_type为online时增加或者更新，为offline时删除select用户的订阅
				json_temp = {
					'task_type':'login',
					'handle_type':msg['handle_type'],
					'user_info':{
						'select_user_dict':self.task_query_list[index]['user_info']['select_user_dict'] 
					}

				}

				#filter(update_keys)
				self.task_query_list[index]['queue_to_car'].put(json_temp,True,timeout_sender)
				query_count += 1
				self.__counter__('QUERY','ONLINE','SUCCESS','CHANGE',index,select_user_clsbdh)
				select_user_count = len(self.task_query_list[index]['user_info']['select_user_dict'].keys())

				#print self.task_query_list[index]['user_info']
 
			except Exception as ex:
				self.__counter__('QUERY','ONLINE','ERROR',index,len(self.task_query_list),ex)
				continue
		else:
			self.__counter__('QUERY','ONLINE','SUCCESS','CHANGE_COUNT',query_count,'SELECT_COUNT',select_user_count,select_user_clsbdh)




	def __query_rmv_select_report__(self,msg):

		#select用户信息，供query用户引用使用
		select_user_clsbdh = msg['user_info']['clsbdh']
		query_count = 0

		has_select_user = False
		select_user_count = 0
		for index in range(0,len(self.task_query_list)):
			try:

				#has_select_user 判断1次是否有select用户即可，query所有进程数据保持一致
				#没有订阅的query用户，不会更新（实际上一个query进程没有订阅，其他query也不会订阅
				#if not has_select_user: 
				if not has_select_user:
					if not 'select_user_dict' in  self.task_query_list[index]['user_info'] or \
						not select_user_clsbdh in  self.task_query_list[index]['user_info']['select_user_dict']:

						self.__counter__('QUERY','OFFLINE','UNKNOW_SELECT_USER','UNCHANGE',index,select_user_clsbdh)

						break
					else:
						has_select_user = True


				if has_select_user:
					#has_select_user = True

					if 'select_user_dict' in self.task_query_list[index]['user_info'] and \
							select_user_clsbdh in self.task_query_list[index]['user_info']['select_user_dict']:
					#self.__counter__('QUERY','OFFLINE','CHANGE',index,select_user_clsbdh)
					#self.task_query_list[index]['user_info']['select_user_dict'].pop(select_user_clsbdh)
						del self.task_query_list[index]['user_info']['select_user_dict'][select_user_clsbdh]

				#构造更新请求,handle_type为online时增加或者更新，为offline时删除select用户的订阅
				json_temp = {
					'task_type':'login',
					'handle_type':msg['handle_type'],
					'user_info':{
						'select_user_dict':self.task_query_list[index]['user_info']['select_user_dict'] 
					}

				}

				#filter(update_keys)
				self.task_query_list[index]['queue_to_car'].put(json_temp,True,timeout_sender)
				query_count += 1
				#self.__counter__('QUERY','OFFLINE','SUCCESS','CHANGE',index,select_user_clsbdh)

				select_user_count = len(self.task_query_list[index]['user_info']['select_user_dict'].keys())
				self.__counter__('QUERY','OFFLINE','SUCCESS','CHANGE',index,select_user_clsbdh,select_user_count)

			except Exception as ex:
				self.__counter__('QUERY','OFFLINE','ERROR',index,ex)
		else:
			self.__counter__('QUERY','OFFLINE','SUCCESS','CHANGE_COUNT',query_count,'SELECT_COUNT_ALIVE',select_user_count,select_user_clsbdh)


	#更新只更新select用户关注的信息，更新先停止进程，更新完数据再启动，直接调用__query_register
	#原则，更新保证task_query_list中的用户信息是最新的有效数据
	def __query_update_query_user__(self,msg):
		try:
			#select上线广播
			if msg['task_type'] == 'login':
				query_pc_list = msg['user_info']['query_pc'].split(',')

				self.__counter__('LOGIN',msg['handle_type'] ,self.hostname, msg['user_info']['clsbdh'],query_pc_list)

				print_infor('约号用户信息更新',msg['user_info']['clsbdh'],'LOGIN',msg['handle_type'])
				#select用户上线
				if msg['handle_type'] == 'online':
					#hostname没有在query_pc中，需要删除订阅
					if not self.hostname in query_pc_list:
						self.__query_rmv_select_report__(msg)

					#hostname在query中，需要增加订阅
					else:			
						self.__query_add_select_report__(msg)


				#select用户下线
				elif msg['handle_type'] == 'offline' or msg['handle_type'] == 'stop' :
						self.__query_rmv_select_report__(msg)					
				else:
					self.__counter__('LOGIN','UNKNOW_TYPE',msg['user_info']['clsbdh'],msg['task_type'],msg['handle_type'])
					return
			#退出登录
			#内部生成的更新用户信息函数
			elif msg['task_type'] == 'update':

				#update_keys = ['like','hate','xxxq','gltj','blrq']
				update_keys = []

			else:
				return

		except Exception as ex:
			self.__counter__('QUERY_UPDATE','ERROR',ex)
			#print "car_process.py -> __query_update: has an error ",ex#,user_info['clsbdh']	


	#发送消息给对应的用户，不需要监听，到用户的进程之间就不再用队列通信，效率低
	def __query_send_to_query_user__(self,msg,user_id=None):
	
		for task in self.task_query_list:
			try:
				task['queue_to_car'].put(msg,True,timeout_sender)
				if user_id:
					if task['user_info']['clsbdh']  == user_id:
						task['queue_to_car'].put(msg,True,timeout_sender)
						break
				else:
					task['queue_to_car'].put(msg,True,timeout_sender)
			except Exception as ex:
				self.__counter__('SEND2QUERY','ERROR',ex)
				continue
		
		self.__counter__('SEND2QUERY','FINISH')


	#发送消息给select用户msg['user_info']['clsbdh']是用户唯一标识
	def __query_send_to_select_user__(self,msg):
		try:
			select_user_clsbdh = msg['user_info']['clsbdh']
			if select_user_clsbdh in self.task_select_dict:
				self.task_select_dict[select_user_clsbdh]['queue_to_car'].put(msg,True,timeout_sender)
				self.__counter__('SEND2SELECT','FINISH',select_user_clsbdh)
			else:
				self.__counter__('SEND2SELECT','NO_USER',select_user_clsbdh)
		except Exception as ex:
			self.__counter__('SEND2SELECT','ERROR',select_user_clsbdh,ex)


	def __select_test__(self):
		#已经有select测试用户
		try:
			if not self.select_test is None and self.select_test['task'].is_alive:
				self.__counter__('SELECT_TEST','RUNNING','SELECT_TEST')
				pass
			else:
				#随便复制一个用户信息	
				user_info = {
					#车辆基本信息
					"clsbdh":"JT8AP5421D5677378",#车辆识别代号
					"clxh":"JT8AP542",#车辆型号
					"btnQuery":"查询",#查询 btnSelect 按钮的label名称 
					#"btnSelect":"查询",#按钮的label名称 查询，返回
					"rdclxz":"2",#国产还是进口车,国产-1，进口-2

					#办理地点预约信息
					"bldd":"510100",#办理地点
					"blrq":"2016-06-23",#办理日期


					#详细信息页面		
					#"tbCjh":"S2DA15091F253103K",#车辆识别代号/车架号，使用clsbdh
					#"tbClxh":"S2DA1509",#车辆型号
					"tbFdjh":"CAM1E65F",#发动机号
					"tbFpbh":"11132122",#发票编号
					#"tbQrFpbh":"11132122",#确认发票编号
					"tbSyr":"abcde",#所有人姓名/名称
					"ddlZjzl":"A",#证件种类 
					"tbZjhm":"513011111111111123",#证件号码
					#"tbCfZjhm":"513011111111111111",#确认证件号码
					"ddlXzhq":"510100",#行政区划 
					"tbZzzh":"",#暂住证号
					"tbDz":"四川省双流县临港路四段9号",#住所地址
					"txtyzbm":"610064",#邮政编码
					"chkOK":"chkOK", #确定所填信息已完全正确，一直填写这个即可
					#"btnSelect":"查询",#按钮的label名称 查询，返回


					#所选车牌号码特征
					"like":'6,8',#心仪号码
					"hate":'4,7',#讨厌号码
					"xxxq":'1,3',#限行的星期几
				}# deepcopy(query_task['user_info'])


				user_info['clsbdh'] = 'select_test'
				user_info['task_type'] = 'select_test'

				queue_to_car = Queue(queue_to_car_max_size)

				select_test =  {
					#'id':user_info['clsbdh'],
					'user_info':user_info,
					'task':Process(target=query,args=(user_info,queue_to_car,),name=user_info['clsbdh']),		#用户查询或者预约使用进程，下面监听出口消息采用线程控制
					#'listen':Process(target=__query_out_msg,args=(queue_from_car,)),
					#'queue_from_car':queue_from_car,	#队列用于关闭
					'queue_to_car':queue_to_car,		#队列用于关闭
				}
				
				#暂时不启动观察用户
				#self.select_test['task'].start()

				self.__counter__('SELECT_TEST','START')	
		except Exception as ex:
			self.__counter__('SELECT_TEST','ERROR',ex)


	#守护线程，保证query_task_list中所有线程均保持alive状态
	def __query_observe__(self):

		start_time = None
		inter_select_test = int(self.configInfo.get('inter_select_test','1200'))



		#监听进程
		while True:			
			try:


				#task_temp = []
				count_select = 0
				count_select_alive = 0

				count_query = 0
				count_query_alive = 0

				count = 0
				count_alive = 0


				for query_task in self.task_query_list:
					count_query += 1
					if query_task['task'].is_alive():
						count_query_alive += 1

				for select_user_clsbdh,info in self.task_select_dict.items():
					count_select += 1
					if info['task'].is_alive():
						count_select_alive += 1

				count = count_query + count_select
				count_alive = count_query_alive + count_select_alive
	

				#记录统计结果
				self.__counter__('OBSERVE',count_query,'QUERY_ALIVE',count_query_alive,\
					'ORDER',count_select,'ORDER_ALIVE',count_select_alive )

				#如果有select用户状态活跃，需要定时启动虚拟用户约号查看是否正常
				if count_select_alive > 0:
					self.__select_test__()					
				else:
					#终止
					if not self.select_test is None and self.select_test['task'].is_alive:	
						self.__counter__('OBSERVE','STOP','SELECT_TEST')			
						self.select_test['task'].terminate()		

				#暂停20s轮询
				time.sleep(20)
			except Exception as ex:
				self.__counter__('OBSERVE','SYS_ERROR',ex)
				time.sleep(20)
		else:
			self.__counter__('OBSERVE','ERROR','EXIT')

	def __task_stop__(self):

		print_warnning  ('停止所有用户进程')
		count = 0
		for query_task in self.task_query_list:
			try:
				query_task['queue_to_car'].close()
				query_task['task'].terminate()
				count += 1

			except Exception as ex:
				self.__counter__('STOP', 'QUERY_USER', 'ERROR', ex)
		else:
			self.__counter__('STOP', 'QUERY_USER', count)

		for select_user_clsbdh in self.task_select_dict.keys():

			try:
				self.task_select_dict[select_user_clsbdh]['queue_to_car'].close()
				self.task_select_dict[select_user_clsbdh]['task'].terminate()
				self.__counter__('STOP', 'SELECT_USER', select_user_clsbdh)

			except Exception as ex:
				self.__counter__('STOP', 'SELECT_USER', 'ERROR',
								 self.task_select_dict[select_user_clsbdh]['user_info']['clsbdh'], ex)

	def __task_start__(self):

		print_success ( '启动所有用户进程')

		for select_user_clsbdh in self.task_select_dict.keys():

			try:
				try:
					self.task_select_dict[select_user_clsbdh]['queue_to_car'].close()
					self.task_select_dict[select_user_clsbdh]['task'].terminate()
				except Exception as ex:
					pass

				self.task_select_dict[select_user_clsbdh]['queue_to_car'] = Queue(queue_to_car_max_size)
				self.task_select_dict[select_user_clsbdh]['task'] = \
					Process(target=query, args=(self.task_select_dict[select_user_clsbdh]['user_info'], \
												self.task_select_dict[select_user_clsbdh]['queue_to_car'],),
							name=self.task_select_dict[select_user_clsbdh]['user_info']['clsbdh'])

				self.task_select_dict[select_user_clsbdh]['task'].start()
				self.__counter__('RESET', 'SELECT_USER', select_user_clsbdh)

			except Exception as ex:
				print_error('启动查询约号进程异常,' + str(ex))
				self.__counter__('RESET', 'SELECT_USER', 'ERROR',
								 self.task_select_dict[select_user_clsbdh]['user_info']['clsbdh'], ex)

		count = 0
		for query_task in self.task_query_list:
			count += 1

			try:
				try:
					query_task['queue_to_car'].close()
					query_task['task'].terminate()
				except Exception as ex:
					pass

				query_task['user_info']['query_index'] = count
				query_task['queue_to_car'] = Queue(queue_to_car_max_size)
				query_task['task'] = Process(target=query, args=(query_task['user_info'], query_task['queue_to_car'],),
											 name='query_reset')
				query_task['task'].start()
				#time.sleep(2)

				self.__counter__('RESET', 'QUERY_USER', count)
			except Exception as ex:
				print_error('启动查询用户进程异常,' + str(ex))
				self.__counter__('RESET', 'QUERY_USER', 'ERROR', ex)



	#任务重启
	#关闭当前任务列表中的所有任务，然后重新启动，不会新建任何任务，也不会改变任何任务信息
	def __task_reset__(self):


		count = 0
		for query_task in self.task_query_list:
			try:
				try:
					query_task['queue_to_car'].close()
					query_task['task'].terminate()
				except Exception as ex:
					pass

				query_task['queue_to_car'] =  Queue(queue_to_car_max_size)
				query_task['task'] = Process(target=query,args=(query_task['user_info'],query_task['queue_to_car'],),name='query_reset')
				query_task['task'].start()
				#time.sleep(2)
				count += 1
				self.__counter__('RESET','QUERY_USER',count)
			except Exception as ex:
				self.__counter__('RESET','QUERY_USER','ERROR',ex)

		for select_user_clsbdh in self.task_select_dict.keys():

			try:
				self.task_select_dict[select_user_clsbdh]['queue_to_car'].close()
				self.task_select_dict[select_user_clsbdh]['task'].terminate()

				self.task_select_dict[select_user_clsbdh]['queue_to_car'] = Queue(queue_to_car_max_size)
				self.task_select_dict[select_user_clsbdh]['task'] = \
					Process(target=query,args=(self.task_select_dict[select_user_clsbdh]['user_info'],\
						self.task_select_dict[select_user_clsbdh]['queue_to_car'],),
						name=self.task_select_dict[select_user_clsbdh]['user_info']['clsbdh'])

				self.task_select_dict[select_user_clsbdh]['task'].start()
				self.__counter__('RESET','SELECT_USER',select_user_clsbdh)

			except Exception as ex:
				self.__counter__('RESET','SELECT_USER','ERROR',self.task_select_dict[select_user_clsbdh]['user_info']['clsbdh'],ex)


			
	def __counter_rasdial__(self,*args):
		counter_file_name = 'RASDIAL ' + time.strftime("%Y-%m-%d",time.localtime())
		counter(counter_file_name,*args)


	


	#更换IP监听进程，本地使用，如果要更换IP，则重启所有任务
	def __rasdial__(self):

		addr = ('',self.redial_port)

		udp = socket(AF_INET,SOCK_DGRAM)
		udp.bind(addr)
		start_time = time.time()

		request_users = []		

		count_null_plate = 0


		reset_count = 0

		self.__counter_rasdial__('RUN','START',self.redial_port)

		while True:

			json_temp = {
				'task_type':'network',
				'handle_type':'response',
				'user_info':{

				}
			}

			try:			
				data,addr_src = udp.recvfrom(10*1024)
				cur_time = time.time()
				json_data = loads(data.decode('utf-8'))
				sender = json_data['user_info'].get('sender','')


				#非法的复位请求，不用浪费时间处理
				if json_data.get('task_type') != 'network' or sender == '':

					self.__counter_rasdial__('ERROR_MSG')
					continue

				#用户查询最简单的号码都为空之后，重新获取IP,reset计数到达之后直接复位，car进程需要谨慎
				if json_data.get('task_type') == 'network'  and json_data.get('handle_type') == 'reset':

					udp.sendto(dumps(json_temp).encode(),addr_src)

					print_warnning ('IP已不可用')
					beep(3,1000,250)

					self.__counter_rasdial__('RESET',sender)
					reset_count += 1

					if sender != 'UI' and  self.configInfo.get('net_flag') != 'true' and self.configInfo.get('net_flag') != 'True':
						print_error ('IP已不可用，但是配置文件不自动更换IP，请手动处理')
						self.__counter_rasdial__('CONFIG','DONNOT_CHANGE_IP')
						continue
					

					count = 0
					reset_count = 0

					self.__task_stop__()
					while True:
						count += 1

						result = rasdial(configInfo=self.configInfo)
						self.__counter_rasdial__('RUN',result,count)
						#如果换IP失败，等待5s重新尝试更换
						if not result:
							time.sleep(2)
							continue
						#IP更换成功，需要重新启动相关任务
						else:
							self.__task_start__()
							break
					else:
						pass

					#IP更换之后，跳出
					continue

				#有数据结果，重置
				if json_data.get('handle_type','') == 'have_num':
					#有数据
					self.__counter_rasdial__('HAVE_NUM',sender)

					#空号清零
					count_null_plate = 0
					#复位计数清零
					reset_count = 0
					udp.sendto(dumps(json_temp).encode(),addr_src)
					continue

				#查询结果为空
				self.__counter_rasdial__('NULL',sender)


				#空统计，统计到一定数量之后，让用户查询一次简单的号
				count_null_plate += 1
				#查询最简单的号，并清零null统计
				if count_null_plate >= int(self.configInfo.get('query_null_max','5')):
					count_null_plate = 0
					json_temp['handle_type'] = 'query'
					udp.sendto(dumps(json_temp).encode(),addr_src)
					self.__counter_rasdial__('QUERY',sender)

				else:
					json_temp['handle_type'] = 'continue'
					udp.sendto(dumps(json_temp).encode(),addr_src)

				
			except Exception as ex:
				self.__counter_rasdial__('ERROR',ex)
				#print "listen_task.py ->__rasdial: has an error,",ex


	#查号选好线程相关
	#调度线程，主要监听线程
	def query_schedule(self):

		self.__counter__('SHEDULE', 'START')

		self.__counter__('OBSERVE', 'TRY')
		threading_observer = threading.Thread(target=self.__query_observe__,args=())
		threading_observer.setDaemon(True)
		threading_observer.start()
		self.__counter__('OBSERVE', 'START')

		self.__counter__('RASDIAL', 'TRY')
		#换IP监听
		threading_rasdial = threading.Thread(target=self.__rasdial__, args=())
		threading_rasdial.setDaemon(True)
		threading_rasdial.start()
		self.__counter__('RASDIAL', 'START')


		#如果是查询客户端，直接启动查询进程
		if self.configInfo.get('query_flag') == 'True' or self.configInfo.get('query_flag') == 'true':
			self.__counter__('SHEDULE','QUERY','INIT')
			self.__query_register_qeury_user__()
			self.__counter__('SHEDULE', 'QUERY', 'RUNNING')
		else:
			self.__counter__('SHEDULE', 'QUERY', 'NO')


		while True:
			try:
				#阻断接收任务队列
				#{'task_type':'query','handle_type':'start','user_info':user_conf}

				self.__counter__('SHEDULE','RUNNING')

				msg = self.queue_from_listen_task.get(True)

				if '' == msg.get('user_info',''):
					continue

				task_type = msg.get('task_type','')
				handle_type = msg.get('handle_type','')

				#验证码返回值,需要传递给用户线程,该分支应该用不到了，不需要远程解析验证码
				#yzm类型是更换错误的验证码请求
				#这些消息都只发送给select用户
				if task_type  == 'yzm':
					self.__query_send_to_select_user__(msg)

				#广播消息
				elif task_type == 'broadcast':
					self.__query_send_to_query_user__(msg)

				elif msg['task_type'] == 'select':

					#select启动的信息，允许重复启动，但是重复启动只是更新查询条件
					if msg['handle_type'] == 'start':
						self.__query_register_select_user__(msg)

					elif msg['handle_type'] == 'stop':
						self.__query_stop_select_user__(msg['user_info']['clsbdh'])
						#如果有删除对应
						self.__query_rmv_select_report__(msg)

					#重新登录消息，直接转发给用户处理
					elif handle_type == 'relogin':
						self.__query_send_to_select_user__(msg=msg)

					#更换IP
					elif handle_type == 'ip':
						json_temp = {
							'task_type': 'network',
							'handle_type': 'reset',
							'user_info': {
								'sender': 'UI',
							},
						}
						udp = socket(AF_INET, SOCK_DGRAM)
						udp.sendto(dumps(json_temp).encode(), ('127.0.0.1',self.redial_port))
						data, addr_dst = udp.recvfrom(10 * 8 * 1024)

						json_data = loads(data.decode('utf-8'))

						next_handle = json_data.get('handle_type', '')
					#没有特别定义的消息直接发送给用户
					else:
						self.__query_send_to_select_user__(msg=msg)

				#地址更新任务
				elif msg['task_type']  == 'login':
					#更新任务，直接发送给用户更新
					if msg['handle_type'] == 'online':
						self.__counter__('SHEDULE','LOGIN',msg['task_type'],msg['handle_type'])
						self.__query_update_query_user__(msg)

					#离线消息，也删除
					elif msg['handle_type'] == 'offline':
						self.__counter__('SHEDULE', 'LOGIN', msg['task_type'], msg['handle_type'])
						self.__query_update_query_user__(msg)

					else:
						self.__counter__('SHEDULE','UNKNOW',msg['task_type'],msg['handle_type'])

				#其他未定义的任务类型
				else:
					self.__counter__('SHEDULE','UNKNOW',msg['task_type'],msg['handle_type'])	

			except Exception as ex:
				#print msg
				self.__counter__('SHEDULE','ERROR',ex,msg)
			finally:
				pass
				#print 'car_process.py->__query_schedule: task finisth!',task_type,handle_type
		else:
			self.__counter__('SHEDULE','EXIT','FINAL_ERROR')


#本地广播进程，提供一个端口，共所有用户监听
def __broadcast__(queue_from_listen_task):
	# 监听接口定义以及端口上报到服务器
	udp = socket(AF_INET, SOCK_DGRAM)
	# 随机绑定端口
	udp.bind(('', BROADCAST_PORT))

	while True:
		try:

			data, addr = udp.recvfrom(50 * 1024)
			udp.sendto('ACK'.encode(), addr)

			json_data = loads(data.decode('utf-8'))

			#放入队列
			queue_from_listen_task.put(json_data,True,1)
		except Exception as ex:
			counter('broadcast log','BORADCAST','ERROR',ex)

#queue_out队列用于关键信息输出，输出到中控电脑上
#查询号牌进程主函数
def query_task(queue_from_listen_task):

	broadcast_process = Process(target=__broadcast__, args=(queue_from_listen_task,), name='broadcast')
	print_success('广播进程启动')
	# 查询任务监控队列直接启动
	broadcast_process.start()

	car_manager = car_process(queue_from_listen_task)
	print_success('用户控制主进程启动')
	#调度进程启动
	car_manager.query_schedule()

	print_error(('用户控制主进程退出'))