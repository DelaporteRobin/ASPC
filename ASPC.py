#ASPC main python file
#By Quazar



import os
import sys
import colorama
import time
import threading
import scandir
import multiprocessing

from termcolor import *


from Data.ASPC_SearchingSystem import ASPC_SearchingApplication
from Data.ASPC_Common import ASPC_CommonApplication

colorama.init()






class ASPC_Application(ASPC_CommonApplication):
	def __init__(self):
		print("Hello World, this is ASPC!")


		self.root_folder = "D:/WORK/LIGHTING"

		self.main_data_set_dictionnary = {}
		self.main_log_list = []

		self.queue_size_limit = 600
		self.main_folder_queue = multiprocessing.Queue(maxsize = 50000)

		


		"""
		LIST OF INFORMATIONS TO RETURN

		FOR EACH FILES
			average file size in folder
			average file size for extension
			average file size in pipeline

			apply the performance test and get results

			name recognition algorythm
		FOR EACH FOLDERS
			get traffic for this folder
			average size in pipeline
			define if main folder?
			number of subfolders and files
			time to read files
			time to read folder

			size contained (global) compared to global size
			size contained (only files)
			--> size of the files contained compared to the number of files



		Set an observer file over time to follow folder hierarchy modification
			update the amount of time a folder or file is being used / modified.

		"""




		#IMPORT THE SIDE CLASS TO LAUNCH RESEARCH
		self.sa = ASPC_SearchingApplication()
		self.main_folder_list = self.sa.file_queue_init_function(self.root_folder)
		self.display_message_function(self.main_folder_queue)


		self.display_message_function("%s / %s"%(len(self.main_folder_list), self.queue_size_limit))
		if len(self.main_folder_list) >= self.queue_size_limit:
			self.display_error_function("Too many elements in project! You must increase the size of the Queue!")


		for i in range(600):
			self.main_folder_queue.put('hello')
	

		#LAUCH THE DATA COLLECT PROCESS
		






#launch the application
if __name__ == "__main__":
	application = ASPC_Application
	application()