import os
import multiprocessing
import colorama
import datetime
import Levenshtein
import time 

from termcolor import *

colorama.init()




class ASPC_CommonApplication:



	def display_message_function(self, message):
		print("[%s] %s"% (str(datetime.datetime.now()), message))
	def display_error_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "red"))

	def display_warning_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "yellow"))

	def display_success_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "green"))

	def display_notification_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "magenta"))






	#MATH FUNCTIONS
	def get_average_size_function(self, file_list=None):

		if len(list(file_list.values())) != 0:
			size_addition = 0
			for size in list(file_list.values()):
				size_addition += size 
			return size_addition / len(list(file_list.values()))


	def get_average_function(self, a, b):
		return a/b


	def get_extremum_size_function(self, type="max", file_list = None):
		file_name = list(file_list.keys())
		file_size = list(file_list.values())

		if len(file_list) != 0:
			if type=="max":
				extremum = file_size.index(max(file_size))
			else:
				extremum = file_size.index(min(file_size))

			return (file_name[extremum], file_size[extremum])


	def comparison_function(self,comparison, target):
		distance = Levenshtein.distance(target, comparison)
		length = max(len(target), len(comparison))
		similitude = ((length - distance) / length)*100

		#print("%s : [%s ; %s]"%(similitude,target, comparison))
		return similitude



	def get_date_function(self,file):
		creation_date = os.path.getctime(file)
		modification_date = os.path.getmtime(file)
		time_delta = modification_date - creation_date

		return creation_date, modification_date, time_delta