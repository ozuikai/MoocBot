from time import sleep
from functools import wraps
from requests_html import requests
from Mooc_Config import *

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
}

def requestDecorate(func):
	@wraps(func)
	def requestPro(*args, **kwargs):
		while True:
			try:
				response = func(*args, **kwargs)
				if 'x-application-context' in response.headers and 'mooc:online' in response.headers['X-Application-Context']:
					if 'CourseBean' in args[0]:
						ret = response.text.encode('utf8').decode('unicode_escape')
						return ret
					return response.text
				else:
					# continue
					# sleep(2)
					return response
			except Exception as err:
				print(err)
				# raise
				pass
	return requestPro

@requestDecorate
def requestGet(url):
	response = requests.get(url, headers = headers, timeout = TIMEOUT)
	return response

@requestDecorate
def requestPost(url, data):
	response = requests.post(url, data = data, headers = headers, timeout = TIMEOUT)
	return response