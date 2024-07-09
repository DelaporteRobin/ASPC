import os
import multiprocessing 
import threading
import scandir
import time
import datetime
import sys
import queue

from termcolor import *
from functools import wraps


from Data.ASPC_Common import ASPC_CommonApplication


class ASPC_SearchingApplication(ASPC_CommonApplication):







##############################################################################
# PART OF THE SEARCHING SYSTEM THAT CREATE THE FILE QUEUE FOR MULTIPROCESSING
##############################################################################

	def time_stamp(x):

		def wrapper(self, *args, **kwargs):
			start = time.time()


			self.display_message_function(" [%s] Started"%x)

			result = x(self, *args, **kwargs)

			
			end = time.time()
			delta = end - start
			self.display_message_function(" [%s] Ended after : %s"%(x,delta))

			return result
		return wrapper










	
	@time_stamp
	def file_queue_init_function(self, root_folder=None):
		if (root_folder == None) or (os.path.isdir(root_folder)==False):
			self.display_error_function("Folder doesn't exists!")
			return
		else:

			self.folder_count = 0
			self.main_folder_list = []

			#create the list for the queue creation threads 
			queue_creation_thread_list = []
			#get root folder content
			root_content = os.listdir(root_folder)
			if len(root_content) == 0:
				self.display_error_function("No content in folder!")
				return 
			else:
				for item in root_content:
					if os.path.isdir(os.path.join(root_folder,item)) == True:
						self.folder_count += 1

						#add the root folder to the queue
						if (os.path.join(root_folder,item) not in self.main_folder_list):
							self.main_folder_list.append(os.path.join(root_folder, item))
							self.folder_count += 1
						#create the thread to get the folder content and create the folder queue
						x = threading.Thread(target=self.explore_folder_function, args=(os.path.join(root_folder,item),))
						x.start()
						self.display_warning_function("Started")
						queue_creation_thread_list.append(x)

				
				for thread in queue_creation_thread_list:
					thread.join()
					self.display_notification_function("Thread terminated : %s"%thread)



				
				self.display_success_function("File queue creation done")
				self.display_message_function("Number of folder : %s"%self.folder_count)

				return self.main_folder_list









	@time_stamp
	def explore_folder_function(self,folder):

		self.display_message_function("Exploring : %s"%folder)

		for root, dirs, files in scandir.walk(folder):
			for d in dirs:
				self.folder_count += 1
				if os.path.join(folder,d) not in self.main_folder_list:
						#self.main_folder_list.append(os.path.join(folder,d))
						self.main_folder_list.append(os.path.join(folder,d))

		#self.display_warning_function("Terminated")






##############################################################################
# PART OF THE PROGRAM THAT COLLECT DATA (TRIGGERED)
##############################################################################
	@time_stamp
	def collect_data_from_project_init_function(self,root_folder,file_queue):

		#get the number of cpu to launch multiprocessing
		#that value needs to be customized in settings !!!
		#TO DO IN NEXT VERSIONS
		cpu_count = multiprocessing.cpu_count()
		self.display_notification_function("Maximum number of processes : %s"%cpu_count)


		self.process_list = []

		for i in range(cpu_count):
			process = multiprocessing.Process(target=self.worker_function, args=(root_folder,file_queue,))
			self.process_list.append(process)
			process.start()




	def worker_function(self, root_folder = None, file_queue = None):
		while not queue.empty():
			folder = queue.get()

			if folder == None:
				break
			else:
				self.display_message_function("Process [%s] inspecting folder : %s"%( os.getpid(), folder))







	


	