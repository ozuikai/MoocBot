import re
import os
if __package__ is None:
	import sys
	sys.path.append('..\\')
	sys.path.append("..\\..\\")
import time
import threading
from MoocBot.Mooc_Request import *
from MoocBot.Mooc_Config import *
from MoocBot.Icourse163.Icourse163_Base import *
from MoocBot.Icourse163.Icourse163_Config import *

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
		# chapter
		chapter_info = []
		chapter_prefix = [re.findall(fr'{i}\.lessons=(\w*\d*)', response) for i in lessons]
		chapter = [re.findall(fr'{i[0]}\[\d*\]=(\w*\d*)', response) for i in chapter_prefix]
		for i_list in chapter:
			chapter_name_sub = [re.findall(fr'{i}\.name="(.+)"', response) for i in i_list]
			chapter_name_sub = [i[0] for i in chapter_name_sub]
			chapter_info.append(chapter_name_sub)
		# unit-video / unit-pdf
		unit_info = self._getUnitInfo(chapter, response)
		self.all_info['lesson_info'] = lesson_info
		self.all_info['chapter_info'] = chapter_info
		self.all_info['unit_info'] = unit_info

	def prepare(self, url):
		self._getCid(url)
		data = {
			'cid': self.cid
		}
		ret = self.checkInfo(data)
		if not ret:
			self._getTitle()
			self._getAllInfo()
			data = {
				'cid': self.cid,
				'title': self.title,
				'info': str(self.all_info)
			}
			ret = self.postInfo(data)
			print(ret)
		return self.link

def main():
	url = 'https://www.icourse163.org/learn/BIT-1001870002'
	# url = 'https://www.icourse163.org/learn/HIT-69005'
	# url = 'https://www.icourse163.org/learn/XJTU-1206495807'
	mooc = Icourse163_Mooc()
	mooc.prepare(url)

if __name__ == '__main__':
	main()