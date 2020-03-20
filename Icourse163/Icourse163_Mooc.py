import re
import os
if __package__ is None:
	import sys
	sys.path.append('..\\')
	sys.path.append("..\\..\\")
import time
# import asyncio
# from lxml import etree
import threading
from Mooc.Mooc_Request import *
from Mooc.Mooc_Config import *
from Mooc.Icourse163.Icourse163_Base import *
from Mooc.Icourse163.Icourse163_Config import *

class Icourse163_Mooc(Icourse163_Base):
	course_url = "https://www.icourse163.org/course/"
	term_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
	lesson_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'
	term_data = {
		'callCount':1,
		'scriptSessionId':'${scriptSessionId}190',
		'httpSessionId':'51410da9a0534c8eb5baa69415174073',
		'c0-scriptName':'CourseBean',
		'c0-methodName':'getMocTermDto',
		'c0-id':0,
		'c0-param0':None, #f'number:{tid}',
		'c0-param1':'number:0',
		'c0-param2':'boolean:true',
		'batchId':1582603197381
	}

	lesson_data = {
		'callCount':1,
		'scriptSessionId':'${scriptSessionId}190',
		'httpSessionId':'51410da9a0534c8eb5baa69415174073',
		'c0-scriptName':'CourseBean',
		'c0-methodName':'getLessonUnitLearnVo',
		'c0-id':0,
		'c0-param0':None, #f'number:{contentId}',
		'c0-param1':None, #f'number:{contentType}',
		'c0-param2':'number:0',
		'c0-param3':None, #f'number:{id}',
		'batchId':1582604993425
	}

	def __init__(self):
		super().__init__()
		self.mode = MODE

	def _getCid(self, url):
		self.cid = None
		match = courses_re['icourse163'].match(url)
		if match and match.group(4):
			self.cid = match.group(4)
			self.link = f'https://mooc.uue.me/icourse163/{self.cid}.html'

	def _getTermId(self, response):
		ret = re.search(r'termId : "(\d+)"', response)
		if ret:
			self.term_id = ret.group(1)
		# 判断是否开课 没有开课则取往期id
		ret = re.findall(r'window.termInfoList = \[\n\{((.|\n)+)\}\n\];\nwindow.categories', response)
		if ret :
			ret = ret[0][0].replace('\n', '')
			ret = ret.split('},{')
			start_time = re.findall(r'startTime : "(\d{10})\d+"', ret[-1])[0]
			if len(ret) > 1 and int(start_time) > int(time.time()):
				self.term_id = re.findall(r'id : "(\d+)"', ret[-2])[0]

	def _getTitle(self):
		if not self.cid:
			return
		self.title = self.term_id = None
		url = self.course_url + self.cid
		response = requestGet(url)
		self._getTermId(response)
		ret = re.findall(r'name:"(.+)"', response)
		if ret:
			title = '_'.join(ret)
			self.title = winre.sub('', title)[:WIN_LENGTH] # 用于除去win文件非法字符
		# print(self.title, '\n')

	def _getUnitLink(self, content_id, content_type, uid):
		download_link = None
		lesson_data = self.lesson_data.copy()
		lesson_data['c0-param0'] = f'number:{content_id}'
		lesson_data['c0-param1'] = f'number:{content_type}'
		lesson_data['c0-param3'] = f'number:{uid}'
		response = requestPost(self.lesson_url, data = lesson_data)
		if content_type == '1':
			download_link = {
				'flv':{
					'hd':None,
					'sd':None,
					'shd':None
				},
				'mp4':{
					'hd':None,
					'sd':None,
					'shd':None
				}
			}
			try:
				download_link['flv']['hd'] = re.findall(r'flvHdUrl="([\w\d:/\-_?.=]+)";', response)[0]
				download_link['flv']['sd'] = re.findall(r'flvSdUrl="([\w\d:/\-_?.=]+)";', response)[0]
				download_link['flv']['shd'] = re.findall(r'flvShdUrl="([\w\d:/\-_?.=]+)";', response)[0]
				download_link['mp4']['hd'] = re.findall(r'mp4HdUrl="([\w\d:/\-_?.=]+)";', response)[0]
				download_link['mp4']['sd'] = re.findall(r'mp4SdUrl="([\w\d:/\-_?.=]+)";', response)[0]
				download_link['mp4']['shd'] = re.findall(r'mp4ShdUrl="([\w\d:/\-_?.=]+)";', response)[0]
			except IndexError:
				pass
		elif content_type == '3':
			download_link = {
				'pdf':None
			}
			try:
				download_link['pdf'] = re.findall(r'textOrigUrl:"(.+\.pdf)",', response)[0]
			except IndexError:
				pass
		# 讨论
		elif content_type == '6':
			pass
		else:
			pass
		if download_link:
			self.unit_link[uid].update(download_link)

	def _getUnitInfo(self, chapter, response):
		unit_info = [] #all
		unit_info_sub_1 = [] #chapter
		unit_info_sub_2 = [None]*2 #unit
		threads = []
		for i_list in chapter:
			unit_sub = [re.findall(fr'{i}\.units=(\w*\d*)', response) for i in i_list]
			unit_info_sub = [] #lesson
			for i in unit_sub:
				unit_info_prefix = re.findall(fr'{i[0]}\[\d+\]\=(\w*\d*)', response)
				unit_info_sub_1 = []
				for unit_info_prefix_sub in unit_info_prefix:
					unit_info_sub_2[0] = re.findall(fr'{unit_info_prefix_sub}\.name="(.+)"', response)[0]
					unit_info_contentId = re.findall(fr'{unit_info_prefix_sub}\.contentId=(\d*)', response)[0]
					unit_info_contentType = re.findall(fr'{unit_info_prefix_sub}\.contentType=(\d*)', response)[0]
					unit_info_id = re.findall(fr'{unit_info_prefix_sub}\.id=(\d*)', response)[0]
					threads.append(threading.Thread(target = self._getUnitLink, args = (unit_info_contentId, unit_info_contentType, unit_info_id,)))
					self.unit_link[unit_info_id] = {}
					unit_info_sub_2[1] = self.unit_link[unit_info_id]
					unit_info_sub_1.append(unit_info_sub_2.copy())
				unit_info_sub.append(unit_info_sub_1)
			unit_info.append(unit_info_sub)
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		return unit_info

	def _getAllInfo(self):
		if not self.term_id:
			return
		self.all_info = {}
		self.term_data['c0-param0'] = f'number:{self.term_id}'
		response = requestPost(self.term_url, data = self.term_data)
		#lesson
		lessons = re.findall(r';\n?(\w*\d*).lessons', response)
		lesson_info = [re.findall(fr'{i}\.name="(.+)"', response) for i in lessons]
		lesson_info = [i[0] for i in lesson_info]
		# print(lesson_info, '\n')
		# chapter
		chapter_info = []
		chapter_prefix = [re.findall(fr'{i}\.lessons=(\w*\d*)', response) for i in lessons]
		chapter = [re.findall(fr'{i[0]}\[\d*\]=(\w*\d*)', response) for i in chapter_prefix]
		for i_list in chapter:
			chapter_name_sub = [re.findall(fr'{i}\.name="(.+)"', response) for i in i_list]
			chapter_name_sub = [i[0] for i in chapter_name_sub]
			chapter_info.append(chapter_name_sub)
		# print(chapter_info, '\n')
		# unit-video / unit-pdf
		unit_info = self._getUnitInfo(chapter, response)
		# print(unit_info, '\n')
		self.all_info['lesson_info'] = lesson_info
		self.all_info['chapter_info'] = chapter_info
		self.all_info['unit_info'] = unit_info

	def _printInfo(self):
		print(f'┌──{self.title}')
		for lesson_name in enumerate(self.all_info['lesson_info']):
			print(f'|  |──{lesson_name[1]}')
			for chapter_name in enumerate(self.all_info['chapter_info'][lesson_name[0]]):
				print(f'|  |  |──{chapter_name[1]}')
				for sub in self.all_info['unit_info'][lesson_name[0]][chapter_name[0]]:
					print(f'|  |  |  |──{sub[0]}')
					if sub[1]:
						for link_type in sub[1]:
							print(f'|  |  |  |  |──{link_type}')
							link_info = sub[1][link_type]
							if isinstance(link_info, dict): # video
								[print(f'|  |  |  |  |  |──{link_tag}:{link_value}') for link_tag,link_value in link_info.items()]
							if isinstance(link_info, str): # pdf
								print(f'|  |  |  |  |  |──{link_info}')

	def _creatHTML(self):
		src = ''
		src += f'<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><head></head><title>{self.title}</title><body>'
		src += f'<h3>{self.title}</h3>'
		src += '<ul>'
		for lesson_name in enumerate(self.all_info['lesson_info']):
			src += f'<li>{lesson_name[1]}</li>'
			src += '<ul>'
			for chapter_name in enumerate(self.all_info['chapter_info'][lesson_name[0]]):
				src += f'<li>{chapter_name[1]}</li>'
				src += '<ul>'
				for sub in self.all_info['unit_info'][lesson_name[0]][chapter_name[0]]:
					src += f'<li>{sub[0]}</li>'
					src += '<ul>'
					if sub[1]:
						for link_type in sub[1]:
							src += f'<li>{link_type.upper()}</li>'
							link_info = sub[1][link_type]
							if isinstance(link_info, dict): # video
								for link_tag,link_value in link_info.items():
									if link_value:
										src += f'<a href="{link_value}">{link_tag.upper()}</a> / '
									else:
										src += f'<a">{link_tag.upper()}</a> / '
								src = src[:-3]
							if isinstance(link_info, str): # pdf
								if link_info:
									src += f'<a href="{link_info}">FILE</a>'
								else:
									src += f'<a">FILE</a>'
					src += '</ul>'
				src += '</ul>'
			src += '</ul>'
		src += '</ul>'
		src += '</body></html>'
		with open(f"{self._base_path}/Mooc/Icourse163/page/{self.cid}.html", 'wb') as fp:
			fp.write(src.encode('utf-8'))
			fp.close()
		self.uploadSrc('icourse163', self.cid)

	def prepare(self, url):
		self._getCid(url)
		self._getTitle()
		self._getAllInfo()
		print(self.cid)
		print(self.all_info)
		# self._printInfo()
		# self._creatHTML()
		# return self.link

def main():
	# url = 'https://www.icourse163.org/learn/BIT-1001870002?tid=1207408201#/learn/content?type=detail&id=1212743005&sm=1'
	url = 'https://www.icourse163.org/learn/BIT-1001870002'
	# url = 'https://www.icourse163.org/learn/HIT-69005'
	# url = 'https://www.icourse163.org/learn/XJTU-1206495807'
	mooc = Icourse163_Mooc()
	ret = mooc.prepare(url)
	print(ret)

if __name__ == '__main__':
	main()