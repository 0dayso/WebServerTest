#!/usr/bin/env python
#coding:utf-8

from tkinter import *

from PIL import Image, ImageTk
import io
from json import dumps,loads
import time

from common import  *
from log import counter,counter_print
from threading_pool import Threading_pool

from socket import *
from math import *
from copy import deepcopy
from login import  *

import  threading
from  multiprocessing import  freeze_support


from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


ui_log = 'UI ' + time.strftime("%Y-%m-%d",time.localtime())





def msg(text='',count_max = 100):



	root = Tk()

	root.geometry('600x600+300+20')
	#窗口大小固定
	root.resizable(False,False)

	#frame = Frame(height=600,width=600,bg='yellow')
	#frame.pack(expand='yes',fill='both')

	label_titile = {'font': ('Times', 16), 'height': 2, 'bg': 'yellow'}
	label_temp = Label(root,text=text, **label_titile)
	label_temp.pack(expand='yes',fill='both')

	root.update()


	root.mainloop()

def new_user():

	clsbdh = create_user_clsbdh()

	tbZjhm = ''
	tbFpbh = ''
	for i in range(0, 18):
		tbZjhm += random.choice(list('0123456789'))

		tbFpbh += random.choice(list('0123456789'))

	user_info = {
		'clsbdh':clsbdh,
		'clxh':clsbdh[0:8],
		'rdclxz': '2',  #国产进口
		'tbFdjh': '12345678',
		'tbFpbh': tbFpbh[0:8],

		'tbSyr': '李四',
		'ddlZjzl': 'A',	#身份证
		'bldd': '510100',
		'blrq': time.strftime("%Y-%m-%d",time.localtime()),
		'ddlXzhq': '510100',


		'tbZjhm': tbZjhm,
		'tbZzzh': '',
		'tbDz': '四川省成都市',
		'txtyzbm': '610005',
		'ddlhplqd': 'A001',

		'like': '1,2',
		'hate': '4',
		'xxxq': '',
		'gltj': '',
		'pctj': 'S.B',


		'hostname': 'select_pc',
		'query_pc': 'query_pc',
		'status': 'idle',
		'xzhm': '',

	}

	return user_info

class Row_grup(Frame):
	def __init__(self,parent):
		Frame.__init__(self,master=parent)
		self.parent = parent
		self.control_list = []




	def add(self,key,control):
		control.pack(side='left')
		self.control_list.append({'key':key,'control':control})

	def clear(self):
		for control in self.control_list:
			control['control'].pack_forget()

		self.pack_forget()
		self.control_list = []

	def get(self):

		#value_list = []
		value_dict = {}
		for control in self.control_list:
			#输入框
			if isinstance(control.get('control'),Entry):
				key = control.get('key')
				if key is None or key == '':
					counter(ui_log,'ROW_GROUP','GET','ERROR_KEY')
					continue

				value_dict[key] = control['control'].get()
				"""value_list.append({
					'key':control.get('key'),
					'value':control['control'].get()
					})"""

		return value_dict




#验证码显示窗格
class Yzm_group(Frame):
	def __init__(self,parent,queue_to_net,width=600,height=200):
		Frame.__init__(self,master=parent,width=width,height=height)
		self.parent = parent
		
		self.queue_to_net = queue_to_net

		self.view_yzm_img = None
		self.view_yzm_text = None
		self.view_yzm_change = None

		try:
			img_show = Image.open('./config/null.png')
			self.img_null = ImageTk.PhotoImage(img_show)
		except Exception as ex:
			counter(ui_log,'GLOBAL','INIT','IMG','ERROR',ex)
			self.img_null = None


	#换码请求压入队列，任务处理器分发给用户，仅针对select用户
	def __change_code__(self):
		json_temp = {
			'task_type':'yzm',
			'handle_type':'change',
			'user_info':{
				'clsbdh':self.clsbdh,
				'sn':self.sn,
			}
		}



		try:
			
			if not (self.sn == '1' or self.sn == '2') or self.clsbdh == '':
				counter(ui_log,'YZM','CHANGE','ERROR',self.clsbdh,self.sn)
				return 
			else:
				counter(ui_log,'YZM','CHANGE','TRIGGER',self.clsbdh,self.sn)
				try:
					self.queue_to_net.put(json_temp,True,0.5)
				except Exception as ex:
					msg('后台处理忙，稍后重试')
		except Exception as ex:
			pass

	def clear(self):

		self.show_flag = False
		self.pack_forget()

		if self.view_yzm_img:
			#self.view_yzm_img.pack_forget()
			self.view_yzm_img.grid_forget()

		if self.view_yzm_text:
			#self.view_yzm_text.pack_forget()
			self.view_yzm_text.grid_forget()

		if self.view_yzm_change:
			#self.view_yzm_change.pack_forget()
			self.view_yzm_change.grid_forget()



	def show(self,json_data):

		try:

			self.clear()

			self.show_flag = True

			self.button_flag = False

			self.clsbdh = json_data.get('clsbdh','')
			if self.clsbdh == '':
				print_warnning('CLSBDH为空')
				return

			

			#验证码图片
			self.data = json_data.get('data')
			# 验证码
			self.yzm = json_data.get('yzm', '')

			if not self.data:
				self.view_yzm_img = Label(self,image=self.img_null,width=256,height=144)

				if self.yzm != '':
					self.yzm = '显示异常'
			else:
				try:
					self.view_yzm_img = Label(self,image=self.data,width=256,height=144)
				except Exception as ex:
					self.view_yzm_img = Label(self,image=self.img_null,width=256,height=144)
					if self.yzm != '':
						self.yzm = '显示异常'


			if self.yzm == '':
				self.view_yzm_text = Label(self,text='暂无结果',font=('Arial',18))	
			else:
				self.view_yzm_text = Label(self,text=self.yzm,font=('Arial',18))


			#换码按钮
			self.sn = json_data.get('sn','')
			if self.sn == '':
				self.button_text = '未知码号'
			else:
				self.button_text = '码' + self.sn + '换码'

			self.view_yzm_change = Button(self,text=self.button_text,command=lambda:self.__change_code__())


			counter(ui_log,'YZM','SHOW',self.sn,'SUCCESS')

			self.view_yzm_img.grid(row=0,column=0,columnspan=2)
			self.view_yzm_text.grid(row=1,column=0)
			self.view_yzm_change.grid(row=1,column=1)

		except Exception as ex:
			counter(ui_log,'YZM','SHOW',self.sn,'ERROR',ex)

		



#验证码元素视图，生成包括码1和码2的图片，可以进行换码操作
class Yzm_item(Frame):
	#初始化
	def __init__(self,parent,clsbdh,sn,yzm,data,queue_to_net):

		Frame.__init__(self,parent)

		self.clsbdh = clsbdh

		#初始化
		self.yzm1 = None
		self.yzm2 = None
		self.yzm1_img = None
		self.yzm2_img = None

		self.queue_to_net = queue_to_net

		#显示属性
		self.show_flag = False

		#初始化时更新
		self.update(sn=sn,yzm=yzm,data=data)


	#换码请求压入队列，任务处理器分发给用户，仅针对select用户
	def __change_code__(self,sn):
		json_temp = {
			'task_type':'yzm',
			'handle_type':'change',
			'user_info':{
				'clsbdh':self.clsbdh,
				'sn':sn,
			}
		}



		try:
			counter(ui_log,'YZM','CHANGE',self.clsbdh)
			self.queue_to_net.put(json_temp,True,0.5)
		except Exception as ex:
			pass


	#绘图
	def __draw__(self):

		#验证码图片尺寸256x144
		#车辆识别代号
		#
		self.view_clsbdh = Label(self,text=self.clsbdh)
		self.view_clsbdh.grid(row=0,column=0,columnspan=4)

		if self.yzm1:
			#码1，右边
			self.view_yzm1_img = Label(self,image=self.yzm1_img,width=256,height=144)
			self.view_yzm1_img.grid(row=1,column=0,columnspan=2)

			#码1下方
			self.view_yzm1_text = Label(self,text=self.yzm1,font=('Arial',18))
			self.view_yzm1_text.grid(row=2,column=0)

			self.view_yzm1_change = Button(self,text='码1换码',command=lambda:self.__change_code__('1'))
			self.view_yzm1_change.grid(row=2,column=1)
		#为空的时候绘图
		else:
			#码1，右边
			self.view_yzm1_img = Label(self,text='正在获取',width=256,height=144)
			self.view_yzm1_img.grid(row=1,column=0,columnspan=2)

			#码1下方
			self.view_yzm1_text = Label(self,text='获取中',font=('Arial',18))
			self.view_yzm1_text.grid(row=2,column=0)

			self.view_yzm1_change = Button(self,text='码1换码',command=lambda:self.__change_code__('1'))
			self.view_yzm1_change.grid(row=2,column=1)

		#码2绘图
		if self.yzm2:
			self.view_yzm2_img = Label(self,image=self.yzm2_img,text='2',width=256,height=144)
			self.view_yzm2_img.grid(row=1,column=2,columnspan=2)

			self.view_yzm2_text = Label(self,text=self.yzm2,font=('Arial',18))
			self.view_yzm2_text.grid(row=2,column=2)

			self.view_yzm2_change = Button(self,text='码2换码',command=lambda:self.__change_code__('2'))
			self.view_yzm2_change.grid(row=2,column=3)
		else:
			self.view_yzm2_img = Label(self,text='正在获取',width=256,height=144)
			self.view_yzm2_img.grid(row=1,column=2,columnspan=2)


			self.view_yzm2_text = Label(self,text='未获取',font=('Arial',18))
			self.view_yzm2_text.grid(row=2,column=2)

			self.view_yzm2_change = Button(self,text='码2换码',command=lambda:self.__change_code__('2'))
			self.view_yzm2_change.grid(row=2,column=3)


	#返回clsbdh
	def get_id(self):

		return self.clsbdh


	#更新
	def update(self,sn,yzm,data):

		if sn == '1':
			self.yzm1 = yzm
			self.yzm1_img = data
		elif sn == '2':
			self.yzm2 = yzm
			self.yzm2_img = data
		else:
			#参数错误
			pass

		#重新绘图需要显示属性为True时
		if self.show_flag:
			self.__draw__()


	#界面不显示
	def hide(self):
		self.show_flag = False
		self.grid_forget()

	#界面布局
	def show(self,user_row,user_column):

		counter(ui_log,'YZM','SHOW',user_row,user_column)

		self.show_flag = True
		self.grid(row=user_row,column=user_column)
		self.__draw__()




#验证码列表的类，一行为一个用户的两个码
class Yzm_list(Frame):


	def __init__(self,root,queue_to_net):

		Frame.__init__(self,master=root)

		self.parent = root#Tk()

		#用户车架号和验证码等相关信息储存表
		self.user_list = []

		#消息发出队列，传递给任务
		self.queue_to_net = queue_to_net

		self.show_flag = False



	#添加或者更新验证码数据
	def add(self,clsbdh,sn,yzm,data):


		len_user_list = len(self.user_list)
		try:
			row = -1
			for index in range(0,len_user_list):
				if self.user_list[index].get_id() == clsbdh:
					self.user_list[index].update(sn,yzm,data)
					row = index
					break
			else:
				yzm_item = Yzm_item(self.parent,clsbdh,sn,yzm,data,self.queue_to_net)
				self.user_list.append(yzm_item)
				row = len_user_list

			if row < 0:
				return

			#界面需要刷新,刷新指定行即可
			if self.show_flag:
				self.__refresh__(row)


		except Exception as ex:
			counter(ui_log,'YZM_LIST','ADD','ERROR',ex)

	def rmv(self,clsbdh):

		len_user_list = len(self.user_list)
		for index in range(0,len_user_list):
			if self.user_list[index].get_id() == clsbdh:
				del self.user_list[index]
				
				if self.show_flag:
					self.__refresh__()
				

	#添加用户的验证码到界面上
	#user_yzm是用户验证码，包含3个字段，用户clsbdh，码号sn，图片data，验证码内容yzm
	def __refresh__(self,row=None):

		#刷新指定行
		if row:
			#2个用户占一行
			user_count_on_row = 2
			user_row = row/user_count_on_row
			user_column = row%user_count_on_row

			#单个刷新
			self.user_list[row].show(user_row,user_column)

		
		#刷新整个窗口			
		else:
			self.show()

		#父窗口刷新
		#self.parent.update()

	#不显示界面
	def hide(self):

		self.show_flag = False

		self.grid_forget()

		for yzm_user in self.user_list:
			yzm_user.hide()



	#界面显示
	def show(self):

		self.show_flag = True

		self.grid(row=0,column=0)
		

		len_user_list = len(self.user_list)


		for index in range(0,len_user_list):



			#2个用户占一行
			user_count_on_row = 2
			user_row = index/user_count_on_row
			user_column = index%user_count_on_row

			#用户验证码控件组显示
			self.user_list[index].show(user_row,user_column)


#用户简略信息
class UserView(Frame):
	def __init__(self,parent,queue_to_net,width=1000,height=50):
		Frame.__init__(self,master=parent,width=width,height=height)
		self.parent = parent

#用户基本信息			
class UserBaseInfo(Frame):

	def __init__(self,parent,width,height,bg='white'):
		Frame.__init__(self,master=parent,width=width,height=height,bg=bg)

		self.parent = parent

		self.bg = bg

		#基本信息展示的行数
		self.base_rows = []
		self.base_row_count = 4

		self.base_info = [ 
			{'clsbdh':{'title':'识别代号','value':''}},
			{'clxh':{'title':'车辆型号','value':''}},
			{'rdclxz':{'title':'国产进口','value':''}},
			{'tbFdjh':{'title':'发动机号','value':''}},
			{'tbFpbh':{'title':'发票编号','value':''}},



			{'tbSyr':{'title':'姓名名称','value':''}},
			{'ddlZjzl':{'title':'证件种类','value':''}},
			{'bldd':{'title':'办理地点','value':''}},
			{'blrq':{'title':'办理日期','value':''}},
			{'ddlXzhq':{'title':'行政区划','value':''}},


			{'tbZjhm':{'title':'证件号码','value':''}},
			{'tbZzzh':{'title':'暂住证号','value':''}},
			{'tbDz':{'title':'住所地址','value':''}},
			{'txtyzbm':{'title':'邮政编码','value':''}},
			{'ddlhplqd': {'title': '预定地点', 'value': ''}},


			{'like':{'title':'心仪号码','value':''}},
			{'hate':{'title':'排除号码','value':''}},
			{'xxxq':{'title':'不会限行','value':''}},
			{'gltj':{'title':'过滤条件','value':''}},
			{'pctj': {'title': '排除条件', 'value': ''}},
			#{'ddlhplqd':{'title':'预定地点','value':''}},


			{'hostname':{'title':'运行实体','value':''}},
			{'query_pc':{'title':'查询实体','value':''}},
			{'status':{'title':'运行状态','value':''}},
			{'xzhm':{'title':'选中号码','value':''}},

		]

		self.show_flag = False



	#重置界面，并按照当前状态初始化显示组件
	def clear(self):

		self.show_flag = False

		self.pack_forget()		

		
		len_info = len(self.base_info)

		#向上取整，获取行数
		row_index = int(ceil(float(len_info)/float(self.base_row_count)))
		#获取rows当前行数
		len_rows = len(self.base_rows)
		for index in range(len_rows,row_index):
			self.base_rows.append(Row_grup(self))

		for row_item in self.base_rows:
			row_item.clear()

	#窗口显示
	def show(self,user_info):

		

		self.clear()

		self.show_flag = True

		#用户不存在，则为空，一般不会有此场景
		json_null = {}
		self.user_info = user_info
		self.status = user_info.get('status','')

		counter(ui_log,'UserBaseInfo','SHOW',user_info.get('clsbdh',''))

		#根据界面，只有idle态的用户可以编辑
		if self.status == 'idle':
			state = 'normal'
		else:
			state = 'readonly'

		label_titile = {'font':('Times',12),'anchor':'e','width':8,'height':2,'bg':self.bg}
		label_value = {'font':('宋体',12),'width':20,'bg':self.bg,'state':state}

		readonly_list = ['status','xzhm']
		label_value_readonly = {'font':('宋体',12),'width':20,'bg':self.bg,'state':'readonly'}
		#一排显示条数

		#总项目数
		len_info = len(self.base_info)

		for index in range(0,len_info):

			#获取所在的行数
			index_row = int(index/self.base_row_count)
			for key,value in self.base_info[index].items():

				try:
					titile_temp =  Label(self.base_rows[index_row],text=value.get('title',''),**label_titile)

					value = StringVar()
					value.set(self.user_info.get(key,''))

					#只读
					if key in readonly_list:
						value_temp = Entry(self.base_rows[index_row],textvariable=value,**label_value_readonly)
					else:
						value_temp = Entry(self.base_rows[index_row],textvariable=value,**label_value)



					self.base_rows[index_row].add(key,titile_temp)

					
					self.base_rows[index_row].add(key,value_temp)

				#某些数据显示异常，记录日志
				except Exception as ex:
					counter(ui_log,'UserBaseInfo','SHOW','ERROR',key,ex)


		for index in range(0,len(self.base_rows)):
			self.base_rows[index].pack(side='top',fill='x')

	#获取配置信息,主要是输入框修改之后，获取最新的数据
	#还原成Json格式
	def get(self):
		len_info = len(self.base_rows)

		value_dict = {}
		for index in range(0,len_info):
			temp = self.base_rows[index].get()
			value_dict = dict(value_dict,**temp)

		return value_dict


#实体列表
class Hosts(Frame):
	def __init__(self,parent,queue_ui_intra,queue_to_net ,width,height):
		Frame.__init__(self,master=parent,width=width,height=height)

		self.queue_ui_intra = queue_ui_intra
		self.queue_to_net = queue_to_net

		self.hosts = {}

		self.show_flag = False

		self.title = {
			'hostname':{'value':'主机名','control':None},
			'status':{'value':'在线状态','control':None},
			'cxtj':{'value':'查询条件','control':None},
			#'zxjg':{'value':'最新结果','conrol':None},
			'row':Row_grup(self)}

		self.column_key  = ['hostname','status','cxtj']




	def add(self,json_data):
		hostname = json_data.get('hostname','')

		#不是查询电脑

		if hostname == '':
			counter(ui_log,'HOSTS','ADD','NULL_HOSTNAME')
			return

		#初始化
		if not hostname in self.hosts:
			self.hosts[hostname] = {
			'hostname':{'value':'','control':None},
			'status':{'value':'','control':None},
			'cxtj':{'value':'','control':None},
			#'zxjg':{'value':'','conrol':None},
			'row':Row_grup(self),
		}

		#更新
		for key,value in json_data.items():
			self.hosts[hostname][key] = {'value':value}

		if self.show_flag:
			self.show()

	def rmv(self,hostname):
		#hostname = json_data.get('hostname','')
		if hostname == '' or hostname is None:
			counter(ui_log,'HOSTS','ADD','NULL_HOSTNAME')
			return

		if hostname in self.hosts:
			self.hosts[hostname]['row'].clear()

			if self.show_flag:
				self.shwo()
		else:
			counter(ui_log,'HOSTS','RMV','NOT_FOUND')



	def clear(self):

		self.show_flag = False

		self.pack_forget()

		#标题行清空
		if self.title['row']:
			self.title['row'].clear()
		else:
			self.title['row'] = Row_grup(self)

		#内容清空
		for key,value in self.hosts.items():

			if 'row' in self.hosts[key]:
				self.hosts[key]['row'].clear()
			else:
				self.hosts[key]['row'] = Row_grup(self)


	def show(self,hosts=None):

		self.clear()

		self.show_flag = True

		label_title = {'font':('Times',10),'anchor':'w','width':15,'height':1,'bd':5,'fg':'blue'}
		label_temp = {'font':('宋体',10),'width':15,'state':'readonly'}

		count_line = 0
		#title初始化
		for name in self.column_key:

			temp = Label(self.title['row'],text=self.title[name].get('value',''),**label_title)
			self.title['row'].add(name,temp)
			count_line += 1
		else:			
			self.title['row'].pack(side='top',fill='x')

		if not hosts:
			return

		self.hosts = hosts

		for key,value in self.hosts.items():

			self.hosts[key]['row'] = Row_grup(self)
			for name in self.column_key:

				attr = self.hosts[key].get(name)
				if attr is None:
					continue

				value = StringVar()
				value.set(attr.get('value',''))

				temp = Entry(self.hosts[key]['row'],textvariable=value,**label_temp)
				self.hosts[key]['row'].add(name,temp)
				count_line += 1
			else:
				
				self.hosts[key]['row'].pack(side='top',fill='x')

		counter(ui_log,'HOSTS','SHOW','SUCCESS','LINES',count_line)

class Select_log(Frame):
	def __init__(self,parent,queue_ui_intra,queue_to_net,width,height):

		Frame.__init__(self, master=parent, width=width, height=height)

		self.queue_ui_intra = queue_ui_intra
		self.queue_to_net = queue_to_net
		self.width = width

		self.scrollbar = Scrollbar(self)
		self.user_log = {}
		self.list_box = Listbox(self, yscrollcommand=self.scrollbar.set, width=45)

	def add(self,clsbdh,text):


		if clsbdh not in self.user_log.keys():

			self.user_log[clsbdh] = Listbox(self,yscrollcommand = self.scrollbar.set,width=45)

		self.user_log[clsbdh].insert(0,str(text))

		counter(clsbdh + ' log',str(text))

		if '约号成功' in text:
			beep(1,2000,3000)
			msg(text)
		elif  '约号失败' in text:
			beep(2,2000,500)


	def clear(self):
		self.pack_forget()
		self.scrollbar.pack_forget()
		self.list_box.pack_forget()

	def show(self,log_list):
		self.clear()

		self.list_box = Listbox(self,yscrollcommand = self.scrollbar.set,width=45)
		for text in log_list:
			self.list_box.insert(0,str(text))

		self.scrollbar.pack(side='right', fill='y')
		self.list_box.pack(side='right',fill='x')







#应急操作区域
class Emergency(Frame):
	def __init__(self,parent,queue_ui_intra, queue_to_net,width,height):
		Frame.__init__(self,master=parent,width=width,height=height)

		self.queue_ui_intra = queue_ui_intra
		self.queue_to_net = queue_to_net
		self.width = width

		self.hosts = {}

		self.show_flag = False

	def show(self):
		pass

	def clear(self):
		pass


class Users(Frame):


	def __init__(self,parent,queue_ui_intra, queue_to_net,width=1100,height=650):


		Frame.__init__(self,master=parent,width=width,height=height)

		self.width = width
		self.height = height
		self.parent = parent
		self.queue_ui_intra = queue_ui_intra	
		self.queue_to_net = queue_to_net

		self.hosts = {}

		self.users = {}
		self.user_info = None

		self.show_flag = False		
		self.emergency_status = False

		self.clsbdh = None

		self.__init_win__()

		# 获取在线节点，会更新host_frame
		json_task = {
			'task_type': 'login',
			'handle_type': 'query',
			'user_info': {}
		}

		try:
			self.queue_to_net.put(json_task, True, 0.5)
		except Exception as ex:
			msg('后台处理忙，稍后重试')

		#图片
		try:
			img_show = Image.open('./config/null.png')
			self.img_null = ImageTk.PhotoImage(img_show)
		except Exception as ex:
			counter(ui_log,'GLOBAL','INIT','IMG','ERROR',ex)
			self.img_null = None

	def __init_win__(self):

		width = self.width
		height = self.height



		self.mode = 'place'

		#上部窗口
		self.top_frame = Frame(master=self,width=width,height=200)
		#下部窗口
		# 用户基本信息Frame
		self.base_info_frame = UserBaseInfo(parent=self, width=width, height=400)
		# 左边
		self.top_left_frame = Frame(master=self.top_frame, width=width * 2 / 3, height=200)
		#验证码窗口
		self.top_right_frame = Frame(master=self.top_frame, width=width / 3, height=200)

		#host和日志窗口
		self.host_log_frame = Frame(master=self.top_left_frame, width=width * 2 / 3, height=180)
		self.host_frame = Hosts(parent=self.host_log_frame, queue_ui_intra=self.queue_ui_intra, \
								queue_to_net=self.queue_to_net, width=width * 1 / 3, height=180)
		self.select_log = Select_log(parent=self.host_log_frame, queue_ui_intra=self.queue_ui_intra, \
									 queue_to_net=self.queue_to_net, width=width * 1 / 3, height=180)

		#按钮窗口
		self.control_buttoen_frame = Frame(master=self.top_left_frame,width=width*2/3,height=20)
		font_button = {'font':('宋体',15),'width':10,'height':4}
		
		#两个大按钮
		self.save = Button(self.top_left_frame,text='保存',command=lambda:self.__click__('update'),**font_button)


		self.start = Button(self.top_left_frame,text='开始',command=lambda:self.__click__('start'),bg='green',**font_button)

		self.stop = Button(self.top_left_frame,text='停止',command=lambda:self.__click__('stop'),bg='yellow',**font_button)

		#self.delete = Button(self.top_left_frame,text='删除',command=lambda:self.__click__('delete'),**font_button)
		self.order = Button(self.top_left_frame, text='约号', command=lambda: self.__click__('order'), **font_button)

		self.relogin = Button(self.top_left_frame,text='重登录',command=lambda:self.__click__('relogin'),**font_button)
		font_emergency = {'font':('宋体',15),'width':8,'bg':'red'}
		value = StringVar()
		value.set('紧急模式')
		#self.emergency = Entry(self.top_left_frame,textvariable=value,**font_emergency)
		self.emergency = Button(self.top_left_frame, text='换IP', command=lambda:self.__click__('ip'),**font_button)

		#YZM页面
		self.yzm1_frame = Yzm_group(parent=self.top_right_frame,queue_to_net=self.queue_to_net,width=width/3,height=100)
		self.yzm2_frame = Yzm_group(parent=self.top_right_frame,queue_to_net=self.queue_to_net,width=width/3,height=100)





	#当前用户信息修改保存事件处理
	def __click__(self,handle):



		clsbdh = self.user_info.get('clsbdh')

		if clsbdh:

			json_temp = None
			#约号用户重新登录
			if handle == 'relogin':
				counter(ui_log,'USERS','CLICK','RELOGIN','TRIGGER')

				json_temp = {
					'task_type':'select',
					'handle_type':'relogin',
					'user_info':{
						'clsbdh':clsbdh,
					}
				}


			elif handle == 'order':
				counter(ui_log, 'USERS', 'CLICK', 'ORDER', 'TRIGGER')

				json_temp = {
					'task_type': 'select',
					'handle_type': 'order',
					'user_info': {
						'clsbdh': clsbdh,
					}
				}
			elif handle == 'ip':
				counter(ui_log, 'USERS', 'CLICK', 'IP', 'TRIGGER')

				json_temp = {
					'task_type': 'select',
					'handle_type': 'ip',
					'hostname':self.user_info.get('hostname',''),
					'user_info': {
						'clsbdh': clsbdh,
					}
				}


			try:
				if json_temp:
					self.queue_to_net.put(json_temp, True, 0.5)
					return
				else:
					pass
			except Exception as ex:
				msg('后台处理忙，稍后重试')
				return



			#待完善
			if handle == 'emergency':
				counter(ui_log,'USERS','CLICK','EMERGENCY','TRIGGER')
				self.emergency_status = True
				return

			self.user_info = self.base_info_frame.get()


			if handle == 'delete' and self.user_info.get('status') != 'idle':
				msg('只有空闲态的用户才能被直接删除')
				counter(ui_log,'USERS','CLICK','FAIL','DELETE')
				return
			elif handle == 'update' and self.user_info.get('status') != 'idle':
				msg('只有空闲态的用户才能被编辑')
				counter(ui_log,'USERS','CLICK','FAIL','UPDATE')
				return
			elif handle == 'start' and self.user_info.get('status') != 'idle':
				msg('只有空闲态的用户才能被启动')
				counter(ui_log,'USERS','CLICK','FAIL','START')
				return


			json_data = {
					'task_type':'user',
					'handle_type':handle,
					'user_info':self.user_info
			}			

			try:
				self.queue_to_net.put(json_data,True,1)
			except Exception as ex:
				msg('后台处理忙，稍后重试')
				counter(ui_log, 'USERS', 'CLICK', 'FAIL', 'QUEUE_FULL')



	def __clear_host_log__(self):



		self.host_frame.clear()
		self.select_log.clear()
		self.host_frame.pack_forget()
		self.select_log.pack_forget()

		self.host_log_frame.pack_forget()

	def __show_host_log__(self):

		self.host_log_frame.pack(side='top', fill='x')

		self.host_frame.pack(side='left', fill='y')
		self.select_log.pack(sid='right', fill='y')


	def __clear_button__(self):



		self.save.pack_forget()
		self.start.pack_forget()
		self.stop.pack_forget()
		#self.delete.pack_forget()
		self.order.pack_forget()
		self.relogin.pack_forget()
		self.emergency.pack_forget()

		self.control_buttoen_frame.pack_forget()

	def __show_button__(self):
		self.control_buttoen_frame.pack(side='top', fill='x')

		self.start.pack(side='left', padx=4)
		self.stop.pack(side='left', padx=4)
		self.save.pack(side='left', padx=4)
		#self.delete.pack(side='left', padx=4)
		self.order.pack(side='left', padx=4)
		self.relogin.pack(side='left', padx=4)
		self.emergency.pack(side='left', padx=10)

	def __clear_yzm__(self):

		self.yzm1_frame.clear()
		self.yzm2_frame.clear()
		self.yzm1_frame.pack_forget()
		self.yzm2_frame.pack_forget()

		# 验证码整体框架
		self.top_right_frame.pack_forget()

	def __show_yzm__(self):

		self.top_right_frame.pack(side='right', fill='y')
		self.yzm1_frame.pack(side='top',fill='x')
		self.yzm2_frame.pack(side='top', fill='x')




	def __clear_top__(self):

		self.__clear_host_log__()
		# 按钮
		self.__clear_button__()

		self.__clear_yzm__()

		# 左边清除
		self.top_left_frame.pack_forget()

		# 上部客户端和日志
		self.top_frame.pack_forget()





	def __show_top__(self):
		# 上部客户端和日志
		self.top_frame.pack(side='top', fill='x')
		# 按钮控制
		self.top_left_frame.pack(side='left', fill='y')

		self.__show_host_log__()

		# 按钮
		self.__show_button__()

		# 验证码整体框架
		self.__show_yzm__()


	#重置界面，并按照当前状态初始化显示组件
	def clear(self):
		self.show_flag = False

		self.pack_forget()

		#上部信息清空
		self.__clear_top__()

		# 基本信息页面清空
		self.base_info_frame.clear()
		self.base_info_frame.pack_forget()

	#数据加载
	def __load__(self,clsbdh=None):

		self.__init_win__()

		# clsbdh不为空
		if clsbdh is not None:
			self.clsbdh = clsbdh

		counter(ui_log, 'USERS', 'SHOW', self.clsbdh, clsbdh)

		if self.clsbdh is None:
			return False

			# 创建一个新用户显示
		# 当前用户刷新，如果有当前用户
		elif self.clsbdh == 'create':
			self.user_info = new_user()
			self.clsbdh = self.user_info.get('clsbdh')
			self.users[self.clsbdh] = {}
			self.users[self.clsbdh]['user_info'] = self.user_info
			self.users[self.clsbdh]['log'] = []

		else:
			# 用户不存在，则为空，一般不会有此场景
			json_null = {}
			self.user_info = self.users[self.clsbdh].get('user_info', json_null)


		# 数据加载
		try:
			self.host_frame.show(self.hosts)
			self.select_log.show(self.users[self.clsbdh].get('log')[-50:])
			counter(ui_log, 'USERS', 'SHOW', 'HOSTS', 'SUCCESS')
		except Exception as ex:
			counter(ui_log, 'USERS', 'SHOW', 'HOSTS', 'ERROR', ex)

		# 验证码数据加载
		try:

			json_yzm1 = {
				'clsbdh': self.clsbdh,
				'yzm': self.users[self.clsbdh].get('yzm1', ''),
				'sn': '1',
				'data': self.users[self.clsbdh].get('yzm1_img'),
			}

			#print_debug('显示验证码1')
			self.yzm1_frame.show(json_yzm1)

			json_yzm2 = {
				'clsbdh': self.clsbdh,
				'yzm': self.users[self.clsbdh].get('yzm2', ''),
				'sn': '2',
				'data': self.users[self.clsbdh].get('yzm2_img'),
			}
			#print_debug('显示验证码2')
			self.yzm2_frame.show(json_yzm2)

		except Exception as ex:
			counter(ui_log, 'USERS', 'SHOW', 'YZM', 'ERROR', ex)
			print_debug('验证码显示异常',ex)

		self.xzhm = self.user_info.get('xzhm','')
		if self.xzhm != '':
			#用户基本信息Frame
			self.base_info_frame = UserBaseInfo(parent=self,width=self.width,height=self.height,bg='green')
		else:
			#用户基本信息Frame
			self.base_info_frame = UserBaseInfo(parent=self,width=self.width,height=400)

		# 用户基本信息
		self.base_info_frame.show(self.user_info)
		return True


	#窗口显示
	def show(self,clsbdh=None):

		self.clear()

		self.show_flag = True

		#数据加载失败
		if not self.__load__(clsbdh):
			counter(ui_log, 'USERS', 'SHOW', 'LOAD', 'FAIL')
			return


		self.pack(fill='both')

		self.__show_top__()
		# 已经成功的用户，还是继续显示其他界面:
		self.base_info_frame.pack(side='bottom', fill='x')



	def add_host(self,json_data):
		#self.hosts_info =
		try:
			hostname = json_data.get('hostname','')
			if hostname != '':
				# 初始化
				if not hostname in self.hosts:
					self.hosts[hostname] = {
						'hostname': {'value': '', 'control': None},
						'status': {'value': '', 'control': None},
						'cxtj': {'value': '', 'control': None},
						# 'zxjg':{'value':'','conrol':None},
						#'row': Row_grup(self),
					}

				# 更新
				for key, value in json_data.items():
					self.hosts[hostname][key] = {'value': value}

				#self.host_frame.add(json_data)
				counter(ui_log,'USER','ADD_HOST',hostname)
		except Exception as ex:
			counter(ui_log,'USER','ADD_HOST','ERROR',ex)

	#批量添加完了之后再刷新
	def show_host(self):
		try:
			if not self.show_flag:
				return
			else:
				self.show()
		except Exception as ex:
			counter(ui_log, 'USERS', 'SHOW_HOST', 'ERROR', ex)


	#数据刷新
	def add(self,user_info):

		clsbdh = user_info.get('clsbdh','')

		print_debug('更新用户相关信息',clsbdh)
		#clsbdh必须包含
		if clsbdh == '':
			counter(ui_log,'USER','INIT','NULL_CLSBDH')
			print_warnning('CLSBDH为空，不能更新数据')
			return


		#新增的用户初始化，更新的用户不用进入分支
		if not clsbdh in  self.users:
			self.users[clsbdh] = {}
			self.users[clsbdh]['user_info'] = {}
			self.users[clsbdh]['log'] = []


		#按需部分更新数据
		for key in user_info.keys():

			try:
				#其他信息
				if key in ('yzm1_img','yzm2_img','yzm1','yzm2'):
					self.users[clsbdh][key] = user_info[key]

				elif key == 'text':
					self.users[clsbdh]['log'].append(user_info['text'])
					text = user_info['text']
					if '约号成功' in text:
						beep(1, 2000, 3000)
						msg(text)
					elif '约号失败' in text:
						beep(2, 2000, 500)

				#基本信息
				else:
					self.users[clsbdh]['user_info'][key] = user_info[key]
			except Exception as ex:
				print_warnning('更新用户数据异常',ex)


		if not self.users[clsbdh].get('yzm1_img'):
			self.users[clsbdh]['yzm1_img'] = self.img_null

		if not self.users[clsbdh].get('yzm2_img'):
			self.users[clsbdh]['yzm2_img'] = self.img_null


		#如果更新的是当前用户的数据，刷新窗口
		if self.show_flag and clsbdh == self.clsbdh:
			#更新窗口
			self.show()

	#删除用户
	def rmv(self,clsbdh):

		counter(ui_log,'USERS','RMV',clsbdh)
		if clsbdh in self.users:
			del self.users[clsbdh]

		#如果更新的是当前用户的数据，刷新窗口
		if self.show_flag:
			self.show()

		
	#换码请求压入队列，任务处理器分发给用户，仅针对select用户
	def __change_code__(self,sn):
		json_temp = {
			'task_type':'yzm',
			'handle_type':'change',
			'user_info':{
				'clsbdh':self.clsbdh,
				'sn':sn,
			}
		}



		try:
			counter(ui_log,'YZM','CHANGE',self.clsbdh)
			self.queue_to_net.put(json_temp,True,0.5)
		except Exception as ex:
			msg('后台处理忙，稍后重试')





status_dict = {
	'running':'运行',
	'idle':'空闲',
	'success':'成功',

}

	


#左边导航树布局，验证码监控以及运行用户展示
class Tree(Frame):

	def __init__(self,root,queue_ui_intra,width=100,height=650):

		Frame.__init__(self,master=root,width=width, height=height,padx=2,pady=5,bg='white')

		self.parent = root

		self.tree_frame = Frame(master=self,width=width,height=height)

		self.queue_ui_intra = queue_ui_intra

		#保存关键字
		self.keys = []

		yzm_all = {
			'key':'yzm_all',
			'name':'验证码监控',
			'status':'all',
			'control':None,
		}

		self.keys.append(yzm_all)


		self.filter_type = 'all'
		"""
		clsbdh:{
			name:联系人名单
			index:时间
		}	
		"""

		self.__refresh__()


	def set_filter(self,filter_type):

		counter(ui_log,'TREE','FILTER','SET',filter_type)

		if filter_type == '' or filter_type is None:
			return

		self.filter_type = filter_type

		self.__refresh__()




	#刷新界面
	def __refresh__(self):

		self.tree_frame.pack_forget()

		self.tree_frame.pack(fill='both')

		for index in range(0,len(self.keys)):

			try:
				if self.keys[index].get('control'):
					self.keys[index]['control'].pack_forget()

					name = self.keys[index].get('name','')
					if name != '验证码监控':
						name += '[' + status_dict.get(self.keys[index].get('status'),'') + ']'

					self.keys[index]['control']['text'] = name

				#重新赋值刷新
				else:
					name = self.keys[index].get('name','')
					if name != '验证码监控':
						name += '[' + status_dict.get(self.keys[index].get('status'),'') + ']'

					self.keys[index]['control'] = Button(self.tree_frame,text=name,\
						command=lambda:self.__select__(index),width=20,height=1)

				counter(ui_log,'TREE','REFRESH',self.keys[index].get('key'),name)

				#显示
				if self.keys[index].get('status') == 'all' or self.filter_type == 'all' or \
				  self.keys[index].get('status') == self.filter_type:
					self.keys[index]['control'].pack(side='top')
			except Exception as ex:
				counter(ui_log,'TREE','REFRESH','ERROR',index,ex)

	
				


	#选择了导航树元素，右边的窗体跟着刷新
	def __select__(self,index):
		try:
			key = self.keys[index].get('key')
			json_data = {
				'task_type':'tree',
				'handle_type':'select',
				'user_info':{'key':key},
			}



			#点击生成页面刷新事件
			self.queue_ui_intra.put(json_data,True,3)
			self.parent.event_generate('<<main_refresh>>',when='tail')

			counter(ui_log,'TREE','SELECT',key)

		except Exception as ex:
			msg('选择导航树异常')
			counter(ui_log,'TREE','SELECT','ERROR',ex)

	#添加元素,并绘图
	def add(self,key,name,status=''):

		counter(ui_log,'TREE','ADD',key,name)
		for index in range(0,len(self.keys)):
			#更新
			if self.keys[index].get('key') == key:

				if name != '' and name is not None:
					self.keys[index]['name'] = name

				self.keys[index]['status'] = status

				counter(ui_log,'TREE','UPDATE',key,name)

				break
		#新增
		else:
			self.keys.append({
				'key':key,
				'name':name,
				'status':status,
			})
			counter(ui_log,'TREE','NEW',key,name)


		self.__refresh__()


	#删除元素，并绘图
	def rmv(self,key):
		for index in range(0,len(self.keys)):
			#更新
			if self.keys[index].get('key') == key:
				self.keys[index]['control'].pack_forget()
				del self.keys[index]
				self.__refresh__()
				return

				


#最右边扩展操作
class Extend(Frame):

	def __init__(self,root,queue_ui_intra,queue_to_net, width=100,height=650):

		Frame.__init__(self,master=root,width=width, height=height,padx=2,pady=5,bg='white')

		self.parent = root

		self.queue_ui_intra = queue_ui_intra
		self.queue_to_net = queue_to_net

		#保存关键字
		self.keys = {}
		"""
		clsbdh:{
			name:联系人名单
			index:时间
		}	
		"""


	#选择了导航树元素，右边的窗体跟着刷新
	def __select__(self,key):

		try:
			counter(ui_log, 'EXTEND', 'SELECT', key)

			json_data = {
				'task_type': 'extend',
				'handle_type': key,
				'user_info': {'key':key},
			}


			#点击生成页面刷新事件
			self.queue_ui_intra.put(json_data,True,3)
			self.parent.event_generate('<<main_refresh>>',when='tail')

			#创建新用户，不用请求服务器
			if key == 'create':
				return

			json_server = deepcopy(json_data)
			json_server['task_type'] = 'user'

			try:
				#后台生成服务器请求
				self.queue_to_net.put(json_server,True,0.5)
			except Exception as ex:
				msg('后台处理忙，稍后重试')

		except Exception as ex:
			counter(ui_log,'EXTEND','SELECT',key,'ERROR',ex)
			msg('操作失败，请等待一会重试')

	#添加元素,并绘图
	def add(self,key,name):
		if key in  self.keys:
			return

		else:

			label_temp = Button(self,text=name,command=lambda:self.__select__(key),width=20,height=2)
			#label_temp.grid(row=len(self.keys),column=0,sticky='n')
			label_temp.pack(side=TOP)

			self.keys[key] = {
				'name':name,
				'label':label_temp,
				'time':time.time(),
			}

			#self.update()


	#删除元素，并绘图
	def rmv(self,key):
		if not  key in self.keys:
			return
		else:
			pass



class Contain(Frame):
	def __init__(self,root,queue_ui_intra,queue_to_net,width=1000,height=700):
		Frame.__init__(self,master=root,width=width,height=height,padx=2,pady=5,bg='white')

		self.parent = root

		self.queue_ui_intra = queue_ui_intra
		self.queue_to_net = queue_to_net

		#验证码界面
		self.yzm_list = Yzm_list(self,self.queue_to_net)

		#用户个人信息页面
		self.users = Users(self, queue_ui_intra = self.queue_ui_intra,queue_to_net= self.queue_to_net, \
			width=width,height=height)


		try:
			img_show = Image.open('./config/null.png')
			self.img_null = ImageTk.PhotoImage(img_show)
		except Exception as ex:
			counter(ui_log,'GLOBAL','INIT','IMG','ERROR',ex)
			self.img_null = None


	#切换窗体内容
	def switch(self,key):

		counter(ui_log,'CONTAINER','SWITCH',key)
		#切换到验证码监控窗口
		if key == 'yzm_all':
			self.users.clear()
			self.yzm_list.show()

		#切换到用户窗口，如果用户存在
		else:
			self.yzm_list.hide()
			self.users.show(key)
		

	#根据任务类型刷新
	def refresh(self,json_data):

		try:
			task_type = json_data.get('task_type')
			handle_type = json_data.get('handle_type')


			#验证码刷新
			if task_type == 'yzm':

				"""if json_data[0:20] == b'0'*20:
					json_head = loads(json_data[20:1024].decode())
				else:
					return"""

				if  handle_type != 'refresh':
					counter(ui_log,'CONTAINER','REFRESH','YZM','TYPE_ERROR',handle_type)
					return
				try:
					#body_data = json_data[1024:]
					clsbdh = json_data['user_info']['data'][0:17].decode()
					sn = json_data['user_info']['data'][17:18].decode()
					yzm = json_data['user_info']['yzm']
					data =json_data['user_info']['data'][18:]
				except Exception as  ex:
					counter(ui_log, 'CONTAIN', 'REFRESH', 'YZM', 'LOAD_ERROR', ex)
					data = self.img_null

				try:
					"""if data.startswith('./'):
						img_data = data
					else:"""
					img_data = io.BytesIO(data)


					img_show = Image.open(img_data)
					data = ImageTk.PhotoImage(img_show)

				#图片加载异常
				except Exception as ex:
					counter(ui_log,'CONTAIN','REFRESH','YZM','ERROR',ex)
					data = self.img_null


				#添加数据，自动判断界面是否需要刷新
				#self.yzm_list.add(clsbdh=clsbdh,sn=sn,yzm=yzm,data=data)

				user_info = {
					'clsbdh':clsbdh,
				}

				if sn == '1':
					user_info['yzm1'] = yzm
					user_info['yzm1_img'] = data
				else:
					user_info['yzm2'] = yzm
					user_info['yzm2_img'] = data

				#验证码相关信息更新到用户数据中
				self.users.add(user_info)

			elif task_type == 'host':

				if handle_type == 'respnse':
					for item in json_data['user_info']:
						self.users.add_host(json_data['user_info'][item])
					else:
						pass
						#self.users.show_host()
				elif handle_type == 'update':
					self.users.add_host(json_data['user_info'])
					#self.users.show_host()

			elif task_type == 'log':
				if handle_type == 'report':
					#print_debug('接收到日志', json_data['user_info'])
					self.users.add(json_data['user_info'])
				else:
					counter(ui_log,'CONAINER','FAIL','UNKNOWN_TYPE',task_type,handle_type)


			#约号用户，从服务器创建的任务
			elif task_type == 'select':
				if json_data.get('handle_type') == 'start':

					self.users.add(json_data.get('user_info'))

				#基本上是选号成功
				elif handle_type == 'stop':

					counter(ui_log,'CONAINER','SUCCESS',json_data['user_info'].get('clsbdh',''),json_data['user_info'].get('xzhm',''))
					if json_data['user_info'].get('xzhm','') != '':
						json_temp = {
							'clsbdh':json_data['user_info'].get('clsbdh',''),
							'status':'success',
							'xzhm':json_data['user_info'].get('xzhm',''),
						}
						self.users.add(json_temp)
				else:
					pass

			elif task_type == 'user':

				#用户列表更新
				if json_data.get('handle_type') == 'list':
					user_list = json_data['user_info']
					for user_info in user_list:
						self.users.add(user_info)

				#单个用户更新
				elif json_data.get('handle_type') == 'update':
					user_info = json_data['user_info']
					self.users.add(user_info)

				elif json_data.get('handle_type') == 'delete':
					user_info = json_data['user_info']
					self.users.rmv(user_info.get('clsbdh'))

				else:
					pass

			elif task_type == 'login':


				if handle_type == 'online':
					json_data['user_info']['status'] = '在线'

				elif handle_type == 'offline':
					json_data['user_info']['status'] = '离线'

				elif handle_type == 'list':

					for key,value in json_data['user_info'].items():

						json_temp = value

						if json_temp['status'] =='online':
							json_temp['status'] = '在线'
						else:
							json_temp['status'] = '离线'

						self.users.add_host(json_temp)

					
					else:
						pass
					return


				else:
					json_data['user_info']['status'] = '离线'

				self.users.add_host(json_data['user_info'])

			else:
				pass
		except Exception as ex:
			counter(ui_log,'CONAINER','REFRESH','ERROR',ex)



#主窗体
class Main_win():

	#初始化，任务队列传递进来
	def __init__(self,root,queue_ui_intra,queue_to_net):

		#root = Tk()
		self.parent = root		

		self.parent.wm_title("约号控制")

		#窗口大小固定
		#self.parent.resizable(False,False)


		#用户列表初始化
		self.user_list = []


		#消息发出队列，传递给任务
		self.queue_to_net = queue_to_net
		#传入队列，用于界面刷新和用户信息更新
		self.queue_ui_intra = queue_ui_intra


		#窗体初始化
		self.__init_win__()

		#各种响应事件注册
		self.__register_event__()

		#后台请求数据
		self.__init_data__()




	#窗体各个部件初始化
	def __init_win__(self):



		self.parent.geometry('1200x650+10+10')

		#各个部件触发的事件汇总都主窗口队列处理


		#左边导航树
		self.tree = Tree(self.parent,self.queue_ui_intra,width=100,height=650)
		self.tree.pack(side='left',fill='y')

		



		#竖条间隔
		inter_v = Frame(self.parent,width=5,bg='green')
		inter_v.pack(side='left',fill='y')

		#右边内容页面
		self.contain = Contain(self.parent,self.queue_ui_intra,self.queue_to_net,width=960,height=650)
		#self.contain.grid(row=0,column=1)
		self.contain.pack(side='left',fill='y')

		#self.contain.switch('本地验证码监控')

		self.extend = Extend(self.parent,self.queue_ui_intra,self.queue_to_net,width=140,height=650)


		self.extend.add(key='create',name='新建用户')
		self.extend.add(key='idle',name='待约用户')
		self.extend.add(key='running',name='运行用户')
		self.extend.add(key='success',name='成功用户')
		self.extend.add(key='all',name='所有用户')


		self.extend.pack(side='left',fill='y')
		

		self.parent.update()

	#初始化数据和网络请求
	def __init_data__(self):
		#请求正在运行的用户数据


		# 刷新hosts
		json_host_request = {
			'task_type': 'host',
			'handle_type': 'query',
			'user_info': {}
		}

		try:
			self.queue_to_net.put(json_host_request, True, 0.5)
		except Exception as ex:
			print_warnning('消息发送失败')
		json_user_request = {
			'task_type': 'user',
			'handle_type': 'running',
			'user_info': {'key': 'running'},
		}
		try:
			self.queue_to_net.put(json_user_request, True, 0.5)
		except Exception as ex:
			pass


	#定制事件
	def __register_event__(self):

		self.event_running = False

		def __main_refresh__():
			try:
				#一般事件是已经触发，可以直接获取
				json_data = self.queue_ui_intra.get(True,3)

				#如果正在运行，等待
				if self.event_running:
					time.sleep(0.1)

				self.event_running = True


				task_type = json_data.get('task_type') 
				handle_type = json_data.get('handle_type')


				#导航树操作
				if task_type == 'tree':
					if json_data.get('handle_type') == 'select':
						key =  json_data['user_info'].get('key','')
						#if key == '验证码监控':
						counter(ui_log,'EVENT','SELECT',key)

						self.contain.switch(key)

						self.parent.update()
				#右边扩展功能
				elif task_type == 'extend':
					counter(ui_log, 'EVENT', 'extend')

					if handle_type == 'create':
						self.contain.switch(handle_type)

						#刷新hosts
						json_host_request = {
							'task_type':'host',
							'handle_type':'query',
							'user_info':{}
						}

						try:
							self.queue_to_net.put(json_host_request,True,0.5)
						except Exception as ex:
							msg('后台处理忙，稍后重试')
					else:
						self.tree.set_filter(handle_type)
					self.parent.update()

				elif task_type == 'host':
					try:
						self.contain.refresh(json_data)

						self.parent.update()
					except Exception as ex:
						counter(ui_log,'EVENT','HOST','REFRESH_ERROR',ex)

				#验证码更新，透传给contain
				elif task_type == 'yzm':

					#车辆识别代号添加
					if not 'user_info' in json_data or not 'data' in json_data['user_info']:
						counter(ui_log,'EVENT','YZM','ERROR_DATA')
						self.event_running = False
						return


					#页面给更新
					self.contain.refresh(json_data)

					self.parent.update()

					counter(ui_log,'EVENT','YZM','SUCCESS')


				elif task_type == 'user':
					#列表形式返回的用户信息
					if json_data.get('handle_type') == 'list':
						user_list = json_data['user_info']
						for user_info in user_list:
							self.tree.add(key=user_info.get('clsbdh'),name=user_info.get('tbSyr'),status=user_info.get('status'))
						
						self.contain.refresh(json_data)

						self.parent.update()
					elif json_data.get('handle_type') == 'update':
						#更新
						user_info = json_data.get('user_info')
						if user_info is None or user_info == '':
							counter(ui_log,'MAIN','EVENT','USER','UPDATE','FAIL','NULL_INFO')
							self.event_running = False
							return

						self.tree.add(key=user_info.get('clsbdh'),name=user_info.get('tbSyr'),status=user_info.get('status'))

						self.contain.refresh(json_data)

						counter(ui_log,'MAIN','EVENT','USER','UPDATE','SUCCESS',user_info.get('clsbdh'))


					elif json_data.get('handle_type') == 'delete':
						user_info = json_data.get('user_info')
						if user_info is None or user_info == '':
							counter(ui_log,'MAIN','EVENT','USER','DELETE','FAIL','NULL_INFO')
							self.event_running = False
							return

						self.tree.rmv(key=user_info.get('clsbdh',''))
						self.contain.refresh(json_data)


					else:
						pass

				elif task_type == 'login':
					#上下线状态更新
					if handle_type == 'online' or handle_type == 'offline' or \
						handle_type == 'list':

						counter(ui_log,'MAIN_EVENT','LOGIN','REFRESH',handle_type,json_data)
						self.contain.refresh(json_data)

						self.parent.update()

						pass

				elif task_type == 'select':

					counter(ui_log,'MAIN_EVENT','SELECT',handle_type,json_data)
					self.contain.refresh(json_data)
					self.parent.update()
				else:
					pass

			except Exception as ex:
				counter(ui_log,'MAIN','EVENT','ERROR',ex,json_data)
			finally:
				self.event_running = False


		self.parent.bind('<<main_refresh>>',lambda e:__main_refresh__())

		def __net_data_recv__():
			try:
				# 一般事件是已经触发，可以直接获取
				data_from_net = self.queue_ui_intra.get(True, 3)

				if self.event_running:
					time.sleep(0.1)

				self.event_running = True

				try:
					if data_from_net[0:20] == b'0' * 20:

						json_data = {
							'task_type': 'yzm',
							'handle_type': 'refresh',
							'user_info': {
								'yzm': data_from_net[20:40].decode('gbk')[0:4],
								# 'data':data.decode('utf-8'),
							}
						}
						print_debug('接收到验证码',data_from_net[20:40].decode('gbk')[0:4])

						json_data['user_info']['data'] = data_from_net[40:]
					else:
						json_data = loads(data_from_net.decode())
				except Exception as ex:
					print_error('解析网络数据异常',ex)
					self.event_running = True
					return

				task_type = json_data.get('task_type')
				handle_type = json_data.get('handle_type')

				print_debug('接受到网络数据', task_type, handle_type)

				# 导航树操作
				if task_type == 'tree':
					if json_data.get('handle_type') == 'select':
						key = json_data['user_info'].get('key', '')
						# if key == '验证码监控':
						counter(ui_log, 'EVENT', 'SELECT', key)

						self.contain.switch(key)

						self.parent.update()
				# 右边扩展功能
				elif task_type == 'extend':
					counter(ui_log, 'EVENT', 'extend')

					if handle_type == 'create':
						self.contain.switch(handle_type)

						# 刷新hosts
						json_host_request = {
							'task_type': 'host',
							'handle_type': 'query',
							'user_info': {}
						}

						try:
							self.queue_to_net.put(json_host_request, True, 0.5)
						except Exception as ex:
							msg('后台处理忙，稍后重试')
							self.event_running = False
							return
					else:
						self.tree.set_filter(handle_type)
					self.parent.update()

				#host信息，或者select用户的日志
				elif task_type == 'host' or task_type == 'log' or \
					task_type == 'select' or task_type == 'login' or task_type == 'yzm':
					counter(ui_log, 'MAIN_EVENT', task_type, handle_type)
					self.contain.refresh(json_data)
					self.parent.update()


				elif task_type == 'user':
					# 列表形式返回的用户信息
					if json_data.get('handle_type') == 'list':
						user_list = json_data['user_info']
						for user_info in user_list:
							self.tree.add(key=user_info.get('clsbdh'), name=user_info.get('tbSyr'),
										  status=user_info.get('status'))

						self.contain.refresh(json_data)

						self.parent.update()
					elif json_data.get('handle_type') == 'update':
						# 更新
						user_info = json_data.get('user_info')
						if user_info is None or user_info == '':
							counter(ui_log, 'MAIN', 'EVENT', 'USER', 'UPDATE', 'FAIL', 'NULL_INFO')
							return

						self.tree.add(key=user_info.get('clsbdh'), name=user_info.get('tbSyr',''),
									  status=user_info.get('status',''))

						self.contain.refresh(json_data)

						counter(ui_log, 'MAIN', 'EVENT', 'USER', 'UPDATE', 'SUCCESS', user_info.get('clsbdh'))

						self.parent.update()


					elif json_data.get('handle_type') == 'delete':
						user_info = json_data.get('user_info')
						if user_info is None or user_info == '':
							counter(ui_log, 'MAIN', 'EVENT', 'USER', 'DELETE', 'FAIL', 'NULL_INFO')
							self.event_running = False
							return

						self.tree.rmv(key=user_info.get('clsbdh', ''))
						self.contain.refresh(json_data)


					else:
						pass
				else:
					pass

			except Exception as ex:
				counter(ui_log, 'MAIN', 'EVENT', 'ERROR', ex)
			finally:
				self.event_running = False

		self.parent.bind('<<net_data_recv>>', lambda e: __net_data_recv__())


#点击事件
def click(parent,json_task,queue_ui_intra=None,queue_to_net=None):
	try:
		if queue_ui_intra:
			#点击生成页面刷新事件
			queue_ui_intra.put(json_task,True,3)
			parent.event_generate('<<main_refresh>>',when='tail')

		if queue_to_net:
			queue_to_net.put(json_task,True,3)

	except Exception as ex:
		msg('操作异常')
		counter(ui_log,'CLICK','ERROR',ex)


#不在窗体类内部，定义一个函数，生成事件
#监听后台请求，生成事件
def __ui_listen__(root,queue_from_net,queue_ui_intra):

	while True:
		try:


			#UI事件监听
			counter(ui_log,'UI_LISTEN','RUNNING')

			json_data = queue_from_net.get(True)

			counter(ui_log,'UI_LISTEN','START')

			#5秒的响应时间
			queue_ui_intra.put(json_data,True,5)

			root.event_generate('<<net_data_recv>>',when='tail')

			counter(ui_log,'UI_LISTEN','SUCCESS')

		#窗体刷新失败
		except Exception as ex:
			counter(ui_log,'UI_LISTEN','ERROR',ex)
			print_error('处理网络任务异常',ex)


#视窗程序
def __main_win__(queue_from_net, queue_to_net):

	root = Tk()
	# UI进程内部队列,一个一个处理
	queue_ui_intra = Queue(1)

	main_win = Main_win(root, queue_ui_intra, queue_to_net)

	threading_ui_listen = threading.Thread(target=__ui_listen__, args=(root, queue_from_net, queue_ui_intra,))
	threading_ui_listen.start()


	root.mainloop()

#通信进程
def __communication__(server, server_port, hostname, queue_from_net, queue_to_net):
	# 后台通信进程启动
	login = login_to_server(user_type= client.UI.value, server=server, port=server_port, hostname=hostname, queue_from_net=queue_from_net,
							queue_to_net=queue_to_net)

#主程序入口
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
		counter(ui_log,'MAIN','CONFIG','ERROR',ex)
		print_error('加载配置文件异常',ex)

	try:
		queue_from_net = Queue(20)
		queue_to_net = Queue(2)

		server = configInfo.get('server_host', 'www.wuyoubar.cn')
		server_port = int(configInfo.get('slogin_port', '61236'))
		hostname = 'ui-client-' + configInfo.get('hostname', gethostname())
	except:
		print_error('初始化配置失败')


	try:
		# 启动后台通信进程
		communication = Process(target=__communication__,args=(server,server_port,hostname,queue_from_net,queue_to_net,))
		communication.start()
	except Exception as ex:
		print_error('注册异常',ex)

	try:
		ui = Process(target=__main_win__,args=(queue_from_net,queue_to_net,))
		ui.start()
	except Exception as ex:
		pass


	#窗口隐藏
	"""whnd = ctypes.windll.kernel32.GetConsoleWindow()
	if False and whnd != 0:
		ctypes.windll.user32.ShowWindow(whnd, 0)
		ctypes.windll.kernel32.CloseHandle(whnd)"""








			

		

