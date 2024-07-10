import os
import multiprocessing 
import threading
import scandir
import time
import datetime
import sys
import queue

from multiprocessing import Manager
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


			self.display_message_function(" [%s] Started"%(x))

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
	def get_data_init(self,root_folder, folder_list):

		with Manager() as manager:
			self.global_folder_dictionnary = manager.dict()
			self.global_file_dictionnary = manager.dict()

			self.root_folder=root_folder
			self.main_folder_list = folder_list 

			file_queue = multiprocessing.Queue()
			p_list = []
			
			for folder in self.main_folder_list:
				file_queue.put(folder)
			

			for i in range(multiprocessing.cpu_count()):
				try:
					p = multiprocessing.Process(target=self.get_data_worker, args=(file_queue,self.root_folder,))
					#self.display_notification_function("Process created : %s"%p)
					p.start()
					
					#self.display_success_function("Process created successfully!")
					p_list.append(p)
				except:
					self.display_error_function("Impossible to create process : %s"%p)
					break
			
			
			for p in p_list:
				p.join()

			self.display_notification_function("Number of process created : %s"%len(p_list))

			#print(self.global_data_dictionnary)


	def get_data_worker(self, test_queue, root_folder):
		while not test_queue.empty():
			folder = test_queue.get()

			if folder == None:
				break
			else:
				#get data from folder and update value in dictionnary
				#print("added")
				
				#CHECK LIST FOR EACH FOLDER AND FILES
				"""
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



				#get the content of the folder
				#get the file list
				#get the subfolder list

				print("%s : %s"%(os.path.isdir(folder),folder))

				"""
				folder_content = os.listdir(folder)
				file_list = []
				subfolder_list = []

				for f in folder_content:
					if os.path.isfile(os.path.join(folder,f))==True:
						file_list.append(os.path.join(folder, f))
					if os.path.isdir(os.path.join(folder,f))==True:
						subfolder_list.append(os.path.join(folder,f))
				"""

				
	


	