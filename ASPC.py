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


		self.root_folder = "D:/TRASH/poster"

		#self.queue_size_limit = 50000
		self.main_data_set_dictionnary = {}
		self.main_log_list = []

		

		


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
		self.main_folder_queue = self.sa.file_queue_init_function(self.root_folder)

		self.display_message_function(type(self.main_folder_queue))
		#self.display_message_function(self.main_folder_queue)

		#display the content of the folder list
		#for folder in self.main_folder_list:
		#	print(folder)


		#create the test class
		#self.mpa = ASPC_ProcessApplication()
		#self.mpa.get_data_init(self.root_folder, self.main_folder_list)
		self.sa.get_data_init(self.root_folder, self.main_folder_queue)
		



#class ASPC_ProcessApplication:

	







#launch the application
if __name__ == "__main__":
	application = ASPC_Application
	application()