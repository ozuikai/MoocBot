from abc import ABC, abstractmethod
from Mooc_Request import *
from Mooc_Config import *
import asyncio
import aiohttp
import json
import os

class Mooc_Base(ABC):
	def __init__(self):
		self._base_path = os.path.abspath(os.getcwd()).split('MoocBot')[0] + '/MoocBot'

	@staticmethod
	def postInfo(mooc_info):
		# url = 'http://127.0.0.1:5000/mooc/insert'
		url = 'http://178.62.80.215:5000/mooc/insert'
		response = requestPost(url, data = mooc_info)
		ret = response.json()
		return ret

	@staticmethod
	def checkInfo(mooc_info, update):
		# url = 'http://127.0.0.1:5000/mooc/query'
		url = 'http://178.62.80.215:5000/mooc/query'
		headers = { 'Content-Type': 'application/json' }
		mooc_info = json.dumps(mooc_info)
		response = requestPost(url, data = mooc_info, headers = headers)
		ret = response.json()
		if ret['code'] == 200:
			if update == 'update':
				return False
			return True
		else:
			return False

def main():
	pass

if __name__ == '__main__':
	main()