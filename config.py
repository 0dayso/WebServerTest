#!/usr/bin/env python
#coding:utf-8


import cgi
from urllib  import unquote
from net import send_with_ack
import time,datetime
from json import dumps,loads
from struct import unpack,pack
from bs4 import BeautifulSoup

import os
import pickle
from copy import deepcopy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


#form = cgi.FieldStorage()
global html_enter,user_conf_keys

password = 'afdjiajfoeijieojiffoa87712121'
#定义文件存储的目录和后缀
config_path = './config/'
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
		print 'is_manage:password error!'
		return False
	else:
		return True


#根据关键字查找用户
def config_user_find(key,value):
	if key == '' or value == '':
		return None

	#遍历配置文件
	for file in os.listdir(config_path):
		with open(config_path+file,'r') as file_config:
			jsonTemp = pickle.load(file_config)
			file_config.close()
			if key in jsonTemp.keys() and jsonTemp[key] == value:
				return jsonTemp

	else:
		print 'config.py -> config_user_load: cannot find the user',key,value
		return None


#用户信息提取
def config_user_get(clsbdh):
	jsonTemp = {}
	if clsbdh == '':
		return jsonTemp

	file_name = './config/'+clsbdh+type_user
	if not os.path.exists(file_name):
		return jsonTemp
	#用户配置相关信息
	try:
		#前置默认值
		with open(file_name,'r') as file_config:
			#加载配置文件
			#user_str = unpack('i',file_config.read())
			jsonTemp =  pickle.load(file_config)
			file_config.close()

			return jsonTemp

	except Exception,ex:
		#user_conf['error'] = ex
		return jsonTemp



#从网页提交的信息中刷新，或者内部传送字典过来进行刷新
def config_save(form):



	#clsbdh = 
	
	#global user_conf,conf_running
	#如果是form页面修改
	if isinstance(form,cgi.FieldStorage):

		clsbdh = form.getvalue('clsbdh')
		if clsbdh == '':
			print '车架号不能为空'
			return
		user_conf  =  config_user_get(clsbdh)

		for key in user_conf_keys:
			if key in form.keys():
				user_conf[key] = form.getvalue(key)
			#form表单中没有赋值的，同时user_conf也没有赋值的
			else:
				user_conf[key] = ''

		if user_conf['rdclxz'] == '2':
			user_conf['clxh'] = user_conf['clsbdh'][:8]

		file_name = './config/'+form.getvalue('clsbdh') + type_user
		with open(file_name,'w') as file_config:
			pickle.dump(user_conf,file_config)

			file_config.close()

		"""
		with open('./config/conf_server'+ type_sys,'w') as file_config:
			pickle.dump(conf_running,file_config)"""

	#其他接口修改，只能修改任务运行状态，不能修改其他字段
	else:
		clsbdh = form.get('clsbdh','')
		user_conf  =  config_user_get(clsbdh)

		for key in form.keys():
			user_conf[key] = form.get(key,'')

		file_name = './config/'+ form.get('clsbdh','') + type_user
		with open(file_name,'w') as file_config:
			pickle.dump(user_conf,file_config)



			file_config.close()

		#任务状态更新
		#refresh_task(clsbdh)

	return True


def get_config_list(form):


	listfile=os.listdir(config_path)


	html = ''


	#html += '<ul>'

	html += '<table border="1">'

	#标题行
	html += '<tr>'
	html += '<th>' + '车架号' + '</th>'
	html += '<th>' + '任务类型' + '</th>'
	html += '<th>' + '有效状态' + '</th>'
	html += '<th>' + '任务状态' + '</th>'
	html += '<th>' + '运行主机' + '</th>'
	html += '<th>' + '选中号码' + '</th>'
	html += '</tr>'


	type_len = len(type_user)
	for file_name in listfile:
		if len(file_name) > type_len and file_name.endswith(type_user):
			tempUser = config_user_get(file_name[:-5])
			if tempUser.get('yxzt','') != '0':
				tempUser['yxzt'] = '1'

			for key in form.keys():
				#print key ,tempUser.has_key(key)
				#print key
				if key == 'xzhm' and form.getvalue(key) != '' and tempUser[key] == '':
					break

				elif tempUser.has_key(key) and tempUser[key] != form.getvalue(key):
					break
				else:
					pass
			else:

				#print file_name[:-5]

				html += '<tr>'
				#html += '<td>' + '<a href="./config_page_load.py?clsbdh=' + file_name.split('.')[0] + '">' + '</td>'
				html += '<td>' + '<a href="./config_page_load.py?clsbdh=' + file_name.split('.')[0] + '">' +\
					tempUser['clsbdh'] + '</a>' + '</td>'
				html += '<td>' + tempUser.get('task_type','') + '</td>'
				html += '<td>' + tempUser.get('yxzt','') + '</td>'
				html += '<td>' + tempUser.get('status','') + '</td>'
				html += '<td>' + tempUser.get('hostname','') + '</td>'
				html += '<td>' + tempUser.get('xzhm','') + '</td>'

				html += '</tr>'

	else:
		html += '</table>'

	return html



def get_config_page(clsbdh):

	#查询用户
	user_conf  =  config_user_get(clsbdh)

	html = ''
	#error = ''

	try:
		#没有报错
		blrq_str = 	user_conf.get('blrq','')
		if blrq_str != '':
			blrq = time.strptime(blrq_str, "%Y-%m-%d")
			#print blrq
			if datetime.datetime(*blrq[0:6]) <=  \
				datetime.datetime(*(time.strptime(time.strftime('%Y-%m-%d',time.localtime(time.time())),"%Y-%m-%d"))[0:6]):
				user_conf['error'] = '办理日期必须晚于当天'
		else:
			pass
	except Exception,ex:
		user_conf['error'] = '日期配置错误'


	try:

		#user_conf_keys需要与网页定义的%s变量保持一致
		template_value = []	
		for user_conf_key in user_conf_keys:
			template_value.append(user_conf.get(user_conf_key,''))


		#html =  "Content-Type:text/html;charset=%s"+html_enter % 'UTF-8'
		s = ''
		with open('./template/conf_static.html','r') as conf_html:
			s = conf_html.read()
			conf_html.close()

		#解析soup
		soup = BeautifulSoup(s,"html",from_encoding='utf-8')

		#默认的下拉选项，待后续刷新

		status = user_conf.get('status','')
		#服务器处理运行或者异常状态,静态页面显示即可
		
		

		html =  soup.prettify() % tuple(template_value)


		
	except Exception,ex:
		#html =  "Content-Type:text/html;charset=%s\r\n"  % 'UTF-8'
		html = ex#'发生异常，请刷新网页重试' 
	finally:
		return html






#刷新任务状态，需要发送任务到select用户以及所有有效的query用户
def refresh_task(clsbdh,password_para):

	if password_para != password:
		print 'refresh_task:password error!' + password_para
		return

	#先获取用户配置
	user_infor = config_user_get(clsbdh)

	task_request = ''
	
	user_infor['select_user'] = user_infor['clsbdh']


	#无效任务不启动
	if user_infor.get('yxzt') != '0':
		print '任务状态无效'
		return

	#启动任务
	elif user_infor['status'] == 'running':
		task_request = 'start'
		data  = {
			'task_type':user_infor['task_type'],'handle_type':'start','user_info':user_infor
		}

	#停止任务
	elif user_infor['status'] == 'idle':
		task_request = 'stop'
		data  = {
			'task_type':user_infor['task_type'],
			'handle_type':'stop',
			'user_info':{
				'clsbdh':user_infor['clsbdh'],
				'hostname':user_infor['hostname'],
				'query_pc':user_infor['query_pc'],
			},
		}
	else:
		return



	addr_server = ('127.0.0.1',61236)

	#发送给中控服务进程
	send_with_ack(addr=addr_server,json_data=data)




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
			print 'cannot find the user',clsbdh
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






