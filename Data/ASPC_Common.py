import os
import multiprocessing
import colorama
import datetime

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