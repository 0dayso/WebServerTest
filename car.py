#!/usr/bin/env python
#coding:utf-8


#导入html解析
from bs4 import BeautifulSoup

#http相关
#from httplib import HTTPConnection
from http.client import HTTPConnection
#from urllib import quote,urlencode,urlopen
from urllib.parse import  quote,urlencode
from urllib.request import urlopen

#导入requests库
import requests

#Gzip网页压缩
from io import StringIO
from gzip import GzipFile

from copy import deepcopy
from json import dumps,loads
from struct import pack

import time,re,urllib

from hashlib import md5
import  math


#号码过滤优选页面的号码图片图像识别
from net_threading import http_get_threading
import threading  
from  multiprocessing import Queue
#python 3.x
from queue import LifoQueue
from collections import deque

from socket import *
from net import *
from common import  *
from log import *

#dll处理模块
import ctypes

from os import path
import random




log_file = 'CAR  ' + time.strftime("%Y-%m-%d",time.localtime())



#城市链接
city_url = {
	'a.b':{
		'name':'main.aspx?str=513200|川U|阿坝藏族羌族自治州公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=513200|'+ quote('川') + 'U|' + quote('阿坝藏族羌族自治州公安局交通警察支队车辆管理所'),
	},
	'ba.z':{
		'name':'main.aspx?str=511900|川Y|巴中市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511900|'+ quote('川') + 'Y|' + quote('巴中市公安局交通警察支队车辆管理所'),
	},
	'cd':{
		'name':'/main.aspx?str=510100|川A|成都市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510100|'+ quote('川') + 'A|' + quote('成都市公安局交通警察支队车辆管理所'),
	},
	
	'da.z':{
		'name':'main.aspx?str=511700|川S|达州市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511700|'+ quote('川') + 'S|' + quote('达州市公安局交通警察支队车辆管理所'),
	},
	'de.y':{
		'name':'main.aspx?str=510600|川F|德阳市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510600|'+ quote('川') + 'F|' + quote('德阳市公安局交通警察支队车辆管理所'),
	},

	'gan.z':{
		'name':'main.aspx?str=513300|川V|甘孜藏族自治州公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=513300|'+ quote('川') + 'V|' + quote('甘孜藏族自治州公安局交通警察支队车辆管理所'),
	},

	'guang.a':{
		'name':'main.aspx?str=511600|川X|广安市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511600|'+ quote('川') + 'X|' + quote('广安市公安局交通警察支队车辆管理所'),
	},
	'guang.h':{
		'name':'main.aspx?str=510681|川F|广汉市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510681|'+ quote('川') + 'F|' + quote('广汉市公安局交通警察支队车辆管理所'),
	},
	'guang.y':{
		'name':'main.aspx?str=510800|川H|广元市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510800|'+ quote('川') + 'H|' + quote('广元市公安局交通警察支队车辆管理所'),
	},
	'le.s':{
		'name':'main.aspx?str=511100|川L|乐山市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511100|'+ quote('川') + 'L|' + quote('乐山市公安局交通警察支队车辆管理所'),
	},
	'liang.s':{
		'name':'main.aspx?str=513400|川W|凉山彝族自治州公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=513400|'+ quote('川') + 'W|' + quote('凉山彝族自治州公安局交通警察支队车辆管理所'),
	},
	'lu.z':{
		'name':'main.aspx?str=510500|川E|泸州市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510500|'+ quote('川') + 'E|' + quote('泸州市公安局交通警察支队车辆管理所'),
	},
	'mei.s':{
		'name':'main.aspx?str=511400|川Z|眉山市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511400|'+ quote('川') + 'Z|' + quote('眉山市公安局交通警察支队车辆管理所'),
	},
	'mian.y':{
		'name':'main.aspx?str=510700|川B|绵阳市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510700|'+ quote('川') + 'B|' + quote('绵阳市公安局交通警察支队车辆管理所'),
	},
	'nan.c':{
		'name':'main.aspx?str=511300|川R|南充市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511300|'+ quote('川') + 'R|' + quote('南充市公安局交通警察支队车辆管理所'),
	},
	'nei.j':{
		'name':'main.aspx?str=511000|川K|内江市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511000|'+ quote('川') + 'K|' + quote('内江市公安局交通警察支队车辆管理所'),
	},
	'pan.zh':{
		'name':'main.aspx?str=510400|川D|攀枝花市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510400|'+ quote('川') + 'D|' + quote('攀枝花市公安局交通警察支队车辆管理所'),
	},

	'sui.n':{
		'name':'main.aspx?str=510900|川J|遂宁市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510900|'+ quote('川') + 'J|' + quote('遂宁市公安局交通警察支队车辆管理所'),
	},
	'ya.a':{
		'name':'main.aspx?str=511800|川T|雅安市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511800|'+ quote('川') + 'T|' + quote('雅安市公安局交通警察支队车辆管理所'),
	},
	'yi.b':{
		'name':'main.aspx?str=511500|川Q|宜宾市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511500|'+ quote('川') + 'Q|' + quote('宜宾市公安局交通警察支队车辆管理所'),
	},
	'zi.g':{
		'name':'main.aspx?str=510300|川C|自贡市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=510300|'+ quote('川') + 'C|' + quote('自贡市公安局交通警察支队车辆管理所'),
	},
	'zi.y':{
		'name':'main.aspx?str=512000|川M|资阳市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=512000|'+ quote('川') + 'M|' + quote('资阳市公安局交通警察支队车辆管理所'),
	},
	'zi.z':{
		'name':'main.aspx?str=511025|川K|资中市公安局交通警察支队车辆管理所',
		'url':'/main.aspx?str=511025|'+ quote('川') + 'K|' + quote('资中市公安局交通警察支队车辆管理所'),
	},
}




#

get_car_url = '/zbhphm.aspx'



test = False

serachFlag = '____to_be_search_in_body'


#打印或者是记录日志
def debug(*args):
	if False:
		with open('./temp/log.txt','a') as file_log:
			json_temp = {
				'tieme':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
				'data':args
			}
			pickle.dump(json_temp,file_log)
	print (args)







class Plate(object):
	def __init__(self, userInfo, queue_in):

		# 可运行状态
		self.run_enable = True

		# 入参获取
		self.userInfo = userInfo
		# 固定变量
		self.userInfo['btnQuery'] = '查询'
		self.userInfo['chkOK'] = 'chkOK'

		self.query_index = '%3s' % self.userInfo.get('query_index', '')

		self.queue_in = queue_in

		# 读取文件配置参数
		self.__init_ini_para__()
		self.__counter__('INIT', 'INIT_INI_OK', 'HIGHT')

		# 相关参数配置
		self.__init_para__()
		self.__counter__('INIT', 'INIT_PARA_OK', 'HIGHT')

		# 切换用户信息，主要针对查询和测试用户
		self.__change_user_info__()

		# 网络相关参数
		self.__init_net__()
		self.__counter__('INIT', 'INIT_NET_OK', 'HIGHT')

		# 重要状态
		self.__init_status__()
		self.__counter__('INIT', 'INIT_STATUS_OK', 'HIGHT')

		# 列表转换，条件会动态更新
		self.__update_like_hate__()
		self.__counter__('INIT', 'INIT_UPDATE_OK', 'HIGHT')




	def __init_net__(self):

		# self.agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
		self.headers = {
			'User-Agent': random.choice([
				'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
				'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'])
			#'X-Forwarded-For': '10.230.200.183, 10.210.106.156',
		}

		#基本的定时
		self.timeout_http_base = 20
		self.timeout_http_post = 30
		self.timeout_http_get = 20

		#self.url_host = "http://www.scjj.gov.cn:121"
		self.url_host = "http://61.139.124.135:121"
		self.url_index = '/index.aspx'
		self.url_city = '/main.aspx?str=510100|' + quote('川') + 'A|' + quote('成都市公安局交通警察支队车辆管理所')
		self.url_city_referer = '/main.aspx?str=510100|川A|成都市公安局交通警察支队车辆管理所'

		self.url_zbhphm = '/zbhphm.aspx'
		self.url_yzm1 = '/yzm.aspx?r=1'
		self.url_yzm2 = '/yzm.aspx?r=2'
		# error_page并不是所有地方都需要重新登录

		self.url_xzhp = '/xzhp.aspx'
		self.url_error = 'Error......'  # 'ErrorPage'
		# 页面重定向
		self.body_redirect = '|pageRedirect||'

		# http会话
		self.session = requests.session()
		self.response = {}

		#self.session.mount('http://', SourceAddressAdapter('100.64.3.77'))
		#self.session.mount('http://', SourceAddressAdapter('192.168.0.105'))
		#self.session.mount(self.url_host + self.url_xzhp, SourceAddressAdapter('192.168.0.105'))


	# 所有用户的动态状态信息均在此处初始化
	def __init_status__(self):


		self.pause = False

		# http长连接，暂时不赋值

		# 查号相关
		self.yzm1 = ''
		self.img_codes = {}
		self.hidcxhp = ''
		self.xxxq = {}
		self.all_flag = False

		self.test_like_list = []

		#约号相关
		self.yzm2 = ''

		# 在线状态（如果需要重登陆，在线状态则为false
		self.status_online = False
		# 重要的当前页面最新状态，主要记录号牌和约号状态
		self.status_plate = status.INIT

		#登录初始化的时候会重新赋值
		self.time_login_start = time.time()
		#登录成功之后会重新赋值
		self.time_login_end = time.time()

		self.__init_time__()



	def __init_time__(self):

		#查询时间统计
		self.time_query_get_plate = 0
		#获取号牌时间统计
		self.time_query_get_hphm = 0

		#约号启动
		self.time_order_start = time.time()

		#提交查询条件开始
		self.time_query_post_hphm_start = time.time()
		#提交查询条件响应
		self.time_query_post_hphm_end = time.time()
		#获取号牌响应
		self.time_query_get_plate_end = time.time()

		#点击号牌开始
		self.time_get_handle_start = time.time()
		#点击号牌响应
		self.time_get_handle_end = time.time()

		self.time_get_finish_start = time.time()
		self.time_get_finish_end = time.time()
		self.time_post_fininsh_end = time.time()

		self.time_order_end = time.time()
		


	# 固定参数配置，只初始化1次，不会刷新
	def __init_para__(self):
		# hphm图片获取的并发数

		# 内部队列
		self.queue_user = {
			'queue_in_yzm': Queue(5),
			'queue_in_login': Queue(5),
			'queue_in_control':Queue(5),	#通知队列
			'queue_in_order': Queue(100), #可约号的请求
			'queue_in_plate': deque(maxlen=100),  # 预约号的队列，保持10个号足矣，先进后出，后到的优先处理
		}

		# 每个线程自己实体化数字和md5码
		self.fontTemplates = {}
		for i in '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ':
			with open('./img_code_src/' + str(i) + '.png', 'rb') as code_file:
				m = md5()
				m.update(code_file.read())
				code = m.hexdigest()
				self.fontTemplates[code] = str(i)

	# 文件配置参数获取
	def __init_ini_para__(self):

		try:
			# 加载系统配置
			self.configInfo = {}
			with open('./config/config.ini', 'r') as config_file:
				for line in config_file:
					if '=' in line:
						config_key = line.split('=')[0].strip()
						config_value = line.split('=')[1].strip()
						if config_key != '' and config_value != '':
							self.configInfo[config_key] = config_value

			self.addr_server_msg = (
				self.configInfo.get('server_host', 'www.wuyoubar.cn'), int(self.configInfo.get('sermsg_port', '61234')))

			self.addr_rasdial = ('127.0.0.1', int(self.configInfo.get('redial_port', '62235')))
			# 由car_process在多个yzm分析端口中调度一个给用户使用
			self.addr_yzm = ('127.0.0.1', int(self.userInfo.get('yzm_fx_port', '62237')))

			self.inter_select_test = int(self.configInfo.get('inter_select_test', '600'))

			self.debug = self.configInfo.get('debug', 'False')
			self.debug_html = self.configInfo.get('debug_html', 'False')

			self.timeout_login = int(self.configInfo.get('timeout_login', '90'))
			self.timeout_yzm1 = int(self.configInfo.get('timeout_yzm1', '150'))

			self.hphm_group_num = int(self.configInfo.get('hphm_group_num', '10'))

			#车牌号定时
			self.timeout_plate = int(self.configInfo.get('timeout_plate', '120'))

			#获取hphm的总时间
			self.timeout_hphm = int(self.configInfo.get('timeout_hphm', '60'))



		except Exception as ex:
			print_error("初始化过程中发生了异常", ex)
			return



	# 随机生成用户信息并本地替换
	def __change_user_info__(self):

		self.relogin_count = 0

		# 约号用户不能被替换,返回一个新数据供用户选择
		if self.userInfo['task_type'] == 'select':
			pass
			return

		# query或者select_test用户均自动修改资料

		clsbdh_old = self.userInfo['clsbdh']

		# 更换车牌到成功
		while self.userInfo['clsbdh'] == clsbdh_old or self.userInfo['clsbdh'] == '':
			try:

				self.userInfo['clsbdh'] = create_user_clsbdh()

				self.__counter__('USER', 'CHANGE', clsbdh_old, self.userInfo['clsbdh'])

				self.userInfo['tbSyr'] = ''
				for i in range(0, 5):
					self.userInfo['tbSyr'] += random.choice(list('ABCDEFGHJKLMNPRSTUVWXYZ'))

				self.userInfo['tbZjhm'] = ''
				for i in range(0, 18):
					self.userInfo['tbZjhm'] += random.choice(list('0123456789'))
				# self.userInfo['tbSyr'] = ''.join(random.sample('ABCDEFGHJKLMNPRSTUVWXYZ',5))
				# self.userInfo['tbZjhm'] = ''.join(random.sample(list('0123456789'),18))

				# 车辆型号更新
				self.userInfo['clxh'] = self.userInfo['clsbdh'][0:8]



			except Exception as ex:
				self.__counter__('USER', 'CHANGE', 'ERROR', clsbdh_old, self.userInfo['clsbdh'], ex)

		# test用户替换查找条件为最简单
		if self.userInfo['task_type'] == 'select_test':
			self.userInfo['like'] = '1,2'
			self.userInfo['hate'] = ''
			self.userInfo['xxxq'] = ''
			self.userInfo['gltj'] = ''
			self.userInfo['pctj'] = ''

	def __update_like_hate__(self):

		if self.userInfo['task_type'] == 'query' and 'select_user_dict' in self.userInfo:
			for select_user_key, select_user_info in self.userInfo['select_user_dict'].items():
				self.userInfo['like'] = select_user_info['like']
				self.userInfo['hate'] = select_user_info['hate']
				self.userInfo['xxxq'] = select_user_info['xxxq']
				break

		# 列表转换
		self.userInfo['like_list'] = [item.strip() for item in self.userInfo['like'].split(',') if item.strip() != '']
		self.userInfo['hate_list'] = [item.strip() for item in self.userInfo['hate'].split(',') if item.strip() != '']
		self.userInfo['xxxq_list'] = [item.strip() for item in self.userInfo['xxxq'].split(',') if item.strip() != '']
		self.userInfo['numb_list'] = list(set(self.userInfo['like_list']) | set(self.userInfo['hate_list']))

	# 直接根据用户信息刷新
	def __update__(self, userInfo):

		try:

			# key相等的时候刷新，主要用于部分刷新
			for key in userInfo.keys():
				self.userInfo[key] = userInfo[key]

			# 列表转换，刷新完毕之后列表转换
			self.__update_like_hate__()

			#self.__counter__('UPDATE', 'SUCCESS')
		except Exception as ex:
			self.__counter__('UPDATE', 'ERROR', ex)

	# 车牌号，过滤条件
	def __plate_is_ok__(self, plate, gltj='', pctj=''):

		#任意号码
		if plate == '.....':
			return True
		# query用户只关注当前的过滤条件
		if self.userInfo['task_type'] == 'query':
			like = self.userInfo['like_list']
			hate = self.userInfo['hate_list']
		# select用户只关注原始的过滤条件
		elif self.userInfo['task_type'] == 'select':
			gltj = self.userInfo['select_gltj']
			like = self.userInfo['select_like']
			hate = self.userInfo['select_hate']
			pctj = self.userInfo.get('select_pctj', '')
		elif self.userInfo['task_type'] == 'select_test':
			return True
		else:

			return False

		# 排除号
		if len(set(hate) & set(plate)) > 0:
			return False

		# 优选号和排除号条件Check
		plate_code = list(plate)
		for item in like:
			if item in plate_code:
				plate_code.remove(item)
			else:
				return False
		else:
			pass


		# 二维数组保存，第一级或条件，只要true就返回，第二级与条件，全部true
		gltj_list = [item.strip() for item in gltj.split('|')]
		pctj_list = [item.strip() for item in pctj.split('|')]

		num = '0123456789'
		word = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz'

		# 全字段匹配，按位比较
		def filter_all(plate, item):
			same_num = []
			same_word = []
			same = []
			# 按位匹配
			for i in range(0, 5):
				# 数字字母任意
				if item[i] == '.':
					continue


				# 数字限定,不满足条件则跳出
				elif item[i] == '%':
					if not plate[i] in num:
						# print plate[i],num
						break
					else:
						continue

				# 字母限定
				elif item[i] == '@':
					if not plate[i] in word:
						break
					else:
						continue

				# 数字字母相同
				elif item[i] == '#':
					same.append(plate[i])

				# 数字相同
				elif item[i] == '$':
					# 非数字，返回
					if plate[i] not in num:
						break
					same_num.append(plate[i])


				# 字母相同
				elif item[i] == '^':
					# 非字母，返回
					if plate[i] not in word:
						break

					same_word.append(plate[i])
				else:
					# 不等于普通字符，返回
					if item[i] != plate[i]:
						break

			else:
				# 同号条件满足,返回True
				if len(set(same)) <= 1 and len(set(same_word)) <= 1 and len(set(same_num)) <= 1:
					return True

			return False

		# 部分字段比较
		def filter_sub(plate, item):
			# 两个特征自己必须隔开
			if '+' in item:
				# 两个
				add_items = [temp_item.strip() for temp_item in item.split('+')]
				# +只允许连接两个元素
				if len(add_items) != 2:
					return False
				# 条件不满足在
				elif not add_items[0] in plate or not add_items[1] in plate or \
										add_items[0] + add_items[1] in plate:
					return False
				# '+'条件过滤满足
				else:
					return True

			# 两个特征字符之间的任务间隔
			elif '.' in item:
				add_items = [temp_item.strip() for temp_item in item.split('.')]
				# .只允许连接两个元素
				if len(add_items) != 2:
					return False
				for add_item in add_items:
					# 不满足
					if not add_item in plate:
						return False

				# 条件过滤最终满足
				else:
					return True

			# 同一个号码或者字符出现次数，主要针对三同场景
			elif '*' in item:
				same_items = [temp_item.strip() for temp_item in item.split('*')]

				if len(same_items) != 2:
					return False

				if plate.count(same_items[0]) != int(same_items[1]):
					return False
				else:
					return True
			else:
				if item in plate:
					return True
				else:
					return False

		# 多条件过滤，不支持括号
		def filter_list_gl(plate, tj_list):
			# 外层 or条件遍历
			for or_item in tj_list:

				and_list = [item_temp.strip() for item_temp in or_item.split('&')]

				# and_list遍历
				for item in and_list:

					# 条件为空
					if item is None or item.strip() == '':
						continue

					len_item = len(item.strip())
					# print  len_item, and_list
					# 按位过滤匹配
					if len_item == 5:

						# 正向或者反向过滤匹配成功
						if filter_all(plate, item):
							continue
						else:
							break

						# 程序运行到此处，and条件已经判定为false
					elif len_item > 0:

						if filter_sub(plate, item):
							continue
						else:
							break
					else:
						# print  'error',tj_list
						continue

					# 有一个条件不满足False，则这一组and_list不再判断
					break

				# 完成之后，整个队列结果是True，则返回；如果是false，则遍历下一个or_item
				else:
					return True

				# or_item继续遍历
				continue

			# 所有or_item均没有成功,正向查找则条件不满足，返回false；排除查找不满足条件，则返回True
			else:
				return False

		def filter_list_pc(plate, tj_list):
			# 外层 or条件遍历
			for or_item in tj_list:

				and_list = [item_temp.strip() for item_temp in or_item.split('&')]

				# and_list遍历
				for item in and_list:

					# 条件为空
					if item is None or item.strip() == '':
						continue

					len_item = len(item.strip())

					# print  len_item, and_list

					# 按位过滤匹配
					if len_item == 5:

						# 正向或者反向过滤匹配成功
						if filter_all(plate, item):
							return False
						else:
							continue

						# 程序运行到此处，and条件已经判定为false
					elif len_item > 0:
						# print  'error', and_list
						if filter_sub(plate, item):
							return False
						else:
							continue
					else:
						# print  'error',tj_list
						continue

					# 有一个条件不满足False，则这一组and_list不再判断
					break

				# 完成之后，整个队列结果是True，则返回；如果是false，则遍历下一个or_item
				else:
					continue

				# or_item继续遍历
				continue

			# 所有or_item均没有成功,正向查找则条件不满足，返回false；排除查找不满足条件，则返回True
			else:
				return True

		return filter_list_gl(plate, gltj_list) and filter_list_pc(plate, pctj_list)

	def __plate_is_good_(self, plate):
		# 统计样本
		count = {}
		# 三同
		for code in plate:
			if code in count.keys():
				count[code] += 1
			else:
				count[code] = 1

			# 3重号直接返回
			if count[code] == 3:
				return True

		# 号牌排序
		keys = sorted(count.keys())
		keys_len = len(keys)
		for index in range(0, keys_len):
			if index > 1 and index < keys_len - 1:
				# 678顺子构造，或者是abc字母顺序构造
				if (ord(keys[index]) - ord(keys[index - 1])) * (ord(keys[index]) - ord(keys[index + 1])) == -1:
					return True

	# 关键信息统计
	def __counter__(self, *counter_value):

		# 识别代号永远都存在
		counter_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ',' + self.userInfo['clsbdh'] + ','
		if self.userInfo['task_type'] == 'query' or self.userInfo['task_type'] == 'select_test':
			counter_str += str(self.userInfo.get('query_index', 'query_user')) + ','

		for counter_item in counter_value:
			counter_str += str(counter_item) + ','

		else:
			counter_str = counter_str[:-1] + '\n'

		if self.userInfo['task_type'] == 'query' or self.userInfo['task_type'] == 'select_test':
			counter_name = self.userInfo['task_type'] + ' ' + time.strftime("%Y-%m-%d", time.localtime())
		else:
			counter_name = self.userInfo['task_type'] + ' ' + self.userInfo['clsbdh'] + ' ' + time.strftime("%Y-%m-%d",
																											time.localtime())

		if self.userInfo['task_type'] == 'select' or self.userInfo['task_type'] == 'select_test' or \
								self.userInfo['task_type'] == 'query' and \
						(self.configInfo.get('debug_query', '') == 'True' or self.configInfo.get('debug_query',
																								 '') == 'true' or \
									 'HIGHT' in counter_value):
			with open('./temp/' + counter_name, 'a') as counter_log:
				counter_log.write(counter_str)

			# 界面打印屏蔽
			# print counter_str

	# 需要专门开启后台进程发送消息，否则可能影响约号速度
	def __debug_select__(self, *counter_value):
		if self.userInfo.get('task_type') == 'select':

			print_debug(self.userInfo.get('clsbdh', ''), counter_value)

			# 带时间戳
			text = str(time.strftime("%H:%M:%S ", time.localtime()))
			for item in counter_value:
				text += ',' + str(item)
			json_temp = {
				'task_type': 'log',
				'handle_type': 'report',
				'user_info': {
					'clsbdh': self.userInfo.get('clsbdh', 'unknown user'),
					'text': text
				}
			}

			send_with_ack(self.addr_server_msg, json_temp)

	def __record_plate__(self, *counter_value):

		print_infor(*counter_value)

		counter_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ',' + self.userInfo['clsbdh'] + ','



		for counter_item in counter_value:
			counter_str += str(counter_item) + ','

		else:
			counter_str = counter_str[:-1] + '\n'

		counter_name = 'PLATE ' + time.strftime("%Y-%m-%d", time.localtime())

		if True:
			with open('./temp/' + counter_name, 'a') as counter_log:
				counter_log.write(counter_str)

			# print counter_str

	# 判断是否需要重新登录，只是判断结果，但不进行重登陆
	def __is_offline__(self, response=None):
		if response is None:
			if not self.status_online:
				return True
			else:
				return False

		if response.status_code == 500 or self.url_index in response.url or \
						self.url_error in response.url:
			self.response = response
			# 离线了
			self.status_online = False
			return True

		elif self.url_index in response.text:
			self.response = response
			# 离线了
			self.status_online = False
			return True

		else:
			return False

	#封装httpget，主要是控制http get
	def __http_get__(self,url,headers,timeout=None,allow_redirects=True):

		#暂停
		while self.pause:
			self.__counter__('HTTP_GET','PAUSE','HIGHT')
			time.sleep(5)

		#self.__get_token__('127.0.0.1',62262)

		if timeout is None:
			timeout = self.timeout_http_get
		try:
			response = self.session.get(url, headers=headers,
										 timeout=timeout,allow_redirects=allow_redirects)
		except Exception as ex:
			#print_debug('HTTP_GET异常',ex)
			response = None

		return response

	def __http_get_threading__(self,queue_out,url,headers,timeout=None,allow_redirects=True):
		# 暂停
		while self.pause:
			self.__counter__('HTTP_POST', 'PAUSE', 'HIGHT')
			time.sleep(5)

		try:
			response = self.__http_get__(url, headers=headers,timeout=timeout, allow_redirects=allow_redirects)
			if response:
				try:
					json_result = {}
					json_result['status_code'] = response.status_code
					if response.status_code == 302:
						json_result['location'] = response.headers['location']
						json_result['url'] = response.url
						json_result['text'] = response.text
					elif response.status_code == 200:
						json_result['text'] = response.text
						json_result['url'] = response.url

					queue_out.put(json_result, True, 1)
				except Exception as ex:
					queue_out.put(False, True, 1)

		except Exception as ex:
			try:
				queue_out.put(False,True,1)
			except Exception as ex:
				pass

	def __http_post__(self,url,data,headers,timeout=None,allow_redirects=True):
		# 暂停
		while self.pause:
			self.__counter__('HTTP_POST', 'PAUSE', 'HIGHT')
			time.sleep(5)

		#self.__get_token__('127.0.0.1', 62263)

		if timeout is None:
			timeout = self.timeout_http_post

		try:
			response = self.session.post(url, data=data, headers=headers,
											  timeout=timeout,allow_redirects=allow_redirects)
		except Exception as ex:
			response = None

		finally:
			return response

	def __http_post_threading__(self,queue_out,url,data,headers,timeout,allow_redirects):
		# 暂停
		while self.pause:
			self.__counter__('HTTP_POST', 'PAUSE', 'HIGHT')
			time.sleep(5)
		try:
			response = self.__http_post__(url,data,headers,timeout=timeout,allow_redirects=allow_redirects)
			if response:
				try:
					json_result = {}
					json_result['status_code'] = response.status_code
					if response.status_code == 302:
						json_result['location'] = response.headers['location']
					json_result['url'] = response.url
					json_result['text'] = response.text
					queue_out.put(json_result, True, 1)
				except Exception as ex:
					queue_out.put(False, True, 1)
		except Exception as ex:
			try:
				queue_out.put(False,True,1)
			except Exception as ex:
				pass

	# 判断是否需要重新登录，如果需要重新登录，直接重登陆
	def __retry_with_login__(self):
		try:
			if self.__is_offline__():
				self.__relogin__()
				return True
			else:
				return False
		except Exception as ex:
			self.__counter__('RETRY', 'RELOGIN', 'ERROR', ex)
			return False

	def __relogin__(self):

		# 最终到注册提交之后重定向的页面
		def __login__():

			self.__get_token__('127.0.0.1',62259)

			try:
				if 'Referer' in self.headers:
					del self.headers['Referer']
			except Exception as ex:
				pass

			############################################################################
			# 【1】Index页面获取Cookie
			############################################################################
			"""try:

				if 'Referer' in self.headers:
					del self.headers['Referer']

				self.response = self.__http_get__(self.url_host + self.url_index, headers=self.headers,timeout=self.timeout_http_get)

				if self.response.status_code != 200:
					self.__debug_select__('1.主页获取失败', self.response.status_code)
					self.__counter__('LOGIN', 'FAIL', '1.GET_MAIN', self.response.status_code, 'HIGHT')
					return False
			except Exception as ex:
				self.__debug_select__('1.主页获取异常', ex)
				self.__counter__('LOGIN', 'ERROR', '1.GET_MAIN', 'ERROR', ex, 'HIGHT')
				return False

			self.__debug_select__('1.主页获取成功')"""
			############################################################################
			# 【2】跳转到成都页面,referer = /main.aspx?str=510100|川A|成都市公安局交通警察支队车辆管理所
			############################################################################
			try:
				self.headers['Referer'] = self.url_host + self.url_index
				self.response = self.__http_get__(self.url_host + self.url_city, headers=self.headers,timeout=self.timeout_http_get)
				if self.response.status_code != 200 or self.__is_offline__(self.response):
					self.__debug_select__('2.成都页面获取失败', self.response.status_code)
					self.__counter__('LOGIN', 'FAIL', '2.GET_CITY', self.response.status_code, self.response.url,
									 'HIGHT')
					return False
			except Exception as ex:
				self.__debug_select__('2.成都页面获取异常', ex)
				self.__counter__('LOGIN', 'ERROR', '2.GET_CITY', 'ERROR', ex, 'HIGHT')
				return False

			self.headers['Referer'] = (self.url_host + self.url_city_referer).encode().decode('latin-1')
			self.__debug_select__('2.成都页面获取成功')

			time.sleep(5)
			############################################################################
			# 【3】post main.aspx重定向到/cd_chose.aspx,refer更新到/cd_chose.aspx
			############################################################################
			def __login_post_agree__():

				try:
					# 获取action和其他三个参数
					soup = BeautifulSoup(self.response.text, "html.parser")  # ,from_encoding='utf-8')

					# action头/不存在
					action = '/' + soup.find(id='form1').get('action', '')

					if action == '':
						self.__counter__('POST', 'CITY', 'ACTION_NULL',  'HIGHT')
						return False

					postJson = get_value_from_body(self.response.text, {
						"__VIEWSTATE": serachFlag,
						"agree": "同意",
						"__EVENTVALIDATION": serachFlag,
					})
					headers = deepcopy(self.headers)
					headers["Content-Type"] = "application/x-www-form-urlencoded"

					# self.__counter__('POST', 'CITY', 'POST', 'TRY', 'HIGHT')
					self.response = self.__http_post__(self.url_host + action, data=postJson, headers=headers,timeout=self.timeout_http_post)
					return True
				except Exception as ex:
					self.__counter__('POST', 'CITY', 'ERROR', ex, 'HIGHT')
					return False

			# 【3】post main.aspx重定向到/cd_chose.aspx,refer更新到/cd_chose.aspx
			try:
				if __login_post_agree__() and '_chose' in self.response.url:
					self.__counter__('LOGIN', 'PASS', '3.POST_MAIN')
					self.__debug_select__('3.城市选择成功')
					pass
				else:
					self.__debug_select__('3.城市选择失败')
					self.__counter__('LOGIN', 'ERROR', '3.POST_MAIN', 'FAIL','HIGHT')
					return False
			except Exception as ex:
				self.__debug_select__('3.城市选择异常', ex)
				self.__counter__('LOGIN', 'ERROR', '3.POST_MAIN', 'ERROR', ex, 'HIGHT')
				return False

			self.headers['Referer'] = self.response.url

			############################################################################
			# 【4】post cd_chose.aspx重定向到/cd1_one.aspx,refer更新到/cd1_one.aspx
			############################################################################
			try:
				postJson = get_value_from_body(self.response.text, {"__VIEWSTATE": serachFlag,
																	"firstChoose": "",  # 选择第一个,新车
																	"__EVENTVALIDATION": serachFlag})

				headers = deepcopy(self.headers)
				headers["Content-Type"] = "application/x-www-form-urlencoded"
				self.response = self.__http_post__(self.response.url, data=postJson, headers=headers,timeout=self.timeout_http_post)
				if self.response.status_code == 200 and '_one' in self.response.url:
					self.__debug_select__('4.新车二手车选择成功')
					pass
				else:
					self.__debug_select__('4.新车二手车选择失败')
					return False

				self.headers['Referer'] = self.response.url
			except Exception as ex:
				self.__debug_select__('4.新车二手车选择异常', ex)
				return

			############################################################################
			# 【5】post cd1_one.aspx重定向到/cd1_two.aspx,refer更新到/cd1_two.aspx
			############################################################################
			try:
				postJson = get_value_from_body(self.response.text, {"__VIEWSTATE": serachFlag,
																	"__EVENTVALIDATION": serachFlag,
																	"clsbdh": self.userInfo['clsbdh'],
																	# "S2DA15091F253103K",#车辆识别代号
																	"clxh": self.userInfo['clxh'],  # "S2DA1509",#车辆型号
																	"btnSelect": self.userInfo['btnQuery'],
																	# "查询",#按钮的label名称 查询，返回
																	"rdclxz": self.userInfo['rdclxz'],
																	# 国产还是进口车,国产-1，进口-2
																	})

				headers = deepcopy(self.headers)
				headers["Content-Type"] = "application/x-www-form-urlencoded"
				self.response = self.__http_post__(self.response.url, data=postJson, headers=headers,timeout=self.timeout_http_post)
				if self.response.status_code == 200 and '_two' in self.response.url:
					self.__debug_select__('5.车架号车型基本信息提交成功')
					pass


				# 已经编号页面
				# 此机动车已于2016-7-9 23:32:10 由 黎阳 自主编号!
				# query用户，对于select用户
				elif re.search('此机动车已于.*由.*自主编号', self.response.text) is not None:
					self.__debug_select__('5.车架号车型基本信息提交失败，该车已经选中号码')

					if self.userInfo.get('task_type') == 'select':
						order_result = {
							'task_type': 'order',
							'handle_type': 'response',
							'user_info': {
								'clsbdh': self.userInfo.get('clsbdh', ''),
								'result': 'success',
								'xzhm': '请上网查询',
							}
						}
						self.run_enable = False
						try:
							# 选号成功，通知服务器
							send_with_ack(self.addr_server_msg, order_result)
						except Exception as ex:
							self.__counter__('ORDER_RUN', 'POST_FINISH', 'NOTIFY_ERROR', ex)

					else:
						self.__change_user_info__()
					return False
				else:
					self.__debug_select__('5.车架号车型基本信息提交失败', self.response.status_code)
					self.__counter__('LOGIN', 'FAIL', '5.POST_CD1_ONE', self.response.status_code, 'HIGHT')
					return False

				self.headers['Referer'] = self.response.url
			except Exception as ex:
				self.__debug_select__('5.车架号车型基本信息提交异常', ex)
				return False

			############################################################################
			# 【6】post cd1_two.aspx生成生成日期和地点页面
			############################################################################

			def __login_post_addr_info__():
				try:
					# 查询或者约号测试用户，自动获取办理日期，默认最近一天
					# if self.userInfo.get('blrq') == '':
					# 每次都更新查询
					if self.userInfo.get('task_type') == 'query':
						soup = BeautifulSoup(self.response.text, "html.parser")
						blrq = soup.find(id='blrq')
						if blrq == None:
							self.__counter__('GET', 'BLRQ', 'BODY', 'FAIL', 'HIGHT')
							return False

						options = blrq.find_all('option')
						if len(options) > 2:
							self.userInfo['blrq'] = options[2].get('value')
						elif len(options) > 0:
							self.userInfo['blrq'] = options[0].get('value')
						else:
							self.__counter__('GET', 'BLRQ', 'OPTION', 'FAIL', 'HIGHT')
							return False

					postJson = get_value_from_body(self.response.text, {
						"__EVENTTARGET": serachFlag,
						"__EVENTARGUMENT": serachFlag,
						"__LASTFOCUS": serachFlag,
						"__VIEWSTATE": serachFlag,
						"__EVENTVALIDATION": serachFlag,
						"bldd": self.userInfo['bldd'],  # "510100",#办理地点
						"blrq": self.userInfo['blrq'],  # "2016-06-20",#办理日期
						"btnSelect": self.userInfo['btnQuery'],  # "查询",#按钮的label名称 查询，返回
					})

					headers = deepcopy(self.headers)
					headers["Content-Type"] = "application/x-www-form-urlencoded"
					self.response = self.__http_post__(self.response.url, data=postJson, headers=headers,timeout=self.timeout_http_post)
					return True
				except Exception as ex:
					self.__counter__('LOGIN', 'ERROR', '6.POST_CD1_TOW', ex, 'HIGHT')
					return False

			try:
				if not __login_post_addr_info__():
					self.__debug_select__('6.查询日期和车管所失败', self.response.status_code, self.response.url)
					self.__counter__('LOGIN', 'FAIL', '6.POST_CD1_TOW', self.response.status_code, self.response.url,
									 'HIGHT')
					return False
			except Exception as ex:
				self.__counter__('LOGIN', 'ERROR', '6.POST_CD1_TOW', ex, 'HIGHT')
				self.__debug_select__('6.查询日期和车管所异常', ex)

			self.__counter__('LOGIN', 'PASS', '6.POST_CD1_TOW')
			self.__debug_select__('6.查询日期和车管所成功')

			# referer暂时不用更新
			# return False

			############################################################################
			# 【7】get cd_reginfo 网页链接在界面上提供，格式如下
			# <a href="cd_reginfo.aspx?slrq=2016-06-27&slcc=1&keyword=6583C8834091833EDB7B9FD0DDB2F210">选择</a>
			############################################################################
			def __login_get_reg_info__():
				try:
					# 更新关键字
					soup = BeautifulSoup(self.response.text, "html.parser")
					a_list = soup.find_all('a')
					url = ''
					for a_item in a_list:
						href = a_item.get('href', '')
						# print a_item
						if href.startswith('cd_reginfo.aspx'):
							url = '/' + href
							break

					if not url.startswith('/cd_reginfo.aspx'):
						self.__counter__('LOGIN', 'FAIL', '7.GET_CD_REG', 'GET_URL_FAIL', 'HIGHT')
						return False

					self.response = self.__http_get__(self.url_host + url, headers=self.headers,timeout=self.timeout_http_get)
					if self.response.status_code == 200:
						return True
					else:
						self.__counter__('LOGIN', 'FAIL', '7.GET_CD_REG', self.response.status_code, 'HIGHT')
						return False
				except Exception as ex:
					self.__counter__('LOGIN', 'ERROR', '7.GET_CD_REG', ex, 'HIGHT')
					return False

			try:
				if not __login_get_reg_info__() or not '_reginfo' in self.response.url:
					self.__counter__('LOGIN', 'FAIL', '7.GET_CD_REG', self.response.url, 'HIGHT')
					self.__debug_select__('7.获取注册页面失败', self.response.url)
					return False
			except Exception as ex:
				self.__counter__('LOGIN', 'ERROR', '7.GET_CD_REG', ex, 'HIGHT')
				self.__debug_select__('7.获取注册页面异常', ex)
				return False

			self.headers['Referer'] = self.response.url
			self.__counter__('LOGIN', 'PASS', '7.GET_CD_REG')
			self.__debug_select__('7.获取注册页面正常')

			############################################################################
			# 【8】post cd_reginfo.aspx生成预约界面的列表，更换证件号码需要post;zbhphm
			############################################################################
			def __login_post_reg_info__():
				try:
					ddlZjzl = self.userInfo.get('ddlZjzl')
					if ddlZjzl != 'A':

						# 更换
						postJson = get_value_from_body(self.response.text, {
							"__EVENTTARGET": "ddlZjzl",
							"__EVENTARGUMENT": serachFlag,
							"__LASTFOCUS": serachFlag,
							"__VIEWSTATE": serachFlag,
							"__EVENTVALIDATION": serachFlag,
							"tbCjh": self.userInfo['clsbdh'],  # "S2DA15091F253103K",#车辆识别代号/车架号
							"tbQrCjh": self.userInfo['clsbdh'],  # "S2DA15091F253103K",#确认车辆识别代号/车架号
							"rdclxz": self.userInfo['rdclxz'],  # 国产还是进口车,国产-1，进口-2
							"tbClxh": self.userInfo['clxh'],  # "S2DA1509",#车辆型号
							"tbFdjh": self.userInfo['tbFdjh'],  # "CAM1E65F",#发动机号
							"tbFpbh": self.userInfo['tbFpbh'],  # "11132122",#发票编号
							"tbQrFpbh": self.userInfo['tbFpbh'],  # "11132122",#确认发票编号


							"tbSyr": self.userInfo['tbSyr'],  # "fsfsfs",#所有人姓名/名称
							"ddlZjzl": self.userInfo['ddlZjzl'],  # "A",#证件种类
							"tbZjhm": "",  # "513011111111111111",#证件号码
							"tbCfZjhm": "",  # "513011111111111111",#确认证件号码
							"tbZzzh": "",  # 暂住证号码
							"ddlXzhq": self.userInfo['ddlXzhq'],  # "510100",#行政区划

							"tbDz": "",  # "四川省双流县临港路四段9号",#住所地址
							"txtyzbm": "",  # "610064",#邮政编码
							# "chkOK":"on",#self.userInfo['chkOK'], #确定所填信息已完全正确
							# "btnSelect":"查询",# "查询",#按钮的label名称 查询，返回
						})

						headers = deepcopy(self.headers)
						headers["Content-Type"] = "application/x-www-form-urlencoded"
						self.response = self.__http_post__(self.response.url, data=postJson, headers=headers,timeout=self.timeout_http_post)

						if self.response.status_code != 200:
							self.__counter__('POST', 'CD_REGINFO', 'CHANGE', 'CHANGE_FAIL', self.response.status_code,
											 'HIGHT')
							return False
						else:
							pass

					# else:
					postJson = get_value_from_body(self.response.text, {
						"__EVENTTARGET": serachFlag,
						"__EVENTARGUMENT": serachFlag,
						"__LASTFOCUS": serachFlag,
						"__VIEWSTATE": serachFlag,
						"__EVENTVALIDATION": serachFlag,
						"tbCjh": self.userInfo['clsbdh'],  # "S2DA15091F253103K",#车辆识别代号/车架号
						"tbQrCjh": self.userInfo['clsbdh'],  # "S2DA15091F253103K",#确认车辆识别代号/车架号
						"rdclxz": self.userInfo['rdclxz'],  # 国产还是进口车,国产-1，进口-2
						"tbClxh": self.userInfo['clxh'],  # "S2DA1509",#车辆型号
						"tbFdjh": self.userInfo['tbFdjh'],  # "CAM1E65F",#发动机号
						"tbFpbh": self.userInfo['tbFpbh'],  # "11132122",#发票编号
						"tbQrFpbh": self.userInfo['tbFpbh'],  # "11132122",#确认发票编号


						"tbSyr": self.userInfo['tbSyr'],  # "fsfsfs",#所有人姓名/名称
						"ddlZjzl": self.userInfo['ddlZjzl'],  # "A",#证件种类
						"tbZjhm": self.userInfo['tbZjhm'],  # "513011111111111111",#证件号码
						"tbCfZjhm": self.userInfo['tbZjhm'],  # "513011111111111111",#确认证件号码
						"ddlXzhq": self.userInfo['ddlXzhq'],  # "510100",#行政区划

						"tbDz": self.userInfo['tbDz'],  # "四川省双流县临港路四段9号",#住所地址
						"txtyzbm": self.userInfo['txtyzbm'],  # "610064",#邮政编码
						"chkOK": "on",  # self.userInfo['chkOK'], #确定所填信息已完全正确
						"btnSelect": "查询",  # "查询",#按钮的label名称 查询，返回
					})

					if ddlZjzl == 'A':
						postJson["tbZzzh"] = self.userInfo.get('tbZzzh', '')
					# 如果是B类型，需要先提交一次
					if ddlZjzl == 'B':
						postJson['tbDlr'] = '李明'
						postJson['tbDlrSfzhm'] = '510029198904083146'
						postJson['tbDlrlxdh'] = '13812345678'
						postJson['tbDlrdz'] = '四川省成都市'

					else:
						postJson["tbZzzh"] = self.userInfo.get('tbZzzh', '')  # "",#暂住证号

					headers = deepcopy(self.headers)
					headers["Content-Type"] = "application/x-www-form-urlencoded"
					self.response = self.__http_post__(self.response.url, data=postJson, headers=headers)

					if self.response.status_code != 200:
						self.__counter__('POST', 'CD_REGINFO', 'REGISTER', 'FAIL', self.response.status_code, 'HIGHT')
						return False
					else:
						return True

				except Exception as ex:
					self.__counter__('POST', 'CD_REGINFO', 'REGISTER', 'ERROR', ex, 'HIGHT')
					return False

			try:
				if not __login_post_reg_info__() or 'xzhphm.aspx' in self.response.url:
					self.__counter__('POST', 'FAIL', '8.POST_CD_REG', self.response.status_code,
									 self.response.url, 'HIGHT')
					self.__debug_select__('8.提交注册页面失败', self.response.status_code, self.response.url)
					return False
				else:
					# 更新Referer
					self.headers['Referer'] = self.response.url
					self.__counter__('LOGIN', 'PASS', '8.POST_CD_REG')
					self.__debug_select__('8.提交注册页面成功')
					return True

			except Exception as ex:
				self.__debug_select__('8.提交注册页面异常', ex)
				self.__counter__('LOGIN', 'ERROR', '8.POST_CD_REG', ex, 'HIGHT')
				return False

		self.__counter__('RELOGIN', 'ENTER', 'HIGHT')
		self.__debug_select__('重新登录')

		while self.run_enable:
			try:
				# 登录网页相关状态清除重置
				self.__init_status__()

				# 记录用户重登陆次数，如果次数超过多少次，替换用户
				self.relogin_count += 1
				self.time_login_start = time.time()
				#self.__counter__('RELOGIN', 'START', self.relogin_count, 'HIGHT')

				# 重新登录
				if not __login__():
					self.__counter__('RELOGIN', 'FAIL', 'HIGHT')
					self.__debug_select__('登录失败，等待2s之后再重新登录')
					time.sleep(2)
					continue
				# 登录成功
				else:
					self.time_login_end = time.time()
					#self.__counter__('RELOGIN', 'SUCCESS', self.time_login_end - self.time_login_start , 'HIGHT')
					self.__debug_select__('登录成功，共耗时', '%.3f' %  (self.time_login_end - self.time_login_start) )
					# 登录成功，在线状态设置为True
					self.status_online = True
					return


			except Exception as ex:
				self.__counter__('RELOGIN', 'ERROR', ex, 'HIGHT')
				self.__debug_select__('登录过程发生异常，等待2秒后接入', ex)
				time.sleep(2)
				pass

	def __get_token__(self,server, port):
		# query用户获取查询号码的token
		if self.userInfo['task_type'] == 'query':

			first = True
			while True:
				try:
					# 本地直接发送给Select用户进行约号
					tcp = socket(AF_INET, SOCK_STREAM)
					tcp.settimeout(3)
					# dumps data转换成网络数据发送格式
					addr_query_token = (server, port)
					tcp.connect(addr_query_token)

					#第一次
					if first:
						json_token_request = {
							'index':self.query_index,
							'hphm':self.time_query_get_hphm,
							'plate':self.time_query_get_plate,
						}
					else:
						json_token_request = {
							'index': self.query_index
						}
					tcp.send(dumps(json_token_request).encode())
					first = False
					if tcp.recv(512).decode() == 'ACK':
						return
					else:
						pass
						#print_debug('获取Token失败')
				except Exception as ex:
					self.__counter__('GET_TOKEN','ERROR',ex)
					pass
					#print_debug('获取Token异常',ex)
				finally:
					time.sleep(0.5)

	#sn = 1 表示获取码1，sn为2时表示获取码2
	def __get_yzm_from_url__(self, sn='1'):

		# 验证码识别
		BOM = b'\xef\xbb\xbf'
		existBom = lambda s: True if s == BOM else False
		headers = deepcopy(self.headers)

		if sn == '1':
			if self.yzm1 == '':
				headers['Referer'] = self.url_host + self.url_zbhphm
				url = self.url_yzm1
			else:
				return True
		elif sn == '2':
			if self.yzm2 == '':
				headers['Referer'] = self.url_host +  '/finish.aspx'
				url = self.url_yzm2
			else:
				return True
		else:
			return False


		# 循环获取验证码直到成功，先获取照片，然后发送给识别进程
		while self.run_enable:

			# 验证码一直重试
			count = 0
			while self.run_enable:
				count += 1
				try:
					response = self.__http_get__(url=self.url_host + url, headers=headers, timeout=self.timeout_http_get,allow_redirects=False)
				except Exception as ex:
					self.__counter__('YZM', 'GET',sn, 'ERRER', ex,'HIGHT')
					self.__debug_select__('下载验证码异常',sn,ex)
					time.sleep(2)
					continue

				# 判断您是否需要重新登录
				if self.__is_offline__(response):
					return False
				try:
					if response and response.status_code == 200:
						break
					else:
						self.__debug_select__('下载验证码失败', sn,response.status_code, response.url)
						self.__counter__('YZM', 'GET', 'FAIL', response.status_code, response.url, 'HIGHT')
						continue
				except Exception as ex:
					self.__counter__('YZM', 'GET', 'ERROR', ex, 'HIGHT')
					continue

			# bmp的图片暂时重新获取，更换
			if len(response.content) > 270000:
				continue


			yzm_data = b''

			# 调用本地验证码识别软件
			try:

				# select用户编码
				if self.userInfo['task_type'] == 'select':
					while True:
						try:
							id_fmt = '!18s'
							str_header = self.userInfo.get('clsbdh', '01234567890123456') + sn
							id_binary = pack(id_fmt, str_header.encode())
							# response.content = id_binary + response.content
							self.__counter__('YZM', 'TRY', self.addr_yzm[1])

							tcp = socket(AF_INET, SOCK_STREAM)
							tcp.connect(self.addr_yzm)
							tcp.send(id_binary + response.content)
							yzm_data = tcp.recv(512)
							break
						except Exception as ex:
							self.__counter__('YZM', 'GET', 'FAIL', 'LOCAL', 'ERROR', ex, self.addr_yzm, 'HIGHT')
							time.sleep(5)
							pass
				# query用户采用udp方式发送
				elif self.userInfo['task_type'] == 'query':
					while True:

						try:
							udp = socket(AF_INET, SOCK_DGRAM)
							udp.settimeout(40)
							udp.bind(('', 0))
							if self.configInfo.get('yzm_fx_mod') == 'local':
								udp.sendto(response.content, self.addr_yzm)
							else:
								udp.sendto(response.content, (self.configInfo.get('yzm_fx_server_addr',self.addr_yzm[0]),
															  int(self.configInfo.get('yzm_fx_server_port',self.addr_yzm[1]))))
							yzm_data = udp.recv(512)
							udp.shutdown(SHUT_RDWR)
							udp.close()
							# 成功解析
							break

						except Exception as ex:
							self.__counter__('YZM', 'GET', 'FAIL', 'LOCAL', 'ERROR', ex, self.addr_yzm, 'HIGHT')
							time.sleep(20)
							continue
					else:
						udp.shutdown(SHUT_RDWR)
						udp.close()
				else:
					self.__counter__('YZM', 'GET', 'ERROR_TYPE', self.userInfo.get('task_type', ''), 'HIGHT')
					return False

				yzm = yzm_data.decode('gbk')

				# 验证码为空或者解析失败，重新获取
				if yzm == '0000' or yzm == '':
					self.__counter__('YZM', 'GET', 'FAIL', 'LOCAL', yzm, yzm_data, 'HIGHT')
					self.__debug_select__('码1解析失败，需要重新解析', yzm)
					time.sleep(1)
					yzm = ''
					continue
				else:
					self.__counter__('YZM', 'FX', 'SUCCESS', 'LOCAL', yzm, yzm_data)
					if sn == '1':
						self.yzm1 = yzm
						self.__debug_select__('码1解析成功')

					else:
						self.yzm2 = yzm
						self.__debug_select__('码2解析成功')

					return yzm
			except Exception as ex:
				# 可能是验证码解析软件,解析软件拥塞之后，等待多点时间
				self.__counter__('YZM', 'ERROR', ex, len(response.content), self.addr_yzm, yzm_data, 'HIGHT')
				self.__debug_select__('验证码解析过程发生异常', ex)
				return False

		else:
			return False



	def __clear_plate_filter__(self):
		self.img_codes = {}
		self.yzm1 = ''
		self.hidcxhp = ''
		self.xxxq = {}
		# 清空状态
		self.response = None

	def __get_hphm__(self):


		# 号牌号码队列
		queue_hphm = Queue(34)
		# 并行任务队列
		queue_task = Queue(self.hphm_group_num)

		# 根据网页内容查找号牌编码的图片链接
		def __get_num_code_urls__():
			src_list = []
			soup = BeautifulSoup(self.response.text, "html.parser")
			img_code_srcs = soup.find_all('image')

			if len(img_code_srcs) <= 0:
				self.__counter__('GET_HPHM','GET_CODES_URL', 'FAIL', 'NULL', 'ONE', 'HIGHT')
				return src_list

			# 数字和字母码图添加到进程任务中
			for img_code_src in img_code_srcs:
				src = img_code_src.get('src', '')
				# 不是号牌的图片不处理
				if src.startswith('GetNumImage.aspx?hphmValue='):
					src_list.append(src)

			if len(src_list) <= 0:
				self.__counter__('GET_HPHM','GET_CODES_URL', 'FAIL', 'NULL', 'TWO', 'HIGHT')

			return src_list

		# 直接获取hphm
		def __get_hphm_keep_alive__(url):
			try:
				temp_header = deepcopy(self.headers)
				temp_header['Referer'] = self.url_host + self.url_zbhphm
				# 统一处理，如果
				if not url.startswith('/'):
					url = '/' + url

				code = ''
				src_items = url.split('=')
				hphmValue = src_items[1] if len(src_items) == 2 else ''
				if hphmValue == '':
					return status.HPHM_NULL


				#不用本线程重试，交给其他线程重试
				hphm_download_try_max = 1
				hphm_download_try = 0
				# 循环重试4次
				while hphm_download_try < hphm_download_try_max:

					hphm_download_try += 1
					try:
						response_hphm = self.__http_get__(self.url_host + url, headers=temp_header, timeout=self.timeout_http_get,allow_redirects=False)
					except Exception as ex:
						self.__counter__('GET_HPHM','HPHM', 'GET', 'FAIL', 'TIMOUT', timeout, ex, 'HIGHT')
						continue

					if self.__is_offline__(response_hphm):
						self.__counter__('GET_HPHM','HPHM', 'GET', 'FAIL', 'RELOGIN', 'HIGHT')
						return status.HPHM_OTHER

					# 不需要POST,还在获取，用户已经刷新hphm页面时，直接退出即可
					elif response_hphm and 'text/html' in response_hphm.headers.get('content-type'):
						#self.__counter__('GET_HPHM','HPHM', 'GET', 'LATER',response_hphm,'HIGHT')
						return status.HPHM_TEXT

					"""
					gzip解码,request会自动解码
					"""
					try:
						# 二进制
						body = response_hphm.content
						code = get_code(body, self.fontTemplates)
						if code in '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ' and code != '':
							self.img_codes[code] = hphmValue
							"""self.__counter__('GET_HPHM','HPHM', 'GET', 'SUCCESS', hphm_download_try, response_hphm.status_code,
											 response_hphm.url,'HIGHT')"""
							return True
						else:
							self.__counter__('GET_HPHM','HPHM', 'GET', 'FAIL', hphm_download_try, response_hphm.status_code,
											 response_hphm.url,'HIGHT')
							continue
					except Exception as ex:
						self.__counter__('GET_HPHM','HPHM', 'GET', 'ERROR', hphm_download_try, ex,'HIGHT')
						continue
				# 重试之后仍然失败的压入队列，让其他线程获取
				else:
					self.__counter__('GET_HPHM','GET','FAIL','HIGHT')
					self.__debug_select__('获取HPHM失败，稍后重新尝试，本次GET次数',hphm_download_try_max)
					try:
						queue_hphm.put(url)
					except Exception as ex:
						pass
			except Exception as  ex:
				self.__counter__('GET_HPHM','HPHM', 'GET', 'ERROR', 'EXIT', ex,'HIGHT')
				pass

		# 各个线程从队列里面并发获取url
		def get_hphm_threading():

			#队列不退出
			while True:
				#如果已经处理完毕，提前退出
				if self.__hphm_is_finish__():
					break

				try:
					# 获取url
					url = queue_hphm.get(True,3)
				# 获取不到url，可能被其他线程抢了
				except Exception as ex:
					#self.__counter__('GET_HPHM','THREAD','ERROR',ex,'HIGHT')
					break

				try:
					__get_hphm_keep_alive__(url=url)
				except Exception as ex:
					#self.__counter__('GET_HPHM','THREAD', 'ERROR', ex,'HIGHT')
					pass
			else:
				#self.__counter__('GET_HPHM','THREAD', 'FINISH', 'HIGHT')
				pass

			# 非阻塞，表明任务处理完毕
			try:
				queue_task.put(1)
			except Exception as ex:
				pass

		# 如果需要获取hphm
		if self.img_codes is None or len(self.img_codes) == 0:

			self.__debug_select__('需要更新HPHM')

			threading_hphm = []
			# 获取地址
			url_list = __get_num_code_urls__()
			if len(url_list) != 34:
				self.__counter__('GET_HPHM_LIST', 'GET_CODE_URLS', 'FAIL', len(url_list), 'HIGHT')
				self.__clear_plate_filter__()
				return False

			else:

				if self.hphm_group_num == 1:
					for url in url_list:
						try:
							count = 0
							while count < 3:
								count += 1
								try:
									if __get_hphm_keep_alive__(url=url):
										break
									else:
										pass
										#print_debug('获取HPHM失败',url)
								except Exception as ex:
									pass
							else:
								print_debug('获取HPHM失败', url)

							if self.__hphm_is_finish__():
								return True

						except Exception as ex:
							print_debug('获取HPHM异常', ex)
							pass
					else:
						if self.__hphm_is_finish__():
							return True
						else:
							return False

				#url推送到队列里面
				for url in url_list:
					try:
						queue_hphm.put(url,True,0.01)
					except Exception as ex:
						pass



				#self.__counter__('GET_HPHM_LIST', 'GET_CODE_URLS', 'TRY',  'HIGHT')
				# 并行线程配置
				for index in range(0, self.hphm_group_num):
					threading_hphm.append(threading.Thread(target=get_hphm_threading))
				else:
					pass

				# 并行线程启动
				for theeading_get_hphm in threading_hphm:
					theeading_get_hphm.setDaemon(True)
					theeading_get_hphm.start()

				count = 0
				while True:
					try:
						try:
							# 任务间隔10s，超时退出
							queue_task.get(True)
						except Exception as ex:
							continue

						if self.__hphm_is_finish__():
							queue_task.close()
							return

						count += 1
						if count >= self.hphm_group_num:
							queue_task.close()
							return
						else:
							continue
					except Exception as ex:
						try:
							pass
							queue_task.close()
						except Exception as ex:
							pass

						return

		else:
			self.__counter__('GET_HPHM_LIST', 'INFO', 'IMG_CODES', 'HAVE', len(self.img_codes), 'HIGHT')

	# 34个hphm和验证码
	def __is_finish__(self):

		if self.__hphm_is_finish__() and self.yzm1 != '':
			return True
		else:
			return False

	#34个hphm下载完成判断
	def __hphm_is_finish__(self):

		test_len = len(self.test_like_list)
		img_codes_len = len(self.img_codes)

		# 需要所有线程结束
		if self.all_flag:
			if img_codes_len != 34:
				return False
			else:
				return True

		# 指定了心仪号牌
		elif test_len > 0 and len(set(self.test_like_list).difference(self.img_codes.keys())) <= 0 or \
								test_len <= 0 and len(
					set(self.userInfo['numb_list']).difference(self.img_codes.keys())) <= 0:
			return True
		else:
			return False


	# 获取网页返回值，一般获取验证码图片或者其他附件时使用
	# 如果hphm不为空，则只获取验证码
	def __get_zbhphm_yzm___(self):

		# 码1和数字字母码有效，直接退出
		if len(self.img_codes) > 0 and self.yzm1 != '':
			return True

		# 获取zhhphm页面
		try:
			# print_debug('过滤条件页面判断')
			# 当前处于zbhphm页面，不用重新获取页面，否则需要重新获取
			if self.response and self.url_zbhphm in self.response.url:
				pass
			else:

				self.response = self.__http_get__(self.url_host + self.url_zbhphm, headers=self.headers,allow_redirects=False)

				if self.response.status_code == 200 and self.url_zbhphm in self.response.url:
					pass
				else:
					self.__counter__('GET_ZBHPHM', 'GET', 'FAIL', self.response.status_code, \
									 self.url_zbhphm, self.response.url, 'HIGHT')
					self.__debug_select__('HPHM页面已经下载失败', self.response.status_code, self.url_zbhphm, self.response.url)

					# 判断在线状态，并返回
					if self.__is_offline__(self.response):
						pass

					self.__clear_plate_filter__()
					return False

		except Exception as ex:
			self.__debug_select__('HPHM页面已经下载异常', ex)
			self.__counter__('GET_ZBHPHM', 'GET', 'ERROR', ex, 'HIGHT')
			self.__clear_plate_filter__()
			return False

		self.headers['Referer'] = self.response.url

		try:

			# 验证码1获取线程
			threading_get_yzm1 = threading.Thread(target=self.__get_yzm_from_url__,args=('1',))
			threading_get_yzm1.setDaemon(True)

			threading_get_hphm = threading.Thread(target=self.__get_hphm__)
			threading_get_hphm.setDaemon(True)

			threading_get_hphm.start()
			threading_get_yzm1.start()


			# 20s超时
			threading_get_yzm1.join()
			threading_get_hphm.join(self.timeout_hphm)

			if self.__is_offline__():
				return False

			elif self.__is_finish__():
				return True

			else:
				self.__debug_select__('更新码1和HPHM失败', self.yzm1, len(self.img_codes))
				self.__counter__('GET_HPHM_LIST', 'GET', 'FAIL', 'NOT_ENOUGH', len(self.img_codes), 'HIGHT')
				return False

		except Exception as ex:
			self.__debug_select__('更新码1和HPHM异常', self.yzm1, len(self.img_codes), ex)
			self.__counter__('GET_HPHM_LIST', 'GET', 'ERROR', ex, len(self.img_codes), self.yzm1, 'HIGHT')
			self.__clear_plate_filter__()
			return False

	# 生成hidcxhp,查号条件
	def __get_hidcxhp__(self):
		inter_str = '%2c'
		hidcxhp = ''

		# 如果是测试优选号，填上必填参数之后，返回
		if len(self.test_like_list) > 0:
			for temp in self.test_like_list:
				value = self.img_codes.get(temp, '')
				# 获取码失败，需要重新获取hphm页面
				if value == '':
					self.__counter__('HIDXCHP', 'ERROR', 'GETNULL', temp, len(self.img_codes),'HIGHT')
					return False

				hidcxhp += self.img_codes.get(temp, '') + inter_str
			else:
				# 去除最后一个逗号,没有厌恶号和其他约束，添加两个$
				hidcxhp = hidcxhp[:-3] + '$$'

			self.hidcxhp = hidcxhp
			return True

		# 构造喜欢的号码
		for temp in self.userInfo['like_list']:

			value = self.img_codes.get(temp, '')
			if value == '':
				self.__counter__('HIDXCHP', 'ERROR', 'GETNULL', temp, len(self.img_codes),'HIGHT')
				return False

			hidcxhp += value + inter_str
		else:
			# 去除最后一个逗号
			hidcxhp = hidcxhp[:-3] + '$'

		# 不喜欢的号
		for temp in self.userInfo['hate_list']:
			hidcxhp += self.img_codes.get(temp, '') + inter_str
		else:
			# 排除的号可以为空
			if len(self.userInfo['hate_list']) == 0:
				hidcxhp += '$'
			else:
				# 去除最后一个逗号
				hidcxhp = hidcxhp[:-3] + '$'

		# 选择限行的星期
		##"cklxx$0": "on",#限号标识，是否设定了限号的值
		xxxq_keys = {
			'1': "cklxx$0",
			'2': "cklxx$1",
			'3': "cklxx$2",
			'4': "cklxx$3",
			'5': "cklxx$4",
		}

		xxxq_nums = {
			'1': '6',
			'2': '7',
			'3': '8',
			'4': '9',
			'5': '0'
		}

		# XXXQ也可以为空
		#
		# 初始化
		self.xxxq = {}
		for temp in self.userInfo['xxxq_list']:
			hidcxhp += temp + inter_str

			# 镜像号添加
			if temp in xxxq_nums:
				hidcxhp += xxxq_nums[temp] + inter_str

			# 限行星期的复选框
			if temp in xxxq_keys.keys():
				xxxq_name = xxxq_keys[temp]
				self.xxxq[xxxq_name] = 'on'


		else:
			if len(self.userInfo['xxxq_list']) != 0:
				# 去除最后一个逗号
				hidcxhp = hidcxhp[:-3]

		self.hidcxhp = hidcxhp
		return True

	# 提交车牌过滤信息，然后返回可用车牌
	def __post_query_filter__(self):
		# hidcxhp格式如下
		# 5171c6172f05477eaee995e4cfb6b97d,f136d04f5df6415189f1a17b61f86cdc$805d40a26d2b4a22b6ae8018e4b4eb1f,1b7360c4e42d4e048f687fe651f4bc28$1,6
		if self.response is None:
			self.__counter__('POST_QUERY_FILTER','FAIL','NULL_TEXT','HIGHT')
			self.__clear_plate_filter__()
			return False

		postJson = get_value_from_body(self.response.text, {
			"ScriptManager1": "UpdatePanel1|lkbcxhp",
			"__EVENTTARGET": "lkbcxhp",
			"__EVENTARGUMENT": serachFlag,
			"__LASTFOCUS": serachFlag,
			"__VIEWSTATE": serachFlag,
			"__EVENTVALIDATION": serachFlag,
			# "cklxx$0": "on",#限号标识，是否设定了限号的值
			"txt_yzm": self.yzm1,  # 验证码
			# "hidcxhp":hidcxhp,#优选号码，排除号码，限号星期几三个组装x1,x2$y1,y2$1,2,3
		})


		for key in self.xxxq:
			postJson[key] = self.xxxq[key]

		# query用户获取查询号码的token
		if self.configInfo.get('query_control_type') == 'remote':
			self.__get_token__( self.configInfo.get('server_host','127.0.0.1'), 61260)
		else:
			self.__get_token__('127.0.0.1', 62260)

		#print_debug('启动查询')

		#查询之前提交条件
		"""if not self.__get_hidcxhp__():
			self.__counter__('ZBXZHM', 'POST', 'FAIL', 'HIDCXHP_NOT_READY')
			self.__debug_select__('查询条件生成失败，可能是查询条件有变更或者其他异常')
			return False"""

		postJson['hidcxhp'] = self.hidcxhp
		try:
			# 有可能没有重定向，此时返回
			headers = deepcopy(self.headers)
			headers["Content-Type"] = "application/x-www-form-urlencoded"
			# 查询真正开始时间
			time_query_post_hphm_start = time.time()
			#不自动跳转,避免跳转到index页面
			response = self.__http_post__(self.url_host + self.url_zbhphm, data=postJson, headers=headers,allow_redirects=False)

			time_query_post_hphm_end = time.time()
			try:
				if response:
					if response.status_code == 302 and  'xzhp.aspx' in response.headers['location']:

						response = self.__http_get__(self.url_host + response.headers['location'],headers=headers,allow_redirects=False)
						if response and response.status_code == 200 and 'xzhp.aspx' in response.url:
							# 更新Referer
							self.headers['Referer'] = response.url
							self.time_query_post_hphm_start = time_query_post_hphm_start
							self.time_query_post_hphm_end = time_query_post_hphm_end
							self.time_query_get_plate_end = time.time()

							self.time_query_get_plate = self.time_query_get_plate_end - self.time_query_post_hphm_start

							return response
						else:
							self.__counter__('PLATE_PAGE','GET_XZHP','FAIL',response,'HIGHT')
					elif response.status_code == 200:
						return response
					else:
						return  False
				else:
					self.__counter__('PLATE_PAGE','POST_ZBHPHM','FAIL',response,'HIGHT')

				return False

			except Exception as ex:
				self.__counter__('PLATE_PAGE','ERROR',ex,'HIGHT')
				return  False



		except Exception as ex:
			self.__counter__('ZBXZHM', 'POST', 'ERROR', ex, 'HIGHT')
			return False

	# 先GET  '/zbhphm.aspx'，再Post到该页面，重定向到号牌页面
	# HTTP_GET可能两种错误 1、index重登 2、ERROR_Page重新登录
	def __get_plate_page__(self):
		# 【9】post zbhphm.aspx页面，重定向到xzhp.aspx页面，xzhp这个页面有筛选出来的汽车号牌数据
		# 个性化号码相关信息到服务器，获取重定向链接
		count = 0
		self.yzm1_try = 0
		while count < 3:
			count += 1

			#先获取token
			#self.__get_token__('127.0.0.1',62261)
			# 获取过滤条件的页面，如果页面存在，则直接获取
			self.time_get_hphm_start = time.time()
			if not self.__get_zbhphm_yzm___():

				#下线重新登录一下
				self.__clear_plate_filter__()
				self.__counter__('GET_PLATE_PAGE', 'FAIL', 'GET_ZBHPHM', 'HIGHT')
				return False

			self.time_get_hphm_end = time.time()
			self.time_query_get_hphm = self.time_get_hphm_end - self.time_get_hphm_start

			# 生成过滤条件，如果生成失败，清除当前条件
			if not self.__get_hidcxhp__():
				self.__clear_plate_filter__()
				return False

			response = self.__post_query_filter__()
			if response:
				if  'xzhp.aspx' in response.url:
					self.__clear_plate_filter__()
					return response
				else:
					# 先判断验证码是不是错误了
					if '<label id="lblmsg" style="color: Red;">验证码输入错误,请重新输入</label>' in response.text or \
									'验证码不能为空' in self.response.text:
						self.__counter__('POST_ZBHPHM', 'ERROR', 'YZM1', self.yzm1, 'HIGHT')
						self.yzm1 = ''
						self.yzm1_try += 1
						continue
					# 可能是正确的查询结果，需要判断
					else:
						self.__counter__('POST_ZBHPHM', 'FAIL', 'UNKNOWN', 'HIGHT')
						# debug_save(self.response.content,'POST_ZBHPHM_FAIL','wb')
						self.__clear_plate_filter__()
						return False
			else:
				self.__clear_plate_filter__()
				self.__counter__('POST_ZBHPHM', 'FAIL', 'POST_QUERY_FILTER_FAIL', 'HIGHT')
				return False
		# 未跳出循环，则获取车牌页面出错
		else:
			self.__counter__('POST_ZBHPHM', 'FAIL', 'MAX_YZM1_TRY', self.response.status_code, 'HIGHT')
			self.__clear_plate_filter__()
			return False


	reserve = """
	# 提交车牌过滤信息，然后返回可用车牌
	def __get_xzhp_threading__(self,get_xzhp_max=3):
		# hidcxhp格式如下
		# 5171c6172f05477eaee995e4cfb6b97d,f136d04f5df6415189f1a17b61f86cdc$805d40a26d2b4a22b6ae8018e4b4eb1f,1b7360c4e42d4e048f687fe651f4bc28$1,6
		if self.response is None:
			self.__counter__('POST_QUERY_FILTER', 'FAIL', 'NULL_TEXT', 'HIGHT')
			self.__clear_plate_filter__()
			return False

		postJson = get_value_from_body(self.response.text, {
			"ScriptManager1": "UpdatePanel1|lkbcxhp",
			"__EVENTTARGET": "lkbcxhp",
			"__EVENTARGUMENT": serachFlag,
			"__LASTFOCUS": serachFlag,
			"__VIEWSTATE": serachFlag,
			"__EVENTVALIDATION": serachFlag,
			# "cklxx$0": "on",#限号标识，是否设定了限号的值
			"txt_yzm": self.yzm1,  # 验证码
			# "hidcxhp":hidcxhp,#优选号码，排除号码，限号星期几三个组装x1,x2$y1,y2$1,2,3
		})

		for key in self.xxxq:
			postJson[key] = self.xxxq[key]

		postJson['hidcxhp'] = self.hidcxhp
		try:
			# 有可能没有重定向，此时返回
			headers = deepcopy(self.headers)
			headers["Content-Type"] = "application/x-www-form-urlencoded"
			# 查询真正开始时间
			time_query_start = time.time()
			# 不自动跳转,避免跳转到index页面
			response_post_hphm = self.__http_post__(self.url_host + self.url_zbhphm, data=postJson, headers=headers,
										  allow_redirects=False)
		except Exception as ex:
			self.__counter__('ZBXZHM', 'POST', 'ERROR', ex, 'HIGHT')
			return False


		try:
			if response_post_hphm:
				if response_post_hphm.status_code == 302 and 'xzhp.aspx' in response_post_hphm.headers['location']:

					if self.debug:
						# 并发测试用
						time.sleep(random.random() * 0.5)

					queue_post_zbxzhm = Queue(get_xzhp_max)

					headers_get_xzhp = deepcopy(self.headers)
					#headers_get_xzhp['Referer'] = response_post_hphm.headers['location']

					if get_xzhp_max == 1:
						response_get_xzhp = self.__http_get__(self.url_host + response_post_hphm.headers['location'],headers_get_xzhp ,None,False)
						if response_get_xzhp and response_get_xzhp.status_code == 200 and 'xzhp.aspx' in response_get_xzhp.url:
							# 更新Referer
							self.headers['Referer'] = response_get_xzhp.url
							return response_get_xzhp
						else:
							self.__counter__('PLATE_PAGE', 'GET_XZHP', 'FAIL', response_get_xzhp, 'HIGHT')
							return False

					index = 0
					while index < get_xzhp_max:
						index += 1
						threading_get_xzhp = threading.Thread(target=self.__http_get_threading__,args=(queue_post_zbxzhm, \
							self.url_host + response_post_hphm.headers['location'],headers_get_xzhp ,None,False,))
						threading_get_xzhp.setDaemon(True)
						threading_get_xzhp.start()

					count = 0
					time_start = time.time()
					while count < get_xzhp_max and time.time() - time_start < 30:
						count += 1
						try:
							response_get_xzhp = queue_post_zbxzhm.get(True,20)
							if response_get_xzhp and response_get_xzhp.get('status_code') == 200 and \
											'xzhp.aspx' in response_get_xzhp.get('url'):
								# 更新Referer
								self.headers['Referer'] = response_get_xzhp.get('url')
								#外面关闭队列
								try:
									queue_post_zbxzhm.close()
								except Exception as ex:
									pass
								return response_get_xzhp
							else:
								self.__counter__('PLATE_PAGE', 'GET_XZHP', 'FAIL', response_get_xzhp,'HIGHT')
						except Exception as ex:
							self.__counter__('PLATE_PAGE', 'GET_XZHP', 'ERROR', ex, 'HIGHT')
							continue
					else:
						try:
							queue_post_zbxzhm.close()
						except Exception as ex:
							pass
						self.__counter__('PLATE_PAGE', 'GET_XZHP', 'FAIL_LAST',  'HIGHT')
						return False
				elif response_post_hphm.status_code == 200:
					self.__counter__('PLATE_PAGE', 'POST', '200_NOT_302', 'HIGHT')
					return response_post_hphm
				else:
					self.__counter__('PLATE_PAGE', 'POST', 'FAIL', 'HIGHT')
					return False
			else:
				self.__counter__('PLATE_PAGE', 'POST', 'FAIL', response_post_hphm,'HIGHT')

			return False

		except Exception as ex:
			self.__counter__('PLATE_PAGE','POST', 'ERROR', ex,'HIGHT')
			return False

	def __get_plate_pages__(self,queue_out=None,get_xzhp_max=1):
		try:


			response = self.__get_xzhp_threading__(get_xzhp_max)
			if response:
				if 'xzhp.aspx' in response.url:
					self.__clear_plate_filter__()

					if queue_out is None:
						return response
					try:
						queue_out.put(response, True, 1)
					except Exception as ex:
						pass

					return True
				elif '<label id="lblmsg" style="color: Red;">验证码输入错误,请重新输入</label>' in response.text or \
								'验证码不能为空' in self.response.text:
					self.__counter__('POST_ZBHPHM', 'FAIL', 'YZM1', self.yzm1, 'HIGHT')
				try:
					queue_out.put(False, True, 1)
				except Exception as ex:
					pass
				return False
			else:
				try:
					queue_out.put(False, True, 1)
				except Exception as ex:
					pass
				return False
		except Exception as ex:
			self.__counter__('POST_ZBHPHM', 'ERROR',ex,'HIGHT')
			try:
				queue_out.put(False, True, 1)
			except Exception as ex:
				pass

			return False

	# 获取号牌页面的函数
	def __get_plate_from_pages__(self,post_filter_max=3,get_xzhp_max=3):

		# 【2】查询号牌
		try:
			# 获取过滤条件的页面，如果页面存在，则直接获取
			if not self.__get_zbhphm_yzm___():
				self.__clear_plate_filter__()
				self.__debug_select__('约号失败', '获取查询条件页面失败')
				return False
		except Exception as ex:
			self.__debug_select__('约号失败', '获取查询条件页面异常', ex)
			self.__counter__('PLATE_PAGES', 'GET_ERROR', ex, 'HIGHT')
			return False

		try:
			# 生成过滤条件，如果生成失败，清除当前条件
			if not self.__get_hidcxhp__():
				self.__clear_plate_filter__()
				self.__debug_select__('约号失败', '生成过滤条件失败')
				return False
		except Exception as ex:
			self.__debug_select__('约号失败','生成过滤条件异常',ex)
			self.__counter__('PLATE_PAGES', 'FAIL_GET_POST_TOKEN', ex, 'HIGHT')
			return False

		#query用户获取查询的权限
		try:
			# query用户获取查询号码的token
			if self.userInfo['task_type'] == 'query':
				while True:
					try:
						# 本地直接发送给Select用户进行约号
						tcp = socket(AF_INET, SOCK_STREAM)

						# dumps data转换成网络数据发送格式
						addr_query_token = ('127.0.0.1', 62260)
						tcp.connect(addr_query_token)
						tcp.send(str(self.userInfo.get('query_index', 'query_user')).encode())
						if tcp.recv(512).decode('utf-8') == 'ACK':
							break
					except Exception as ex:
						pass
					finally:
						time.sleep(0.5)
		except Exception as ex:
			self.__counter__('PLATE_PAGES', 'FAIL_GET_POST_TOKEN', ex,'HIGHT')
			return False


		try:
			self.time_query_post_hphm_start = time.time()
			# 并发查询号牌
			queue_out = Queue(post_filter_max)
			for i in range(0, post_filter_max):
				threading_temp = threading.Thread(target=self.__get_plate_pages__, args=(queue_out,get_xzhp_max,))
				threading_temp.setDaemon(True)
				threading_temp.start()

			count = 0
			time_start = time.time()
			while count < post_filter_max and time.time() - time_start < 40:
				count += 1
				try:
					response = queue_out.get(True, 20)
				except Exception as ex:
					continue

				if response:
					self.time_query_get_plate_end = time.time()
					try:
						#print_debug('查询车牌号成功', response.url)
						queue_out.close()
					except Exception as ex:
						pass

					return  response
				else:
					# self.__debug_select__('约号失败，查询号码失败',xzhm,self.time_get_plate_page - self.time_order_start)
					self.__counter__('PLATE_PAGES', 'FAIL', response,'HIGHT')
					continue
			else:
				self.__clear_plate_filter__()
				self.time_get_plate_page = time.time()
				self.__debug_select__('约号失败，多线程查询号码失败')
				queue_out.close()
				return False

			self.__clear_plate_filter__()
			return True

		except Exception as ex:
			self.__debug_select__('约号失败，查询号码发生异常', ex)
			self.__counter__('PLATE_PAGES', 'ERROR_POST_QUERY_FILTER', ex)
			self.__clear_plate_filter__()
			return False    """


	def __report_plate__(self,plate_count,count_hit_plate):
		try:
			json_data = {
				'taask_type': 'plate',
				'hndle_type': 'result',
				'user_info': {
					'count_all': plate_count,
					'count_hit': count_hit_plate,
				}
			}
			send_with_ack((self.configInfo.get('server_host','127.0.0.1'), 61261),json_data)
		except Exception as ex:
			print_warnning('上报结果异常')

	############################################################################
	# 【10】get xzhp.aspx页面，这个页面生成有号牌，可以直接预约号
	# url是上一个http://www.scjj.gov.cn:121/xzhp.aspx...页面
	# Query任务有两种状态，当select激活时，发送选中的号给select用户
	# 另外，将记录存档
	# 返回值status  201表示少于50个大于0，202表示查询结果为0
	############################################################################
	def __get_plate__(self, response, filter_flag=True):

		len_select_users = len(self.userInfo['select_user_dict'])




		get_hphm_time = '%7.3f' %  self.time_query_get_hphm
		query_post_time = '%7.3f' % (self.time_query_post_hphm_end - self.time_query_post_hphm_start)
		query_get_time = '%7.3f' % (self.time_query_get_plate_end - self.time_query_post_hphm_end)
		result_format = '%2s'
		query_index = result_format % self.query_index


		# query_time = round(query_time,3)
		# 页面错误
		# '未查询到相关号牌' in self.body or
		if '当前页面显示0个' in response.text:

			self.__report_plate__(0, 0)


			# 用户在其他地方登陆或者超时，需要重新登录
			if '类似的号牌有' in response.text and '未查询到相关号牌' not in response.text:
				self.status_plate = status.PLATE_TIMOUT
				self.__record_plate__('进程', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
							   query_get_time, query_post_time,get_hphm_time, '码1',self.yzm1_try,'订阅',len_select_users,'超时错误')


				return None
			else:
				self.status_plate = status.PLATE_NULL

				self.__record_plate__('进程', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
							query_get_time, query_post_time,get_hphm_time,'码1',self.yzm1_try, '订阅',len_select_users)

				return None

		elif '类似的号牌有' not in response.text or '操作倒计时' not in response.text:

			self.__report_plate__(0, 0)

			self.status_plate = status.PLATE_PAGE_ERROR
			self.__record_plate__('进程', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
						   query_get_time, query_post_time, get_hphm_time,'码1',self.yzm1_try,'订阅',len_select_users, '未知页面错误')

			return None
		else:
			# 初始化
			self.status_plate = status.INIT

		# 结果需要按照关键字过滤
		soup = BeautifulSoup(response.text, "html.parser")
		a_list = soup.find_all('a')

		temp_json = {
			'task_type': 'order',
			'handle_type': 'request',
			'user_info': {
				'select_ip': self.userInfo.get('select_ip', ''),
				'select_port': self.userInfo.get('select_port', ''),
				'xzhm': '',
				# 'url':'',
				'send_ip': self.userInfo['send_ip'],
				'id': self.userInfo.get('select_user', ''),
				# 'Referer':url,
			},
		}

		# 发送给服务器记录的车牌号
		plate_list_send_to_server = ''

		count_hit_plate = 0

		if len(a_list) == 0:

			# 如果查询到空号，则换IP重新登录，空号可能是确实查询不出数据，也可能是IP用户受限，先不换用户，换IP
			# 不换IP不换用户，重新登录意义也不大,调用函数刷新IP
			self.status_plate = status.PLATE_NULL
			self.__record_plate__( '进程', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
						   query_get_time, query_post_time,get_hphm_time,'码1',self.yzm1_try, '订阅',len_select_users, '找不到链接')

			return None


		else:
			for a_car in a_list:
				href = a_car.get('href', '')
				if not href.startswith('Xzhphm_Handler.ashx?'):
					continue

				car_pai = a_car.string[-5:]

				temp_json['handle_type'] = 'request'
				temp_json['user_info']['xzhm'] = car_pai
				# 发现号码的时间戳
				temp_json['user_info']['time'] = time.time()

				# 车牌号记录
				plate_list_send_to_server += car_pai

				# 不过滤，给一些特别场景使用，select用户获取验证码2场景，不用过滤号牌，任意搜索
				if not filter_flag:
					# select用户查到号码之后预约，需要url
					temp_json['user_info']['url'] = href
					#self.__counter__('PLATE', 'GET', car_pai)

					self.status_plate = status.PLATE_LITTLE
					self.__record_plate__('特别', query_index, '查询', car_pai, '过滤', result_format % 1, '时长',
								  query_get_time,query_post_time, get_hphm_time,'码1',self.yzm1_try, '订阅',len_select_users)
					return temp_json

				if not self.__plate_is_ok__(car_pai):
					continue

				# 选号用户，或者选号测试用户
				if self.userInfo['task_type'] == 'select' or self.userInfo['task_type'] == 'select_test':
					# 该select用户的车牌号匹配成功
					# select用户查到号码之后预约，需要url
					temp_json['user_info']['url'] = self.url_host + '/' + href
					#self.__counter__('PLATE', 'GET', car_pai)

					self.status_plate = status.PLATE_LITTLE
					return temp_json


				# 针对select用户列表过滤,#query用户把车牌号直接发给select用户
				for select_user_key, select_user_info in self.userInfo['select_user_dict'].items():

					# 该select用户的车牌号匹配成功
					if self.__plate_is_ok__(car_pai, select_user_info.get('gltj', ''),
											select_user_info.get('pctj', '')):

						count_hit_plate += 1

						temp_json['handle_type'] = 'request'

						select_user_addr = select_user_info.get('select_addr')

						if select_user_addr is None:
							self.__counter__('PLATE', 'SEND2SELECT', 'FAIL', 'ADDR_NULL', select_user_key, 'HIGHT')
							continue

						count = 0
						# 重传3次
						while count < 3:
							try:
								# 本地直接发送给Select用户进行约号
								udp = socket(AF_INET, SOCK_DGRAM)

								# 超时定时器1.5s
								udp.settimeout(5)
								# dumps data转换成网络数据发送格式
								udp.sendto(dumps(temp_json).encode(), select_user_addr)

								if udp.recv(512).decode('utf-8') == 'ACK':
									self.__counter__('PLATE', 'SEND2SELECT', 'SUCCESS', car_pai, select_user_addr,
													 'HIGHT')
									break
							except Exception as ex:
								self.__counter__('PLATE', 'SEND2SELECT', 'FAIL', car_pai, select_user_addr, ex, 'HIGHT')
								if '10054' in str(ex):
									time.sleep(1.0)
							finally:
								count += 1

							# self.__record_plate__('QUERY','ORDER',car_pai)
			else:
				self.status_plate = status.PLATE_NORMAL

		if plate_list_send_to_server != '':

			temp_json['user_info']['xzhm'] = plate_list_send_to_server
			len_result = len(plate_list_send_to_server)
			plate_count = int(len_result / 5)
			plates = ''

			if count_hit_plate > 0:
				beep(3,500,250)

			for index in range(0, plate_count):
				plate_start = (index) * 5
				plate_end = (index + 1) * 5
				plates += plate_list_send_to_server[plate_start:plate_end] + '|'

			self.__record_plate__('进程', self.query_index, '查询', result_format % int(len(plate_list_send_to_server) / 5),
						'过滤', result_format % count_hit_plate, '时长', query_get_time,query_post_time, get_hphm_time,'码1',self.yzm1_try,'订阅',len_select_users,plates)
			# 推送到队列里面，发送给服务器存档，号码一次性推送给服务器
			# 直接发送给服务器，不要经过队列

			# 小于50个号牌，不需要重复查询，同一个用户查出来结果一样
			if len(plate_list_send_to_server) < 50 * 5:
				self.status_plate = status.PLATE_LITTLE


			self.__report_plate__(plate_count,count_hit_plate)

		# 没有查询到车牌号
		else:
			self.status_plate = status.PLATE_NULL
			if filter_flag:
				self.__record_plate__('特别', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
									  query_get_time,query_post_time,get_hphm_time,'码1',self.yzm1_try, '订阅',len_select_users)
			else:
				self.__record_plate__('进程', query_index, '查询', result_format % 0, '过滤', result_format % 0, '时长',
							query_get_time, query_post_time,get_hphm_time,'码1',self.yzm1_try, '订阅',len_select_users)

			self.__report_plate__(0, 0)

		return temp_json

	# 重新拨号更换IP，必须更换IP成功，否则不退出
	# omit_time为True时，强制更换IP，忽略时间间隔
	def __rasdial__(self, omit_time=None):

		udp = socket(AF_INET, SOCK_DGRAM)

		udp.setsockopt(SOL_SOCKET, SO_SNDBUF, 10 * 8 * 1024)
		# 端口复用
		# udp.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		# 超时定时器1.5s
		# 5s中等待
		udp.settimeout(5)

		json_temp = {
			'task_type': 'network',
			'handle_type': 'null',
			'user_info': {
				'sender': self.userInfo['clsbdh'],
			},
		}

		if omit_time is None:
			pass
		elif omit_time:
			json_temp['handle_type'] = 'reset'
		else:
			json_temp['handle_type'] = 'have_num'

		result, next_handle = False, ''

		try:
			udp.sendto(dumps(json_temp).encode(), self.addr_rasdial)
			data, addr_dst = udp.recvfrom(10 * 8 * 1024)

			json_data = loads(data.decode('utf-8'))

			next_handle = json_data.get('handle_type', '')

			result = True

		except Exception as ex:
			result = False
		finally:
			# 触发了强制更换IP，等待3s,等网络断掉
			if omit_time:
				time.sleep(3)
			return result, next_handle





	# 单个用户队列处理中枢，用户级入口消息监听，分发各个子模块
	def __listen__(self):

		while True:
			try:
				msg = self.queue_in.get(True)

				task_type = msg.get('task_type', '')
				handle_type = msg.get('handle_type', '')
				# 验证码更换任务
				if msg['task_type'] == 'yzm':
					# 验证码错误，需要更换，发送给select用户的消息
					if msg['handle_type'] == 'change':
						self.queue_user['queue_in_control'].put(msg, True, 2)
						self.__counter__('LISTEN', 'YZM', 'CHANGE', msg['user_info']['sn'])
					else:
						self.__counter__('LISTEN', 'YZM', 'UNKNOW', msg['task_type'], msg['handle_type'])

				#主要是Query用户
				elif task_type == 'broadcast':

					#暂停网络操作
					if handle_type == 'pause':
						self.pause = True
					#继续网络操作
					elif handle_type == 'resume':
						self.pause = False
					else:
						pass

				# 更新信息
				elif msg['task_type'] == 'login':
					self.__counter__('LISTEN', 'SELECT_LOGIN', msg['handle_type'])
					self.__update__(msg['user_info'])

				# 开始停止或者更新相关任务
				elif task_type == 'query' or task_type == 'select':
					if handle_type == 'stop':
						self.run_enable = False
					# 主要针对select用户，重新登录
					elif handle_type == 'relogin' or handle_type == 'order':
						self.queue_user['queue_in_control'].put(msg, True, 2)
						self.__counter__('LISTEN', 'TASK', 'RELOGIN')
					else:
						#print_warnning('用户监听接收到未知的任务', msg['task_type'], msg['handle_type'])
						self.__counter__('LISTEN', 'UNKNOWN_TYPE', msg['task_type'], msg['handle_type'])

				else:
					#print_warnning('用户监听接收到未知的任务', msg['task_type'], msg['handle_type'])
					self.__counter__('LISTEN', 'UNKNOWN_TYPE', msg['task_type'], msg['handle_type'])
			except Exception as ex:
				self.__counter__('LISTEN', 'ERROR', ex)
				#print_warnning('用户监听任务处理异常', ex)
			finally:
				pass

#查询实体继承
class Query(Plate):
	def __init__(self,userInfo,queue_in):
		Plate.__init__(self,userInfo=userInfo,queue_in=queue_in)

	# 最简单的车牌号测试IP和车架号能否正常查询
	# 保证一定有返回结果
	def __get_plate_test__(self):

		result = None
		# 测试模式
		self.test_like_list = ['1', '2']
		while True:
			try:
				# 获取号牌页面

				response = self.__get_plate_page__()
				if response:
					pass
				else:
					if self.__retry_with_login__():
						pass
					continue

				# 分析车牌号返回页面
				self.__get_plate__(response, filter_flag=False)

				# 首先判断是否需要重新登录
				if self.status_plate == status.PLATE_TIMOUT:
					#self.__counter__('PLATE_TEST', 'PLATE_PAGE', 'TIMEOUT', 'SERVER')
					# 登陆超时，直接重新登录
					self.__relogin__()
					continue

				# 不是合适的车牌号页面
				elif self.status_plate == status.PLATE_PAGE_ERROR:
					#self.__counter__('PLATE_TEST', 'PLATE_PAGE', 'ERROR', 'RELOGIN', self.status_plate)
					self.__change_user_info__()
					self.__is_offline__()
					continue

				elif self.status_plate == status.PLATE_NULL:
					#self.__counter__('PLATE_TEST', 'PLATE_PAGE', 'NULL', 'RESET_NET', self.status_plate)
					result = False
					break
				# 不等于200也不等于201
				elif self.status_plate == status.PLATE_LITTLE or self.status_plate == status.PLATE_NORMAL:
					#self.__counter__('PLATE_TEST', 'PLATE_PAGE', 'SUCCESS', 'OK_NET', self.status_plate)
					result = True
					break
				else:
					continue

			except Exception as ex:
				continue

		self.test_like_list = []
		self.__counter__('PLATE_TEST', result, self.status_plate, 'HIGHT')
		return result

	def start(self):

		# 用户级监听子线程
		self.threading_listen = threading.Thread(target=self.__listen__)
		self.threading_listen.setDaemon(True)
		self.threading_listen.start()

		print_success('查询进程启动', self.query_index)
		self.__query__()

	# 创建多线程查询，按照查询条件
	def __query__(self):

		#self.all_flag = True

		# 登录
		self.__relogin__()

		count_query = 0
		while self.run_enable:
			try:

				# 60次切换车架号，重新登录，统计50次就切换
				if count_query >= int(self.configInfo.get('query_user_counts','50')):
					self.__change_user_info__()
					count_query = 0
					self.__relogin__()


				try:

					# 查号页面获取失败，或者需要不在线，需要重新登录
					response = self.__get_plate_page__()
					#time.sleep(10)
				except Exception as ex:
					self.__counter__('QUERY', 'GET_PAGE', 'ERROR', ex, 'HIGHT')
					continue

				try:
					# 查询成功
					if response:
						pass
					# 查询失败需要重新接入
					elif self.__retry_with_login__():
						self.__counter__('QUERY', 'GET_PAGE', 'FAIL', 'GET_PLATE_PAGE_OR_RELOGIN',
										 self.userInfo['numb_list'], 'HIGHT')
						continue

					# 查询失败不需要重新接入
					else:
						self.__counter__('QUERY', 'GET_PAGE', 'FAIL', 'FAIL_UNKNOWN', self.userInfo['numb_list'],
										 response, 'HIGHT')
						time.sleep(2)
						continue
				except Exception as ex:
					self.__counter__('QUERY', 'GET_PAGE', 'PLATE_PAGE', 'ERROR', ex, 'HIGHT')
					continue

				# 查询次数计数
				count_query += 1
				self.__get_plate__(response)
				# 页面报错
				if self.status_plate == status.PLATE_PAGE_ERROR:
					self.__counter__('QUERY', 'ERROR_GET_PLATE', self.status_plate, self.userInfo['numb_list'], 'HIGHT')
					# 页面获取错误，可能是丢包，暂时休眠1s降低请求频率，休眠
					continue

				# 查询结果为空，一般来说是IP受限，查询一个简单的号识别一下场景
				elif self.status_plate == status.PLATE_NULL:
					# 长长打印，级别调低
					self.__counter__('QUERY', 'NULL_GET_PLATE', self.userInfo['numb_list'], 'HIGHT')
					result, infor = self.__rasdial__()

					# 需要查询简单的号
					if result and infor == 'query':
						if not self.__get_plate_test__():
							#print_error('测试IP已经不可用')
							self.__counter__('QUERY', 'NULL_GET_PLATE_TEST', 'HIGHT')
							# 强制刷新IP，等待进程重启
							self.__rasdial__(True)
							self.__relogin__()
						else:
							self.__rasdial__(False)
							self.__counter__('QUERY', 'OK_GET_PLATE_TEST', 'HIGHT')
							self.__clear_plate_filter__()

					continue

				# 不需要重复查询，更换用户重新登录,201代表搜索出来的车牌号个数小于50
				elif self.status_plate == status.PLATE_LITTLE:
					count_query_null = 0
					time_end = time.time()

					self.__rasdial__(False)
					self.__counter__('QUERY', 'SUCCESS', 'LITTLE_RESULT', self.userInfo['numb_list'],
									 time.time() - self.time_query_post_hphm_start, 'HIGHT')

					continue
				elif self.status_plate == status.PLATE_NORMAL:
					self.__rasdial__(False)
				# 其他异常状态码
				else:
					self.__counter__('QUERY', 'ERROR', self.status_plate, self.userInfo['numb_list'], self.status_plate,
									 time.time() - self.time_query_post_hphm_start,'HIGHT')


			except Exception as ex:
				self.__counter__('QUERY', 'ERROR', ex, 'HIGHT')
			finally:
				pass
		else:
			self.__counter__('QUERY', 'STOP', self.run_enable, 'HIGHT')


class Order(Plate):
	def __init__(self,userInfo,queue_in):
		Plate.__init__(self,userInfo=userInfo,queue_in=queue_in)

		# 符合条件的号码列表，历史记录
		self.plate_list = []

		#约号用户参数初始化
		self.__init_order_para__()

		self.__init_status__()

	def __init_order_para__(self):

		# 总体约号流程重试次数
		self.order_retry = 1
		self.order_post_filter_max = 1
		self.order_get_xzhp_max = 1
		# select用户多线程参数
		# 根据出号的号牌页面，并发获取重定向到finish的响应页面
		self.order_xzhphm_max = 2
		# 30秒就可以了
		self.order_xzhphm_timeout = 30 * 1

		# finish页面相关的所有参数配置
		# GET finish页面获取相关的参数配置
		# GET finish的并发配置
		self.select_order_get_finish_max = 2
		# 整个GET过程，等待所有线程响应结果的定时器
		self.get_finish_wait_time = 30 * 2

		# POST finish页面相关的所有
		# post finish页面的线程数
		self.select_order_post_finish_max = 2
		# 验证码出错或者其他场景需要获取验证码2时，设置定时器
		self.yzm2_timeout = 30


		# 整个POST过程，等待所有线程响应结果的定时器
		self.post_finish_wait_time = 60 * 3

		# finish页面
		self.finish = ''

	#重载状态初始化
	def __init_status__(self):

		Plate.__init_status__(self)

		self.time_order_start = None
		self.time_order_end = None

		#处于约号过程
		self.status_order_ready = False  #约号准备状态
		self.status_order_run = False	 #约号运行状态

	def start(self):

		# 用户级监听子线程
		self.threading_listen = threading.Thread(target=self.__listen__)
		self.threading_listen.setDaemon(True)

		# 约号准备以及控制命令监听进程
		self.threading_listen_control = threading.Thread(target=self.__listen_control__)
		self.threading_listen_control.setDaemon(True)

		# select约号监听子线程
		self.threading_select_listen = threading.Thread(target=self.__listen_plate__)
		self.threading_select_listen.setDaemon(True)

		self.threading_listen.start()
		self.threading_listen_control.start()
		self.threading_select_listen.start()

		print_success('约号进程启动', self.userInfo.get('clsbdh', ''))
		# 在线监听进程,控制约号过程
		self.__listen_order__()


	def __get_xzhphm_handle__(self):

		time_start = time.time()

		def __get__xzhphm_handle_thread__(url, headers, time_start, index, queue_get):
			try:
				json_temp = {}
				# get /Xzhphm_Handler.asp页面
				# Refer页面不更新,不进行重定向
				response = self.__http_get__(url=url, headers=headers, allow_redirects=False)
				time_end = time.time()
				#self.__counter__('XZHPHM_HANDLE', 'GET', time_end - time_start, index)
				try:
					queue_get.put(response, True, 10)
				except Exception as ex:
					return
			except Exception as ex:
				self.__counter__('XZHPHM_HANDLE', 'GET', 'ERROR', index, ex)

		# 多线程同时发送
		queue_get = Queue(self.order_xzhphm_max)
		for index in range(0, self.order_xzhphm_max):
			# 验证码获取线程，根据数字和字母码与验证码获取速度调整顺序
			threading_temp = threading.Thread(target=__get__xzhphm_handle_thread__, args=(self.url_xzhphm_handler, \
																						  self.headers, time_start,
																						  index, queue_get,))
			threading_temp.setDaemon(True)
			threading_temp.start()

		count = 0
		response = None
		time_wait_start = time.time()
		while count < self.order_xzhphm_max and time.time() - time_wait_start < self.order_xzhphm_timeout:
			count += 1
			try:
				response = queue_get.get(True)
				if response and response.status_code == 302 and 'finish.aspx' in response.headers.get('location', ''):
					time_end = time.time()
					#self.__counter__('XZHPHM_HANDLE', 'GET', 'SUCCESS', time_end - time_start)
					self.url_xzhphm_handler = ''
					try:
						queue_get.close()
					except Exception as ex:
						self.__counter__('XZHPHM_HANDLE', 'GET', 'CLEAR_ERROR', ex)
					finally:
						return response

				else:
					time_end = time.time()
					try:
						self.__counter__('XZHPHM_HANDLE', 'GET', 'FAIL', response.status_code, response.url, \
										 response.headers.get('location', ''), time_end - time_start)
					except Exception as ex:
						self.__counter__('XZHPHM_HANDLE', 'GET', 'FAIL', response, time_end - time_start)
						pass
					continue
			except Exception as ex:
				self.__counter__('XZHPHM_HANDLE', 'GET', 'ERROR', ex)
		else:
			# return退出之前，还原url
			self.url_xzhphm_handler = ''
			self.__counter__('XZHPHM_HANDLE', 'GET', 'FAIL')
			return False

	# 根据finish连接，获取finish页面并选择上牌地点post
	def __post_finish__(self, response_para):

		def __get_finisn__(url,  index, queue_get):
			response = {}
			try:
				response = self.__http_get__(url, headers=self.headers,allow_redirects=False)
			except Exception as ex:
				self.__counter__('POST_FINISH', 'GET', 'ERROR', ex, index)
			finally:
				try:
					queue_get.put(response)
				except Exception as ex:
					pass

		def __post_finish_last__(url, postJson, queue_post):
			# post尝试起10个线程同时提交
			# 【3】Post finish页面
			response_post_finish = False
			try:
				headers = deepcopy(self.headers)
				headers["Content-Type"] = "application/x-www-form-urlencoded"
				headers["Referer"] = self.finish
				# 控制不重定向
				response_post_finish = self.__http_post__(url=url, data=postJson, headers=headers,allow_redirects=False)

				json_result = response2json(response_post_finish)
				try:
					if json_result and 'last' in json_result.get('location',''):
						response_get = self.__http_get__(url=self.url_host+json_result.get('location',''),headers=headers,allow_redirects=False)
						try:
							queue_post.put(response2json(response_get), True, 10)
						except Exception as ex:
							try:
								queue_post.put(False, True, 10)
							except Exception as ex:
								pass
					else:
						try:
							queue_post.put(False, True, 10)
						except Exception as ex:
							pass
				except Exception as ex:
					try:
						queue_post.put(False, True, 10)
					except Exception as ex:
						pass
			except Exception as ex:
				self.__counter__('POST_FINISH', 'POST', 'ERROR', ex)
				try:
					queue_post.put(False, True, 10)
				except Exception as ex:
					pass

		# 0 - 验证码错误
		# 200 - 选号成功
		def __check_finish__(response_check):

			time_end = time.time()
			if not response_check:
				self.__counter__('POST_FINISH', 'POST', 'FALSE_RESPONSE')
				return 1
			# yzm2错误,重新获取验证码
			elif '验证码输入错误,请重新输入' in response_check.get('text'):
				self.__counter__('POST_FINISH', 'POST', '验证码2失败')
				self.yzm2 = ''
				return 0

			elif '恭喜您选到您心仪的车牌号' in response_check.get('text'):
				#self.__counter__('POST_FINISH', 'POST', 'SUCCESS_BODY')
				self.__debug_select__('恭喜您选到您心仪的车牌号')
				# 停止运行
				self.run_enable = False
				return 200

			else:
				self.__counter__('POST_FINISH', 'POST', 'FAIL')
				return 1

		count = 0
		# 仅仅尝试3次，其他错误返回
		# 验证码错误才需要尝试
		while count < 3:

			# 【1】到get /finish.asp页面
			self.time_get_finish_start = time.time()
			if self.yzm2 == '':
				threading_yzm2 = threading.Thread(target=self.__get_yzm_from_url__,args=('2',))
				threading_yzm2.setDaemon(True)
				threading_yzm2.start()

			queue_get = Queue(self.select_order_get_finish_max)
			for index in range(0, self.select_order_get_finish_max):
				# 验证码获取线程，根据数字和字母码与验证码获取速度调整顺序
				threading_temp = threading.Thread(target=__get_finisn__,
												  args=(self.finish, index, queue_get,))
				threading_temp.setDaemon(True)
				threading_temp.start()

			# 监听多线程GET结果,接收到一个正确结果，立即返回
			count_get = 0
			response_get = None
			time_wait_start = time.time()
			while count_get < self.select_order_get_finish_max and time.time() - time_wait_start < self.get_finish_wait_time:
				count_get += 1
				try:
					response_get = queue_get.get(True)
					if response_get.status_code == 200:
						if '城西：蓝灵集团' in response_get.text or \
										'城东：锦泰小型汽车牌证办理点' in response_get.text:
							self.__counter__('POST_FINISH', 'GET', 'SUCCESS', self.finish)
							self.time_get_finish_end = time.time()
							break
						else:
							self.__counter__('POST_FINISH', 'GET', 'SUB_FAIL', response_get.status_code, self.finish)

					else:
						self.__counter__('POST_FINISH', 'GET', 'SUB_FAIL', response_get.status_code, self.finish)


				except Exception as ex:
					self.__counter__('POST_FINISH', 'GET', 'ERROR', self.select_order_get_finish_max, ex)
					pass
			else:
				self.__counter__('POST_FINISH', 'GET', 'FAIL', self.select_order_get_finish_max)
				# threading_yzm2.join(0.1)
				return False

			if self.yzm2 == '':
				# 码2线程执行结果确认，设置定时器，如果时间超过30s
				threading_yzm2.join(self.yzm2_timeout)

			# 手工更新referer
			self.headers["Referer"] = response_get.url
			postJson = get_value_from_body(response_get.text, {
				"__EVENTTARGET": 'lnkbtnqr',
				"__EVENTARGUMENT": '',
				"__LASTFOCUS": '',
				"__VIEWSTATE": serachFlag,
				"__EVENTVALIDATION": serachFlag,
				"ddlhplqd": self.userInfo['ddlhplqd'],  # "A001/A002
				"txt_yzm": self.yzm2,  # yzm2的验证码
			})

			# 多线程同时发送
			queue_post = Queue(self.select_order_post_finish_max)

			for index in range(0, self.select_order_post_finish_max):
				# 验证码获取线程，根据数字和字母码与验证码获取速度调整顺序
				threading_temp = threading.Thread(target=__post_finish_last__,
												  args=(self.finish, postJson, queue_post,))
				threading_temp.setDaemon(True)
				threading_temp.start()

			# 监听多线程GET结果,接收到一个正确结果，立即返回
			count_post = 0

			# 任务流监控开始时间
			time_wait_start = time.time()
			while count_post < self.select_order_post_finish_max and time.time() - time_wait_start < self.post_finish_wait_time:
				try:
					count_post += 1
					response_last = queue_post.get(True, 20)

					#记录第一个POST响应消息
					self.time_post_fininsh_end = time.time()

					status = __check_finish__(response_last)
					# 验证码错误,跳出，重新获取验证码，页面需要处理,前面需要好好处理一下
					if status == 0:
						self.__counter__('POST_FINISH','RUN','FAIL','YZM2')
						self.yzm2 = ''
						self.__debug_select__('码2错误')
						break

					elif status == 200:
						return True

					# 10个线程，所有线程都检查完毕，才确认本次约号失败
					else:
						continue

				except Exception as ex:
					self.__counter__('POST_FINISH', 'RUN', 'ERROR', ex)
					pass
			else:
				self.__counter__('POST_FINISH', 'RUN', 'FAIL')
				return False

	# 前置页面无，需要保证登录注册成功
	# body是预置内容
	def __order_ready__(self,src='listen_control'):

		def __is_ready_ok__():
			if self.__is_finish__() and self.yzm2 != '':
				return True
			else:
				return False

		# 必须获取到验证码流程和hphm信息之后才能往后
		while self.run_enable:

			if src == 'listen_control' and self.status_order_run:
				self.__debug_select__('约号进程接管了码1，码2和HPHM准备过程，等待5秒之后看约号结果')
				time.sleep(5)
				continue

			start_time = time.time()

			self.__debug_select__('准备码1，码2和HPHM')

			# 并行获取验证码1，验证码2和hphm
			threading_get_zbhphm_yzm = threading.Thread(target=self.__get_zbhphm_yzm___)
			threading_get_zbhphm_yzm.setDaemon(True)

			threading_get_yzm2 = threading.Thread(target=self.__get_yzm_from_url__,args=('2',))
			threading_get_yzm2.setDaemon(True)

			threading_get_yzm2.start()
			threading_get_zbhphm_yzm.start()

			threading_get_yzm2.join()
			if self.__retry_with_login__():
				end_time = time.time()
				self.__counter__('ORDER_READY', 'YZM2', 'RELOGIN', end_time - start_time)
				continue

			threading_get_zbhphm_yzm.join()
			if self.__retry_with_login__():
				end_time = time.time()
				self.__counter__('ORDER_READY', 'GET_HPHM_AND_YZM', 'RELOGIN', end_time - start_time)
				continue

			# 准备OK返回
			if __is_ready_ok__():
				end_time = time.time()
				self.__counter__('ORDER_READY', 'GET_HPHM_AND_YZM', 'SUCCESS', end_time - start_time)
				return True

			#没有准备就绪，需要继续准备
			else:
				self.__debug_select__('约号用户准备失败',len(self.img_codes),self.yzm1,self.yzm2)
				self.__clear_plate_filter__()
				continue

	# 预约车牌号，原则是，成功的步骤就不要有任何的网络和IP操作
	def __order_run__(self, order_request_para):

		self.__init_time__()

		self.time_order_start = time.time()

		#初始化
		self.status_success = False

		get_plate_time = time.time()
		try:
			xzhm = order_request_para['user_info']['xzhm']
			get_plate_time = float(order_request_para['user_info']['time'])

		except Exception as ex:
			self.__counter__('ORDER_RUN', 'GET_NEW_PLATE', 'ERROR', ex, self.time_order_start - get_plate_time)
			return

		if xzhm == '.....':
			json_temp = {
				'like': ','.join(self.userInfo['select_like']),
				'hate': ','.join(self.userInfo['select_hate']),
				'xxxq': ','.join(self.userInfo['select_xxxq']),
				'gltj': xzhm,
			}
		else:
			# 更换过滤条件,截取其中4个即可(5个精准查找)
			json_temp = {
				'like': ','.join(list(xzhm))[0:4],
				'hate': '',
				'xxxq': '',
				'gltj': xzhm,
			}


		self.__update__(json_temp)

		# 【1】再校验一下选择的号码是否符合要求
		try:
			if not self.__plate_is_ok__(xzhm):
				self.__counter__('ORDER_RUN', 'ERROR_PLATE', xzhm)
				self.__debug_select__('约号失败，号码不符合过滤条件', xzhm)
				return False
			else:
				pass
		except Exception as ex:
			self.__counter__('ORDER_RUN', 'CHECK_ERROR', xzhm, ex)
			self.__debug_select__('约号失败，号码过滤发生异常', xzhm, ex)
			return False

		count = 0



		# 重试两次
		while count < self.order_retry:
			count += 1

			response_plate = None

			# 【2】查询号牌
			try:

				response_plate = self.__get_plate_page__()

				if response_plate:
					pass
				else:
					self.__counter__('ORDER_RUN', 'FAIL_POST_QUERY_FILTER', xzhm,response_plate)
					self.__debug_select__('约号失败，查询号码页面报错', xzhm)
					continue

			except Exception as ex:
				self.__debug_select__('约号失败，查询号码发生异常', xzhm, ex)
				self.__counter__('ORDER_RUN', 'ERROR_POST_QUERY_FILTER', xzhm, ex)
				return

			self.headers['Referer'] = response_plate.url


			#self.__debug_select__('搜索号码', xzhm)
			# 【3】根据上一步查出的号牌页面搜索，不会有网络操作
			order_request = self.__get_plate__(response_plate)


			# 异常页面，目前看应该比较少进入该分支
			if self.status_plate == status.PLATE_PAGE_ERROR:
				self.__debug_select__('约号失败，车牌号码页面ERROR', xzhm)
				self.__counter__('ORDER_RUN', 'ERROR_GET_PLATE')
				if self.__is_offline__():
					self.__counter__('ORDER_RUN', 'RELOGIIN_GET_PLATE')
					break
				else:
					continue

			# 查询到号码
			elif self.status_plate == status.PLATE_NORMAL or self.status_plate == status.PLATE_LITTLE:
				pass

			# 号码已经查询不到
			elif self.status_plate == status.PLATE_NULL:
				self.__debug_select__('约号失败，查询不到该车牌号', xzhm)
				self.__counter__('ORDER_RUN', 'GET_PLATE_NULL')
				break
			else:
				self.__debug_select__('约号失败，号牌分析未知错误', xzhm)
				self.__counter__('ORDER_RUN', 'GET_PLATE_ERROR', self.status_plate)
				continue


			xzhm = order_request['user_info'].get('xzhm', '.....')
			# 获取Xzhphm_Handler.ashx页面
			if 'user_info' in order_request and 'url' in order_request['user_info']:
				self.url_xzhphm_handler = order_request['user_info']['url']
				#self.__counter__('ORDER_RUN', 'XZHPHM_HANDLER_URL', self.url_xzhphm_handler)
			# 获取失败，重新查号
			else:
				self.__debug_select__('约号失败，查询不到该车牌号', xzhm)
				self.__counter__('ORDER_RUN', 'FAIL_GET_XZHP_URL')
				continue

			#self.__counter__('ORDER_RUN', 'GET_XZHPHM_HANDLE', 'TRY', self.url_xzhphm_handler)

			self.time_get_handle_start = time.time()
			response = self.__get_xzhphm_handle__()
			self.url_xzhphm_handler = ''
			self.time_get_handle_end = time.time()

			try:
				# 获取失败
				if not response or not 'finish' in response.headers.get('location', ''):
					self.__debug_select__('约号失败，获取不到该车牌号的finish页面', xzhm,'%.3f' %(self.time_get_handle_end-self.time_order_start))
					self.__counter__('ORDER_RUN', 'GET_XZHPHM_HANDLE', 'FAIL')
					continue
			except Exception as ex:
				self.__debug_select__('约号失败，获取该车牌号的finish页面发生异常', xzhm, ex)
				self.__counter__('ORDER_RUN', 'GET_XZHPHM_HANDLE', 'ERROR', ex)
				continue

			self.finish = self.url_host + response.headers.get('location', '')

			# FINISH操作页面
			try:
				result = self.__post_finish__(response)
			except Exception as ex:
				self.__debug_select__('约号失败，POST该车牌号的finish页面发生异常', xzhm, ex)
				result = False

			self.finish = ''

			end_time = time.time()

			if result:
				self.__counter__('ORDER_RUN', 'POST_FINISH', 'SUCCESS', end_time - self.time_order_start, xzhm)
				self.__debug_select__(self.userInfo.get('clsbdh'), '约号成功', xzhm)
				self.status_success = True
				self.run_enable = False

			else:
				self.__debug_select__('约号失败，FINISH页面抢号失败',xzhm)
				self.__counter__('ORDER_RUN', 'POST_FINISH', 'FAIL', end_time - self.time_order_start, xzhm)
				if self.__retry_with_login__():
					end_time = time.time()
					self.__counter__('ORDER_RUN', 'POST_FINISH', 'RELOGIN', end_time - self.time_order_start, xzhm)
				continue

		fmt_float = '%.3f'

		if self.status_success:

			order_result = {
				'task_type': 'order',
				'handle_type': 'response',
				'user_info': {
					'clsbdh': self.userInfo.get('clsbdh', ''),
					'result': 'success',
					'xzhm': xzhm,
					#'time1':fmt_float % (self.time_order_start - get_plate_time),
					#'time2':
				}
			}

			# 发送邮件
			try:
				send_mail(order_result)
			except Exception as ex:
				pass

			try:
				# 选号成功，通知服务器
				send_with_ack(self.addr_server_msg, order_result)
			except Exception as ex:
				self.__counter__('ORDER_RUN', 'POST_FINISH', 'NOTIFY_ERROR', ex)


		self.__debug_select__('重要时间', '查询出号时间',
							  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_plate_time)  ))

		self.__debug_select__('重要时间', '约号启动时间',
							  fmt_float % (self.time_order_start - get_plate_time))

		self.__debug_select__('重要时间', '提交条件时间',
							  fmt_float % (self.time_query_post_hphm_end - self.time_query_post_hphm_start),
							  fmt_float % (self.time_query_post_hphm_end - get_plate_time))

		self.__debug_select__('重要时间', '获取号牌时间',
							  fmt_float % (self.time_query_get_plate_end - self.time_query_post_hphm_end),
							  fmt_float % (self.time_query_get_plate_end - get_plate_time))

		self.__debug_select__('重要时间', '约号点击号牌',
							  fmt_float % (self.time_get_handle_end - self.time_get_handle_start),
							  fmt_float % (self.time_get_handle_end - get_plate_time))

		self.__debug_select__('重要时间', '码2页面时间',
							  fmt_float % (self.time_get_finish_end - self.time_get_finish_start),
							  fmt_float % (self.time_get_finish_end - get_plate_time))

		self.__debug_select__('重要时间', '约号完成时间',
							  fmt_float % (self.time_post_fininsh_end - self.time_get_finish_end),
							  fmt_float % (self.time_post_fininsh_end - get_plate_time))

		# 测试号或者预约号码清除
		self.test_like_list = []
		self.all_flag = True

		try:
			self.__order_resume__()
		except Exception as ex:
			pass



	#约号用户控制监听
	def __listen_control__(self):

		#检查准备状态，包括登录等等
		def order_ready_check():

			if self.status_order_run:
				self.__debug_select__('正在选号，不能响应任何消息')
				return

			self.status_order_ready = False

			#检查时间，如果超时需要重新登录
			time_now = time.time()
			if time_now - self.time_login_end > self.timeout_login or not self.status_online:
				# select用户先登录
				try:
					self.__relogin__()
				except Exception as ex:
					self.__debug_select__('约号准备过程中登录发生异常，请停止用户重新启动', ex)
					return

			#初始准备，设置all_flagS为True
			#print_debug('-----------约号用户准备HPHM，码1和码2-----------------')
			self.all_flag = True
			time_start = time.time()
			try:
				self.__order_ready__()
			except Exception as ex:
				# 验证错误
				self.__counter__("ORDER", 'FAIL_READY', ex)
				self.__debug_select__('预约准备异常，请停止用户重新启动',ex)
				return
			else:
				self.status_order_ready = True
				time_now = time.time()
				self.__debug_select__('预约准备成功', len(self.img_codes),self.yzm1,self.yzm2,'耗时','%.3f' %  (time_now  - time_start))
				self.__counter__("ORDER", 'SUCC_READY', len(self.img_codes), self.yzm1, self.yzm2)

		# 首先检查ready状态，是否需要登录或者重新登录等等
		order_ready_check()
		while self.run_enable:
			try:
				task = self.queue_user['queue_in_control'].get(True,self.timeout_yzm1)
			except Exception as ex:
				self.__debug_select__('码1超时刷新')
				self.yzm1 = ''
				#首先检查ready状态，是否需要重新登录等等
				order_ready_check()
				continue

			#有任务到达
			task_type = task.get('task_type')
			handle_type = task.get('handle_type')
			if task_type == 'yzm' and handle_type == 'change':
				# 理解更换验证码1
				if task['user_info']['sn'] == '1':
					self.yzm1 = ''
					self.__counter__('YZM1', 'CHANGE', 1)
					self.__debug_select__('客户端要求码1刷新')
				# 更换验证码2
				elif task['user_info']['sn'] == '2':
					self.yzm2 = ''
					self.__counter__('YZM2', 'CHANGE', 2)
					self.__debug_select__('客户端要求码2刷新')
				# 位置类型，不会走到这个分支
				else:
					self.__counter__('YZM', 'UNKNOW_TYPE', task['user_info']['sn'])
					continue

				# 马上重新登录
			elif task_type == 'select' and handle_type == 'relogin':
				self.__counter__('SELECT', 'RELOGIN', 'BY_USER')
				self.__debug_select__('客户端要求重新登录')
				#重置在线状态
				self.status_online = False

			elif task_type == 'select' and handle_type == 'refresh':
				self.__counter__('SELECT', 'REFRESH', 'BY_USER')
				self.__debug_select__('需要刷新查找条件')
				self.__clear_plate_filter__()

			elif task_type == 'select' and handle_type == 'order':
				#self.__counter__('SELECT', 'ORDER', 'BY_USER')
				json_order_request = {
					'task_type':'order',
					'handle_type':'request',
					'user_info':{
						'xzhm':'.....',
						'time':time.time(),
					}
				}

				self.queue_user['queue_in_plate'].append(json_order_request)
				self.queue_user['queue_in_order'].put('order')
				continue

			else:
				continue

			order_ready_check()

	#刷新过滤条件
	def __refresh_filter__(self):
		json_refresh = {
			'task_type':'select',
			'handle_type':'refresh',
			'user_info':{}

		}
		try:
			self.queue_user['queue_in_control'].put(json_refresh,True,1)
		except Exception as ex:
			self.__counter__('REFRESH_FILTER','ERROR',ex)
			self.__debug_select__('要求刷新过滤条件异常，请手动处理',ex)

	def __order_resume__(self):
		json_resume = {
			'task_type': 'broadcast',
			'handle_type': 'resume',
			'user_info': {},
		}

		# 选中号码更新
		self.test_like_list = []
		self.all_flag = False

		boadcast(json_resume)
		self.status_order_run = False

	# 选号，保持在线，到任一选号页面驻留，在选号页面获取前置获取验证码2的方式来检测在线
	def __listen_order__(self):



		# 每40s刷新一次验证码；最长每15分钟强制登录一次
		while self.run_enable:

			try:
				# order_request复用一下，可能是更换验证码请求，验证码1比较简单，直接到下一步
				# 验证码2需要重新ready
				# 如果队列大于0
				if len(self.queue_user['queue_in_plate']) > 0:
					order_request = self.queue_user['queue_in_plate'].pop()
				else:
					try:
						self.queue_user['queue_in_order'].get(True)
					except Exception as ex:
						self.__debug_select__('等待约号指令发生异常，继续监听',ex)
						continue

					if len(self.queue_user['queue_in_plate']) > 0:
						order_request = self.queue_user['queue_in_plate'].pop()

				task_type = order_request.get('task_type', '')
				handle_type = order_request.get('handle_type', '')
				# 直接约号
				if task_type == 'order':

					try:
						local_time = order_request['user_info'].get('local_time', time.time())
						plate_time = time.time() - local_time

						xzhm = order_request['user_info'].get('xzhm', '')

						if plate_time > self.timeout_plate:
							self.__debug_select__('约号失败，号码超时', xzhm, \
												  '号牌到达时间', local_time, '经过时间', plate_time, '超时定时器', self.timeout_plate)
							continue
						else:
							pass
							#print_debug('号码有效', xzhm)

						#选中号码更新
						if xzhm == '.....':
							self.test_like_list = self.userInfo['like_list']
						else:
							self.test_like_list = list(xzhm)
						self.all_flag = False

						json_pause = {
							'task_type':'broadcast',
							'handle_type':'pause',
							'user_info':{},
						}
						boadcast(json_pause)

						while not self.status_order_ready:
							#self.__debug_select__('约号用户还没有准备就绪，等候1秒之后重试')
							time.sleep(0.2)

						self.status_order_run = True
						try:
							self.__order_run__(order_request_para=order_request)
						except Exception as ex:
							self.__counter__('SELECT', 'ORDER_RUN', 'ERROR', ex)
							self.__debug_select__('约号过程发生异常', ex)

						self.__order_resume__()
						self.__refresh_filter__()

					except Exception as ex:
						self.__counter__('SELECT', 'ORDER_RUN', 'ERROR', ex)
						self.__debug_select__('约号过程发生异常', ex)
						print_error('约号过程发生异常', ex)
						pass

				else:
					continue


			# 异常一般是超时导致，继续后续流程
			except Exception as ex:
				self.__debug_select__('监听约号指令异常', ex)

	# 上线请求，主要是要在公网上打洞，让查询电脑知道select用户的信息
	def __listen_select_login__(self, udp):
		try:

			# 连接服务器，IP更新
			json_heart = {
				'task_type': 'login',
				'handle_type': 'online',
				'user_info': {
					'hostname': self.configInfo.get('hostname', gethostname()),
				}

			}

			login_keys = ['clsbdh', 'query_pc', 'select_like', 'select_hate', 'select_xxxq', \
						  'select_gltj', 'select_pctj']

			for key in login_keys:
				if key in self.userInfo:
					json_heart['user_info'][key] = self.userInfo[key]

			udp.settimeout(20)
			# 发送给登录进程地址
			addr_select_login = (
				self.configInfo.get('server_host', 'www.wuyoubar.cn'),
				int(self.configInfo.get('select_login', '61237')))

			while True:
				try:
					# self.__debug_select__('约号用户尝试更新信息到服务器')
					self.__counter__('SELECT_LOGIN', 'TRY', addr_select_login)
					udp.sendto(dumps(json_heart).encode(), addr_select_login)

					data, addr = udp.recvfrom(10 * 1024)

					json_temp = loads(data.decode('utf-8'))

					task_type = json_temp.get('task_type')
					handle_type = json_temp.get('handle_type')

					if json_temp['task_type'] == 'login' and json_temp['handle_type'] == 'response' and \
									json_temp['user_info'] == 'success':
						break
					# 约号请求已经发送过来，则表明上线已经成功
					elif json_temp['task_type'] == 'order':
						if handle_type == 'rquest':
							print_success('有号码查询成功，登录成功', json_temp['user_info'].get('xzhm', ''))
							self.__new_plate__(json_temp)
							pass
						break
					else:
						self.__counter__('SELECT_LOGIN', 'FAIL', json_temp['task_type'], json_temp['handle_type'],
										 json_temp.get('user_info', 'unknow'))

					time.sleep(2)
				except Exception as ex:
					self.__counter__('SELECT_LOGIN', 'HEART', ex)
					time.sleep(2)

			self.__counter__('SELECT_LOGIN', 'SUCCESS')

		except Exception as ex:
			self.__counter__('SELECT_LOGIN', 'ERROR', ex)

	def __new_plate__(self, json_data):
		if not ('user_info' in json_data and 'xzhm' in json_data['user_info'].keys()) or \
						json_data['user_info'].get('xzhm', '') in self.plate_list:
			return
		else:
			pass

		# 等待3s就可以，不能等待时间太长，暂时停止
		try:

			json_plate = deepcopy(json_data)
			# 号码加上一个本地定时器
			json_plate['user_info']['local_time'] = time.time()

			#
			if len(self.queue_user['queue_in_plate']) == 0:
				self.queue_user['queue_in_plate'].append(json_plate)
				self.queue_user['queue_in_order'].put(json_data, True, 2)
			else:
				self.queue_user['queue_in_plate'].append(json_plate)
				print_infor('约号用户正在选号，新查询车牌号自动入队，其他命令暂不支持')


		except Exception as ex:
			self.__debug_select__('约号用户消息监听异常')
			pass

		self.plate_list.append(json_data['user_info'].get('xzhm', ''))
		self.__counter__('SELECT_LISTEN', 'XZHM', json_data['user_info']['xzhm'])
		self.__debug_select__('约号用户消息监听到号码', json_data['user_info'].get('xzhm', ''))

	# 监听约号线程
	def __listen_plate__(self):
		# 监听接口定义以及端口上报到服务器
		udp = socket(AF_INET, SOCK_DGRAM)
		# 随机绑定端口
		udp.bind(('', 0))

		self.__listen_select_login__(udp)

		time.sleep(1)

		plate_list = []
		# 定时器设置为20s，每20s与服务器通信一次
		udp.settimeout(20)
		while True:
			try:

				# self.__debug_select__('约号用户正在监听',self.userInfo.get('gltj'),self.userInfo.get('pctj'))

				data, addr = udp.recvfrom(50 * 1024)
				udp.sendto('ACK'.encode(), addr)

				json_data = loads(data.decode('utf-8'))
				self.__new_plate__(json_data)

			except Exception as ex:
				self.__counter__('SELECT_LISTEN', 'HEART', self.userInfo.get('gltj'), self.userInfo.get('pctj'))
				self.__listen_select_login__(udp)

			# 确保监听程序正常，重新赋值
			# 不要初始化和重新绑定


#查询函数
#cget_yzm 是C语言分析验证码函数
def query(userInfo,queue_in):

	counter(log_file,'QUERY','INITIAL',userInfo.get('clsbdh','USER'))

	task_type = userInfo.get('task_type')


	try:
		if task_type == 'query':
			#新建查询号牌的用户
			query_user = Query(userInfo,queue_in)
			query_user.start()
		elif task_type == 'select':
			order_user = Order(userInfo,queue_in)
			order_user.start()
		else:
			print_error('未知的任务类型',task_type)
		
	except Exception as ex:
		counter(log_file, 'QUERY', 'EXIT', 'ERROR',ex,userInfo.get('clsbdh','USER'))
		print_error ('进程发生异常，马上退出',ex )
