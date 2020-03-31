if not __package__:
	import sys
	sys.path.append('.\\')
	sys.path.append('..\\')

from Icourse163.Icourse163_Mooc import *

def mooc(url, update=None):
	mooc = Icourse163_Mooc()
	link = mooc.prepare(url, update)
	return link

if __name__ == '__main__':
	mooc()