#!/usr/bin/env python
#coding:utf-8


from json import  dumps,loads

#普通消息
HEADER_NULL = b''
HEADER_UNKNOWN = None

def msg_encode(json_data, msg_type=HEADER_NULL):
	try:
		if msg_type == HEADER_NULL:
			return dumps(json_data).encode()
		#心跳消息，暂时不加头
		elif msg_type == HEADER_HEART:
			return HEADER_HEART + dumps(json_data).encode()

		else:
			return dumps(json_data).encode()

	except Exception as ex:
		return HEADER_ERROR

def msg_decode(data,msg_type=HEADER_NULL):
	try:
		#未知的包头，等后续所有消息均加上头之后再修改
		if msg_type == HEADER_UNKNOWN:
			pass

		#空头，兼容原来没有头的格式，后面需要修改
		if msg_type == HEADER_NULL:
			return loads(data)

		#如果头和解码格式不一致
		if msg_type != data[:20]:
			return False

		if data[:20] == HEADER_HEART:
			json_data = loads(data[20:].decode())

			try:
				task_type = json_data.get('task_type', '')
				handle_type = json_data.get('handle_type', '')
				if task_type != 'login' or \
						'user_info' not in json_data or json_data['user_info'].get('hostname', '') == '':
					return False
				else:
					return json_data
			except Exception as ex:
				return False

		else:
			return False

	except Exception as ex:
		return False




#登录消息
#HEADER_LOGIN = b'00000000000000000001'
#心跳消息
HEADER_HEART = b'00000000000000000010'

#验证码图片消息
HEADER_YZM_IMG = b'0'*20
#异常消息
HEADER_ERROR = b'1'*20



