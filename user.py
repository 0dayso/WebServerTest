#!/usr/bin/env python
#coding:utf-8



from net import send_with_ack
import time,datetime
from json import dumps,loads
from struct import unpack,pack
from bs4 import BeautifulSoup

import os
import pickle
from copy import deepcopy
from log import counter,counter_print
from common import  *

"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')"""


#form = cgi.FieldStorage()
global html_enter,user_conf_keys

password = 'afdjiajfoeijieojiffoa87712121'

#用户日志
user_log = 'USER ' +  time.strftime("%Y-%m-%d",time.localtime())

#定义文件存储的目录和后缀
config_path = './user/'
type_user = '.user'
type_sys = '.sys'


html_enter = '\r\n'

#global user_conf,conf_running
#user的数据域
user_conf_keys = ['yxzt','status','xzhm','error','clsbdh','clxh','rdclxz','tbFdjh',\
	'tbFpbh','bldd','blrq','ddlXzhq','tbSyr',\
	'ddlZjzl','tbZjhm','tbZzzh','tbDz','txtyzbm',\
	'task_type','hostname','like','hate','xxxq','gltj','ddlhplqd','query_pc']




def is_manage(form):
	if not 'pass' in form.keys() or form.getvalue('pass') != password:
		#print ('is_manage:password error!')
		return False
	else:
		return True


#根据关键字查找用户
def config_user_find(key,value):
	if key == '' or value == '':
		return None

	#遍历配置文件
	for file in os.listdir(config_path):
		with open(config_path+file,'rb') as file_config:
			jsonTemp = pickle.load(file_config)
			file_config.close()
			if key in jsonTemp.keys() and jsonTemp[key] == value:
				return jsonTemp

	else:
		print ('config.py -> config_user_load: cannot find the user',key,value)
		return None







#保存用户信息，需要后续操作的返回字典，否则全部返回False
def save_user_info(json_data,handle='update'):

	if json_data is None:
		print_error('更新用户信息，但是数据为空')
		return False

	try:
		clsbdh =  json_data.get('clsbdh')
		if clsbdh =='' or clsbdh is None:
			counter(user_log,'SAVE','FAIL','NULL_CLSBDH')
			print_error('更新用户信息，但是没有有效的clsbdh')
			return False

		user_infor = get_user_info(clsbdh)


		if handle == 'delete':
			if user_infor.get('status') != 'idle':
				counter(user_log,'SAVE','DELETE','FAIL',clsbdh,'NOT_IDLE',user_infor.get('status'))
				print_error('删除用户信息，但是用户不空闲')
				return False

			return delete_user_info(clsbdh)


		#更新用户
		if user_infor:
			for key,value in json_data.items():
				#如果是xzhm不为空，不需要更新，否则更新
				if key == 'xzhm' and user_infor.get('xzhm','') != '':
					continue
				user_infor[key] = value
		#新建用户
		else:
			user_infor = json_data

		#用户任务属性固定为select
		user_infor['task_type'] = 'select'


		if user_infor.get('xzhm','') != '':
			user_infor['status'] = 'success'

		#持久化存储
		file_name = config_path+ clsbdh + type_user
		with open(file_name,'wb') as file_config:
			pickle.dump(user_infor,file_config)
			file_config.close()

	except Exception as ex:
		counter(user_log,'SAVE','CONFIG','ERROR',ex)
		print_error('更新用户信息异常',ex)
		return False

	try:

		counter(user_log,'SAVE','SUCCESS',clsbdh)

		#触发任务更新，已经约好的用户不能重复操作
		if handle == 'start' or handle == 'stop':
			return get_user_task(user_infor)

		#约好成功的回执，status状态也为sucess
		elif handle == 'success':
			counter(user_log,'SAVE','XZHM',user_infor.get('xzhm',''))
			return get_user_task(user_infor)
		else:
			pass

		return False
	except Exception as ex:
		counter(user_log,'SAVE','TASK','ERROR',ex)
		return False


#用户信息提取
def get_user_info(clsbdh):

	jsonTemp = {}
	if clsbdh is None or clsbdh == '':
		counter(user_log,'GET','USER','CLSBDH_NULL')
		return jsonTemp
	try:
		file_name = config_path + clsbdh + type_user
		if not os.path.exists(file_name):
			counter(user_log,'GET','USER','CLSBDH_NOT_FOUND')
			return jsonTemp

	except Exception as ex:
		counter(user_log,'GET','USER','FAIL_FOUND')
		return jsonTemp

	#用户配置相关信息
	try:
		#前置默认值
		with open(file_name,'rb') as file_config:
			#加载配置文件
			#user_str = unpack('i',file_config.read())
			jsonTemp =  pickle.load(file_config)
			file_config.close()

			return jsonTemp

	except Exception as ex:
		#user_conf['error'] = ex
		counter(user_log,'GET','USER','ERROR',ex)
		return jsonTemp


#用户信息提取
def delete_user_info(clsbdh):

	if clsbdh is None or clsbdh == '':
		counter(user_log,'DELETE','USER','CLSBDH_NULL')
		return False

	try:
		file_name = config_path +clsbdh+type_user
		if not os.path.exists(file_name):
			counter(user_log,'DELETE','USER','NOT_FOUND')
			return False

		os.remove(file_name)
		return False

	except Exception as ex:
		counter(user_log,'DELETE','USER','ERROR',ex)
		return False


#获取用户数据列表
def get_user_list(user_type='running'):

	try:
		listfile=os.listdir(config_path)
	except Exception as ex:
		print_debug('获取USER文件列表异常',ex)
		pass

	json_data = []
	type_len = len(type_user)

	for file_name in listfile:
		if len(file_name) > type_len and file_name.endswith(type_user):

			#获取用户信息
			tempUser = get_user_info(file_name[:-5])

			clsbdh = tempUser.get('clsbdh','')

			#代号非法
			if clsbdh == '':
				continue

			if user_type == 'all' or user_type == tempUser.get('status'):
				json_data.append(tempUser)
			else:
				continue

	else:
		pass

	return json_data










#刷新任务状态，需要发送任务到select用户以及所有有效的query用户
def get_user_task(user_infor):

	
	user_infor['select_user'] = user_infor['clsbdh']

	#启动任务
	if user_infor['status'] == 'running':
		data  = {
			'task_type':'select','handle_type':'start','user_info':user_infor
		}

		counter(user_log,'TASK','START')

	#停止任务
	elif user_infor['status'] == 'idle':
		data  = {
			'task_type':'select',
			'handle_type':'stop',
			'user_info':{
				'clsbdh':user_infor['clsbdh'],
				'hostname':user_infor['hostname'],
				'query_pc':user_infor['query_pc'],
			},
		}

		counter(user_log,'TASK','STOP','CONTROL')

	elif  user_infor['status'] == 'success':
		task_request = 'stop'
		data  = {
			'task_type':'select',
			'handle_type':'stop',
			'user_info':{
				'clsbdh':user_infor.get('clsbdh',''),
				'hostname':user_infor.get('hostname',''),
				'query_pc':user_infor.get('query_pc',''),
				'xzhm':user_infor.get('xzhm',''),
			},
		}

		counter(user_log,'TASK','STOP',user_infor['xzhm'])

	else:
		return False


	return data





#发送验证码
def send_yzm_code(form):

	yzm_response = {
		'task_type':'yzm_response',
		'handle_type':'yzm1',
		'user_info':{'name':'yzm_pic.png','data':''}
	}
	
	

	img_path = './yzm/'
	type_yzm = '.png'


	listfile=os.listdir(img_path)


	#ip未填写，不能发送验证码
	if not 'clsbdh' in form.keys():
		pass
	else:
		clsbdh = form.getvalue('clsbdh')
		user_temp = config_user_find('clsbdh',clsbdh)


		#print user_temp
		if user_temp is None:
			print ('cannot find the user',clsbdh)
		else:

			addr = (user_temp['ip'],62234)

			yzm_response['user_info']['clsbdh'] = user_temp['clsbdh']	
			yzm_response['user_info']['task_type'] = user_temp['task_type']
			#查询验证码
			if 'cxyzm' in form.keys():
				yzm1_response = deepcopy(yzm_response)
				yzm1_response['user_info']['data'] = form.getvalue('cxyzm')
				
				addr = (user_temp['ip'],62234)

				send_with_ack(addr=addr,json_data=yzm1_response)

				for file_name in listfile:
					if file_name.startswith(clsbdh+'$1$'):
						os.remove(img_path + file_name)

			if 'yyyzm' in form.keys():
				yzm2_response = deepcopy(yzm_response)
				yzm2_response['handle_type'] = 'yzm2'
				yzm2_response['user_info']['data'] = form.getvalue('yyyzm')


				send_with_ack(addr=addr,json_data=yzm2_response)

				for file_name in listfile:
					if file_name.startswith(clsbdh+'$2$'):
						os.remove(img_path + file_name)



#保持在线运行
online_flag = True
def offline():
	online_flag = False

#状态保持函数
def __status__():
	while True and online_flag:
		time.sleep(20)

#__status__()






