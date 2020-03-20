from abc import ABC, abstractmethod
from Mooc_Request import *
from Mooc_Config import *
from ftplib import FTP
import asyncio
import aiohttp
import json
import os

class Mooc_Base(ABC):
	def __init__(self):
		self._base_path = os.path.abspath(os.getcwd()).split('MoocBot')[0] + '/MoocBot'

	@staticmethod
	def postInfo(mooc_info):
		url = 'http://127.0.0.1:5000/mooc/api'
		response = requestPost(url, data = mooc_info)
		print(response.text)

def main():
	pass

if __name__ == '__main__':
	main()