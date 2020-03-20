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

	# @abstractmethod
	# def _download(self):
	# 	pass

	@staticmethod
	def uploadSrc(path, file_name):
		ftp = FTP()
		# ftp.set_debuglevel(2)
		ftp.connect(HOST, PORT)
		ftp.login(USERNAME, PASSWORD)
		ftp.encoding = 'utf-8'
		ftp.cwd(path)
		with open(fr"{os.path.abspath(os.getcwd()).split('MoocBot')[0]}/MoocBot/Mooc/{path.capitalize()}/page/{file_name}.html", 'rb') as fp:
			ftp.storbinary(f'STOR {file_name}.html', fp, BUFSIZE)

	@staticmethod
	async def getShortLink(raw_url):
		api_url = 'http://v1.alapi.cn/api/url'
		data = {'url':{raw_url}, 'type':'1'}
		session = aiohttp.ClientSession()
		response = await session.post(api_url, data = data)
		response = await response.json()
		await session.close()
		print(response['data']['short_url'])
		return response['data']['short_url']

def main():
	Mooc_Base.uploadSrc('icourse163', 'HIT-69005')

if __name__ == '__main__':
	main()