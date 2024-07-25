import os
import multiprocessing
import colorama
import datetime
import Levenshtein
import time 
import json
import shutil

import pyfiglet

from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual import events
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on


from termcolor import *

colorama.init()




class ASPC_CommonApplication:


	def display_ascii_function(self, message, size="small"):

		if size == "big":
			font = pyfiglet.Figlet(font="ansi_shadow")
			#font = pyfiglet.Figlet(font="fraktur")
		if size == "small":
			font = pyfiglet.Figlet(font = "modular")

		print(colored(font.renderText(message), "yellow"))

	def display_message_function(self, message):
		print("[%s] %s"% (str(datetime.datetime.now()), message))
	def display_error_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "red"))

	def display_warning_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "magenta"))

	def display_success_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "cyan"))

	def display_notification_function(self, message):
		print(colored("[%s] %s" % (str(datetime.datetime.now()), message), "yellow"))








	def load_settings_function(self):
		#check for the settings file
		try:

			with open(os.path.join(os.getcwd(), "Data/Settings.json"), "r") as read_settings:
				self.settings = json.load(read_settings)
		except:
			self.display_error_function("Impossible to load settings file")
			self.create_settings_function()
		




	def create_settings_function(self):
		self.settings = {
			"Manual": {
				"saveJson":True,
				"executeSpeedTest":True,
				"speedTestThreshold":None,
				"numberOfProcessMode":"core",
				"numberOfProcess":multiprocessing.cpu_count(),
			},
			"Live": {}
		}

		self.save_settings_function()


	def save_settings_function(self):

		
		self.show_message_function(os.path.join(os.getcwd(), "Data/Settings.json"))
		with open(os.path.join(os.getcwd(), "Data/Settings.json"), "w") as save_file:
			json.dump(self.settings, save_file, indent=4)

		for key, value in self.settings.items():
			self.show_message_function("%s : %s"%(key, value))
	


	def update_settings_function(self):
		self.show_message_function("hello world!")







	#MATH FUNCTIONS
	def get_average_size_function(self, file_list=None):

		if len(list(file_list.values())) != 0:
			size_addition = 0
			for size in list(file_list.values()):
				size_addition += size 
			return size_addition / len(list(file_list.values()))


	def get_average_function(self, a, b):
		a_value = a.value 
		b_value = b.value
		if b_value != 0:
			return a_value / b_value
		else:
			return


	def get_size_mo_function(self,size):

		return size / (1024 ** 2)


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



	def time_stamp_return(x):

		def wrapper(self, *args, **kwargs):
			start = time.time()

			result = x(self, *args, **kwargs)
	
			end = time.time()
			delta = end - start
			

			return result, start, end, delta
		return wrapper



	@time_stamp_return
	def copy_file_function(self,source, destination):
		try:
			shutil.copy(source, destination)
		except:
			return False
		else:
			return True


	@time_stamp_return
	def delete_file_function(self,file):

		try:
			os.remove(file)
		except:
			
			return False
		else:
			return True
	


	def worker_speed_test_function(self,type,temp_path,file):
		
		self.display_message_function("Starting speed test [%s] : %s"%(type,file))
		start_worker = time.time()
		if file != None:	
			success,start_copy,end_copy,delta_copy=self.copy_file_function(file, os.path.join(temp_path, os.path.basename(file)))
			#print(colored("COPIED [%s] %s  "%(file,delta_copy)))


			if success == True:
				success,start_delete,end_delete,delta_delete = self.delete_file_function(os.path.join(temp_path,os.path.basename(file)))
			#print(colored("REMOVED [%s] %s"%(file, delta_delete), "cyan"))	
			else:
				delta_delete = None

			end_worker = time.time()
			delta_worker = end_worker - start_worker
			self.speed_test_data[type] = {
				"filename":file,
				"speedTestDelta":delta_worker,
				"copyDelta":delta_copy,
				"removeDelta":delta_delete,
			}
		else:
			self.speed_test_data[type] = None


