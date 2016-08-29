#!/usr/bin/env python
#coding:utf-8



import ctypes
import  random
#导入html解析
from bs4 import BeautifulSoup

from hashlib import md5
from enum import Enum, unique
from log import  debug_save
import  time
#windows声音
import winsound
from json import  dumps

def create_user_clsbdh():

	#符号权重
	code_dict = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
				 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
				 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
				 '0':0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,}

	#位置权重
	Brr = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

	plate_code = "ABCDEFGHJKLMNPRSTUVWXYZ1234567890"

	car_type = ['WBAFE412', 'JT1AP132', 'JT8AP616', 'JT5AP194', 'JT9AP378', 'JT3AM547', 'JT6AP725', \
				'JT5DP741', 'JT9AM732', 'JT3AP272', 'JT8AP825', 'JT1AP826', 'JT3AP258', 'JT4AM394', ]

	Year = 'DEFGHJKLMNPRSTVWXY123456789'

	temp = random.choice(car_type) + '*' + random.choice(list(Year)) + ''.join(random.sample(plate_code, 7))

	sum_brr = 0
	for index in range(0, len(temp)):
		if index != 8:
			code = temp[index]
			sum_brr += code_dict[code] * Brr[index]

	else:
		mod_brr = sum_brr % 11
		if mod_brr == 10:
			temp = temp[:8] + 'X' + temp[9:]
		else:
			temp = temp[:8] + str(mod_brr) + temp[9:]

	return temp

#车牌号，过滤条件
def plate_is_ok(plate,gltj='',pctj=''):


		#二维数组保存，第一级或条件，只要true就返回，第二级与条件，全部true
		gltj_list = [item.strip() for item in gltj.split('|')]
		pctj_list = [item.strip() for item in pctj.split('|')]

		hate = []
		like = ['1','2','T','P','1']

		# 排除号
		if len(set(hate) & set(plate)) > 0:
			print ('hate fail')
			return False

		# 优选号和排除号条件Check
		plate_code = list(plate)
		for item in like:
			if item in plate_code:
				plate_code.remove(item)
			else:
				print  (like,plate_code)
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

		if not filter_list_gl(plate, gltj_list):
			print('过滤条件不能通过')
			return False

		if not  filter_list_pc(plate, pctj_list):
			print('排除条件不能通过')
			return False

		print (filter_list_gl(plate, gltj_list) and  filter_list_pc(plate, pctj_list))

		return True

def plate_featrue(xzhm):

	if xzhm == '.....':
		return 0

	hm_code = list(xzhm)

	hm_set = list(set(hm_code))

	max_num = 0
	for code in hm_set:
		max_temp = hm_code.count(code)
		if max_temp > max_num:
			max_num = max_temp
	else:
		return max_num



def beep(count_max = 1,freq=2000,time=250):
	count = 0
	while count < count_max:
		count += 1
		winsound.Beep(freq, time)


#通过比较md5来匹配选号条件页面的数字和字母图片
def get_code(img_data,fontTemplates):

	m = md5(img_data)
	#m.update(img_data)
	img_data_md5 = m.hexdigest()


	if img_data_md5 in fontTemplates:
		return fontTemplates[img_data_md5]
	# 无法识别就设置空
	else:
		#print(img_data_md5,fontTemplates)
		return ''

serachFlag = '____to_be_search_in_body'
def get_value_from_body(body='',jsonValue={}):
	soup = BeautifulSoup(body,"html.parser")#,from_encoding='utf-8')
	for key in jsonValue:
		if  jsonValue[key] == serachFlag:
			html_item = soup.find(id=key)
			if html_item is None:
				jsonValue[key] = ''  #htmml未定义，则重置为空
				#debug('get_value_from_body:error',key)
			else:
				jsonValue[key] = html_item.get('value','')
		else:
			pass

	return jsonValue


def response2json(response):
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

			return json_result
		except Exception as ex:
			print_error('消息解析错误异常',ex)
			return False
	else:
		return False


@unique
class status(Enum):
	INIT = 1

	#数字字母码图片未获取完全
	IMG_CODE_LITTLE = 3001

	#查号页面错误
	PLATE_PAGE_ERROR = 4404
	#查号结果为空
	PLATE_NULL = 4004
	PLATE_NORMAL = 2000
	PLATE_LITTLE = 4001
	PLATE_TIMOUT = 4005

	HPHM_NULL = 9000	#空
	HPHM_TEXT = 9001	#文本，没有图片
	HPHM_LOGIN = 9002 #重登陆
	HPHM_OTHER = 9099

	#需要重新登录
	RELOGIN = 409

@unique
class client(Enum):
	UI='ui'
	QUERY='query'
	SELECT='select'
	CLIENT='client'



#颜色枚举
# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_BLACK = 0x00  # black.
FOREGROUND_DARKBLUE = 0x01  # dark blue.
FOREGROUND_DARKGREEN = 0x02  # dark green.
FOREGROUND_DARKSKYBLUE = 0x03  # dark skyblue.
FOREGROUND_DARKRED = 0x04  # dark red.
FOREGROUND_DARKPINK = 0x05  # dark pink.
FOREGROUND_DARKYELLOW = 0x06  # dark yellow.
FOREGROUND_DARKWHITE = 0x07  # dark white.
FOREGROUND_DARKGRAY = 0x08  # dark gray.
FOREGROUND_BLUE = 0x09  # blue.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_SKYBLUE = 0x0b  # skyblue.
FOREGROUND_RED = 0x0c  # red.
FOREGROUND_PINK = 0x0d  # pink.
FOREGROUND_YELLOW = 0x0e  # yellow.
FOREGROUND_WHITE = 0x0f  # white.

# Windows CMD命令行 背景颜色定义 background colors
BACKGROUND_DARKBLUE = 0x10  # dark blue.
BACKGROUND_DARKGREEN = 0x20  # dark green.
BACKGROUND_DARKSKYBLUE = 0x30  # dark skyblue.
BACKGROUND_DARKRED = 0x40  # dark red.
BACKGROUND_DARKPINK = 0x50  # dark pink.
BACKGROUND_DARKYELLOW = 0x60  # dark yellow.
BACKGROUND_DARKWHITE = 0x70  # dark white.
BACKGROUND_DARKGRAY = 0x80  # dark gray.
BACKGROUND_BLUE = 0x90  # blue.
BACKGROUND_GREEN = 0xa0  # green.
BACKGROUND_SKYBLUE = 0xb0  # skyblue.
BACKGROUND_RED = 0xc0  # red.
BACKGROUND_PINK = 0xd0  # pink.
BACKGROUND_YELLOW = 0xe0  # yellow.
BACKGROUND_WHITE = 0xf0  # white.

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def __set_cmd_text_color__(color_foregruound, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color_foregruound)
    return Bool

def __resetColor__():
	__set_cmd_text_color__(FOREGROUND_WHITE)

def print_warnning(*info):
	__set_cmd_text_color__(FOREGROUND_YELLOW)
	str_print = '【警告】'+ str( time.strftime("%H:%M:%S ",time.localtime()))
	for item in info:
		str_print += str(item) + ' '

	print (str_print)
	__resetColor__()

def print_error(*info):
	__set_cmd_text_color__(FOREGROUND_RED)
	str_print = '【错误】'+ str( time.strftime("%H:%M:%S ",time.localtime()))
	for item in info:
		str_print += str(item) + ' '

	print (str_print)

	__resetColor__()

def print_infor(*info):
	str_print = '【提示】'+ str( time.strftime("%H:%M:%S ",time.localtime()))
	for item in info:
		str_print += str(item) + ' '

	print (str_print)


def print_success(*info):
	__set_cmd_text_color__(FOREGROUND_GREEN)
	str_print = '【成功】' + str( time.strftime("%H:%M:%S ",time.localtime()))
	for item in info:
		str_print += str(item) + ' '

	print (str_print)
	__resetColor__()

def print_debug(*info):
	__set_cmd_text_color__(FOREGROUND_DARKPINK)
	str_print  =  '【测试】'+ str( time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime()))
	for item in info:
		str_print += str(item) + ' '
	print(str_print)
	__resetColor__()


if __name__ == '__main__':
	input_str = raw_input('enter q to quit:')
	while input_str != 'q':
		if input_str == 'pt':
			plate = raw_input('plate:')
			gltj = raw_input('gltj:')
			pctj = raw_input('pctj:')

			print ('check:',plate_is_ok(plate,gltj,pctj))
