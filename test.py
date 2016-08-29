#coding:utf-8

#导入html解析
from bs4 import BeautifulSoup


from net import *
from struct import pack,unpack
from hashlib import md5
import time
import os
import random

import ctypes


def yzm():
	try:
		try:
			# 本地加载dll，验证码识别模块初始化
			lm_dll = ctypes.CDLL('./config/lm.dll')
			# 加载进来，然后生成共享的函数
			model_path = ctypes.c_char_p(b'./config/model_4chuang_0701')
			# path_bytes = ctypes.c_int(len('./config/model_4chuang_0701'))
			load_result = lm_dll.LoadModel(model_path, ctypes.c_int(100))
			# 本地引用获取验证码函数
			cget_yzm = lm_dll.LM_REC_2
		except Exception as ex:
			print( 'YZM_FX', 'LOAD', 'ERROR', ex,)

		print( 'YZM_FX', 'START')

		# tcp接口监听，接收到消息立即放入队列缓存
		#while True:

		with  open('./temp/save_listen_test.png','rb') as yzm_file:
			data = yzm_file.read()

		result_buf = ctypes.c_char_p(b'')
		cget_yzm(ctypes.c_char_p(data), ctypes.c_int(len(data)), result_buf, ctypes.c_int(20))

		yzm_data = result_buf.value  #b'\xd1\xb8xr\xbc\xa4'
		yzm = result_buf.value
		print(yzm,yzm_data)



	except Exception as ex:
		print ( 'YZM_FX', 'ERROR', ex,)

	finally:
		print( 'YZM_FX', 'RESET')
		#lm_dll.DestroyModel()


	#print ret

def __create_user_clsbdh():
		code_dict = {'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,
			'J':1,'K':2,'L':3,'M':4,'N':5,'P':7,'R':9,
			'S':2,'T':3,'U':4,'V':5,'W':6,'X':7,'Y':8,'Z':9,
			'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,}

		Brr = [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]


		plate_code ="ABCDEFGHJKLMNPRSTUVWXYZ1234567890"

		car_type = ['WBAFE412','JT1AP132','JT8AP616','JT5AP194','JT9AP378','JT3AM547','JT6AP725',\
			'JT5DP741','JT9AM732','JT3AP272','JT8AP825','JT1AP826','JT3AP258','JT4AM394',]

		Year = 'DEFGHJKLMNPRSTVWXY123456789'

		temp = random.choice(car_type)  + '*' + ''.join(random.sample(Year,1)) + ''.join(random.sample(plate_code,7))

		sum_brr = 0
		for index in range(0,len(temp)):
			if index != 8:
				code = temp[index]
				sum_brr += code_dict[code] * Brr[index]

		else:
			mod_brr = sum_brr % 11
			if mod_brr == 10:
				temp = temp[:8] + 'X' + temp[9:]
			else:
				temp =  temp[:8] + str(mod_brr) + temp[9:]  

		return temp

#车牌号，过滤条件
def plate_test(plate,gltj=''):	


	#二维数组保存，第一级或条件，只要true就返回，第二级与条件，全部true
	gltj_list = [item.strip() for item in gltj.split('|')]




	num = '0123456789'
	word = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz'

	#全字段匹配，按位比较
	def filter_all(plate,item):
		same_num = []
		same_word = []
		same = []
		#按位匹配
		for i in range(0,5):
			#数字字母任意
			if item[i] == '.':
				continue


			#数字限定,不满足条件则跳出
			elif item[i] == '%':
				if not plate[i] in num:
					break
				else:
					continue

			#字母限定	
			elif item[i] == '@':
				if not plate[i] in word:
					break
				else:
					continue

			#数字字母相同
			elif item[i] == '#':
				same.append(plate[i])

			#数字相同
			elif item[i] == '$':
				#非数字，返回
				if plate[i] not in num:
					break
				same_num.append(plate[i])


			#字母相同
			elif item[i] == '^':
				#非字母，返回
				if plate[i] not in word:
					break

				same_word.append(plate[i])
			else:
				#不等于普通字符，返回
				if item[i] != plate[i]:
					break

		else:
			#同号条件满足,返回True
			if len(set(same)) <= 1 and len(set(same_word)) <= 1 and len(set(same_num)) <= 1:
				return True

		return False

	#部分字段比较
	def filter_sub(plate,item):
		#两个特征自己必须隔开
		if '+' in item:
			#两个
			add_items = [temp_item.strip() for temp_item in item.split('+')]
			#+只允许连接两个元素
			if len(add_items) != 2:
				return False
			#条件不满足在
			elif not add_items[0] in plate  or not add_items[1] in plate or \
				add_items[0]+add_items[1] in plate:
				return False
			#'+'条件过滤满足
			else:
				return True

		#两个特征字符之间的任务间隔
		elif '.' in item:
			add_items = [temp_item.strip() for temp_item in item.split('.')]
			#.只允许连接两个元素
			if len(add_items) != 2:
				return False
			for add_item in add_items:
				#不满足
				if not add_item in plate:
					return False

			#条件过滤最终满足
			else:
				return True

		#同一个号码或者字符出现次数，主要针对三同场景
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


		
	#外层 or条件遍历
	for or_item in gltj_list:

		and_list = [item.strip() for item in or_item.split('&')  ]

		#and_list遍历
		for item in and_list:

			#正向过滤
			flag = True

			#！非条件,反向过滤
			if item.startswith('!'):
				item = item[1:]
				flag = False

			#条件为空
			if item is None or item.strip() == '':
				continue

			len_item = len(item.strip())
			#按位过滤匹配
			if len_item == 5:

				#正向或者反向过滤匹配成功
				if filter_all(plate,item) == flag:
					continue
				else:
					break

				#程序运行到此处，and条件已经判定为false
			else:
				if filter_sub(plate,item) == flag:
					continue
				else:
					break

			#有一个条件不满足False，则这一组and_list不再判断
			break

		#完成之后，整个队列结果是True，则返回；如果是false，则遍历下一个or_item
		else:
			return True

		#or_item继续遍历
		continue

	#所有or_item均没有成功返回True，则返回False
	else:
		return False



def get_blrq():
	body = ''
	with open('./06 cd1_two.aspx','r') as webfile:
		body = webfile.read()

	soup = BeautifulSoup(body,"html",from_encoding='utf-8')
	blrq = soup.find(id='blrq')
	if blrq == None:
		print ('GET the blrq html fail' , body)
		return

	print ('blrq:',blrq)

	options = blrq.find_all('option')
	if len(options) > 0:
		print (options[0])
		print ( options[0].get('value',''))





if __name__ == '__main__':

	input_str = input('enter q to quit:')
	while input_str != 'q':


		if input_str == 'code':
			fontTemplates = []
			for i in '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ' :
				fontTemplates.append((str(i), md5.new(open('./img_code_src/'+str(i)+".png",'rb').read()).digest()))

			print (fontTemplates)
			md5_temp = md5.new(open('./image_temp/00a3efe0744b4e81ae531e2ef6dfa1bc.png','rb').read()).digest()

			for font in fontTemplates:
				if md5_temp == font[1]:
					print (font[0])
					break

		if input_str == 'file':
			file_list  = sorted(os.listdir('./config/'),reverse=True)
			print (file_list)


		elif input_str == 'dll':

			yzm()

		elif input_str == 'plate':
			print( __create_user_clsbdh())

		elif input_str == 'blrq':
			get_blrq()


		elif input_str == 'yzm':

			with open('./yzm.png','rb') as yzm_file:
				img = yzm_file.read()

				addr = '127.0.0.1'

				flag = 'JT3AM5478D3258286'

				fmt = '!17s'

				flag_binary = pack(fmt,flag)
				print (flag_binary)
				data = flag_binary + img

				host_data_list = [{
					'addr':'127.0.0.1',
					'data':{
						'task_type':'yzm',
						'handle_type':'yzm1',
						'user_info':{
							'data': flag_binary + img
						}
					}
				}]

				#sender(host_data_list)

		else:
			pass


		input_str = input('enter q to quit:')

