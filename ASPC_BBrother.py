import os
import sys
import colorama
import time


from termcolor import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from time import sleep

import pyfiglet
import shutil
import json
import getpass



colorama.init()





class MyHandler(FileSystemEventHandler):

	def __init__(self, project_settings):
		self.settings = project_settings
		#load the observer log
		self.main_log = {}
		self.load_observer_log_function()





	def load_observer_log_function(self):
		try:
			with open(self.settings["logPath"], "r") as read_data:
				self.main_log = json.load(read_data)
		except:
			print(colored("Impossible to get log dictionnary", "red"))
		else:
			print(colored("Log dictionnary loaded", "green"))


	def save_log_function(self):
		try:
			with open(self.settings["logPath"], "w") as save_file:
				json.dump(self.main_log, save_file, indent=4)
		except:
			print(colored("Impossible to save log", "red"))


	def on_created(self, event):
		print(f"Created: {event.src_path}")
		target_folder = event.src_path
		proxy_folder = target_folder

		for i in range(100):
			proxy_folder = os.path.dirname(os.path.normpath(proxy_folder))
			if os.path.normcase(os.path.normpath(proxy_folder)) == os.path.normcase(os.path.normpath(self.settings["projectPath"])):
				break
			else:
				if proxy_folder not in self.main_log:
					self.main_log[proxy_folder] = 1
				else:
					self.main_log[proxy_folder] = self.main_log[proxy_folder] + 1

		self.save_log_function()


		 

	#def on_modified(self, event):
	#	print(f"Modified: {event.src_path}")

	def on_deleted(self, event):
		print(f"Deleted: {event.src_path}")
		target_folder = event.src_path
		proxy_folder = target_folder

		for i in range(100):
			proxy_folder = os.path.dirname(os.path.normpath(proxy_folder))
			if os.path.normcase(os.path.normpath(proxy_folder)) == os.path.normcase(os.path.normpath(self.settings["projectPath"])):
				break
			else:

				if self.main_log[proxy_folder] == 1:
					self.main_log.pop(proxy_folder)
				else:
					self.main_log[proxy_folder] = self.main_log[proxy_folder] - 1

		self.save_log_function()

	def on_moved(self, event):
		print(f"Moved: {event.src_path} to {event.dest_path}")






class Application:
	def __init__(self):


		self.font_title = pyfiglet.Figlet(font="ansi_shadow")
		print(colored(self.font_title.renderText("ASPC\nLive mode"), "cyan"))


		#get the real path of the program
		self.real_program_path = os.path.dirname(os.path.abspath(sys.argv[0]))
		print(self.real_program_path)

		#try to load settings
		self.settings = {}
		load_value = self.load_settings_function()
		if load_value == False:
			exit()

		for key, value in self.settings.items():
			print("[ %s ] --> %s"%(key,value))

		self.launch_job()




	def load_settings_function(self):
		try:
			with open(os.path.join(self.real_program_path, "Data/Live_Settings.json"), "r") as read_settings:
				self.settings = json.load(read_settings)
		except:
			print(colored("Impossible to load settings", "red"))
			return False
		else:
			print(colored("Settings loaded", "green"))
			return True






	def launch_job(self):
		try:
			observer = Observer()
			handler = MyHandler(self.settings)
			observer.schedule(handler, path="D:/TRASH", recursive=True)
			observer.start() 

			print(colored("Observer launched", "cyan"))

			sleep(1)

			try:
				while True:
					time.sleep(1)
			except KeyboardInterrupt:
				observer.stop()
			observer.join()
		except:
			print(colored("Impossible to launch observer", "red"))



Application()

	
	
	
	
	