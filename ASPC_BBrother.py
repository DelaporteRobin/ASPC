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
	def on_created(self, event):
		print(f"Created: {event.src_path}")

	def on_modified(self, event):
		print(f"Modified: {event.src_path}")

	def on_deleted(self, event):
		print(f"Deleted: {event.src_path}")

	def on_moved(self, event):
		print(f"Moved: {event.src_path} to {event.dest_path}")




class Application:
	def __init__(self):


		self.font_title = pyfiglet.Figlet(font="ansi_shadow")
		print(colored(self.font_title.renderText("ASPC\nLive mode"), "cyan"))


	def launch_job(self):
		try:
			observer = Observer()
			handler = MyHandler()
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

	
	
	
	
	