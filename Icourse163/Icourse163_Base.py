
if not __package__:
	import sys
	sys.path.append('../')
from Mooc.Mooc_Base import *

class Icourse163_Base(Mooc_Base):
	def __init__(self):
		super().__init__()
		self.__mode = None
		self.__cid = None
		self.__link = None
		self.__title = None
		self.__term_id = None
		self.__unit_link = None
		self.__all_info = None
		self.all_info = {}
		self.unit_link = {}

	@property
	def mode(self):
		return self.__mode
	
	@mode.setter
	def mode(self, mode):
		self.__mode = mode

	@property
	def cid(self):
		return self.__cid
	
	@cid.setter
	def cid(self, cid):
		self.__cid = cid

	@property
	def link(self):
		return self.__link

	@link.setter
	def link(self, link):
		self.__link = link

	@property
	def title(self):
		return self.__title
	
	@title.setter
	def title(self, title):
		self.__title = title

	@property
	def term_id(self):
		return self.__term_id
	
	@term_id.setter
	def term_id(self, term_id):
		self.__term_id = term_id

	@property
	def unit_link(self):
		return self.__unit_link
	
	@unit_link.setter
	def unit_link(self, unit_link):
		self.__unit_link = unit_link

	@property
	def all_info(self):
		return self.__all_info
	
	@all_info.setter
	def all_info(self, all_info):
		self.__all_info = all_info

	@abstractmethod
	def _getCid(self):
		pass

	@abstractmethod
	def _getTitle(self):
		pass

	@abstractmethod
	def _getTermId(self, response):
		pass

	@abstractmethod
	def _getUnitLink(self, content_id, content_type, uid):
		pass

	@abstractmethod
	def _getUnitInfo(self, chapter, response):
		pass

	@abstractmethod
	def _getAllInfo(self):
		pass

	@abstractmethod
	def _printInfo(self):
		pass

	@abstractmethod
	def _creatHTML(self):
		pass

	@abstractmethod
	def prepare(self, url):
		pass