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

		self.queue_size_limit = 50000
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
		self.main_folder_list = self.sa.file_queue_init_function(self.root_folder)
		#self.display_message_function(self.main_folder_queue)


		#YOU NEED TO CREATE A CONSUMER FOR THE QUEUE IN ORDER TO NOT LOCK IT DUMBASS!

		test_queue = multiprocessing.Queue()
		for item in self.main_folder_list:
			test_queue.put(item, block=True, timeout=None)

		p_list = []

		for i in range(multiprocessing.cpu_count()):
			p = multiprocessing.Process(target=self.test_worker, args=(test_queue,))
			p.start()
			p_list.append(p)



	def test_worker(self, queue):
		while not queue.empty():
			item = queue.get()

			if item == None:
				break
			else:
				print(item)

		






#launch the application
if __name__ == "__main__":
	application = ASPC_Application
	application()