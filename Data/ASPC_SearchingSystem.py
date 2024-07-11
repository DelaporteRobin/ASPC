import os
import multiprocessing 
import threading
import scandir
import time
import datetime
import sys
import queue
import json

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
			self.main_folder_queue = multiprocessing.Queue()

			#get root folder content
			root_content = os.listdir(root_folder)
			if len(root_content) == 0:
				self.display_error_function("No content in folder!")
				return 
			else:

				thread_list = []
				thread_lock = threading.Lock()

				for content in root_content:
					thread = threading.Thread(target=self.get_folder_content_worker, args=(os.path.join(root_folder, content), thread_lock))
					thread.start()
					thread_list.append(thread)
					self.display_notification_function("Thread started: %s" % thread)

				for thread in thread_list:
					thread.join()

				#for folder in self.main_folder_list:
				#	print(folder)
				return self.main_folder_queue

	def get_folder_content_worker(self, root_folder, lock):
		for root, dirs, files in scandir.walk(root_folder):
			for d in dirs:
				with lock:
					#self.main_folder_list.append(os.path.join(root, d))
					self.main_folder_queue.put(os.path.join(root, d))
					






	def save_data_function(self):
		with open(os.path.join(os.getcwd(), "data_file.json"), "w") as save_file:
			json.dump(dict(self.global_file_dictionnary), save_file, indent=4)

		with open(os.path.join(os.getcwd(), "data_folder.json"), "w") as save_folder:
			json.dump(dict(self.global_folder_dictionnary), save_folder, indent=4)


		self.display_notification_function("DATA SAVED IN FILES!")
		print(os.getcwd())







##############################################################################
# PART OF THE PROGRAM THAT COLLECT DATA (TRIGGERED)
##############################################################################

	@time_stamp
	def get_data_init(self,root_folder, folder_queue):


		self.display_notification_function("Ready to launch processes ! ")
		with Manager() as manager:
			self.global_folder_dictionnary = manager.dict()
			self.global_file_dictionnary = manager.dict()

			self.root_folder=root_folder
			#self.main_folder_list = folder_list 

			#file_queue = multiprocessing.Queue()
			p_list = []
			

			"""
			self.display_message_function("Started to create the folder queue")
			for folder in self.main_folder_list:
				if os.path.isdir(folder)==True:
					file_queue.put(folder)
			self.display_message_function("Queue created")
			"""
			
			
			for i in range(multiprocessing.cpu_count()):
				try:
					p = multiprocessing.Process(target=self.get_data_worker, args=(folder_queue,self.root_folder,))
					#self.display_notification_function("Process created : %s"%p)
					p.start()
					
					self.display_success_function("Process created successfully!")
					p_list.append(p)
				except:
					self.display_error_function("Impossible to create process : %s"%p)
					break
			
			
			for p in p_list:
				p.join()
				self.display_success_function("Process terminated successfully")

			self.display_notification_function("Number of process created : %s"%len(p_list))

			self.save_data_function()
			#print(self.global_data_dictionnary)





	def get_data_worker(self, test_queue, root_folder):
		while not test_queue.empty():
			folder = test_queue.get()

			if folder == None:
				break
			else:

				
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



				#print("%s : %s"%(os.path.isdir(folder),folder))

				if os.path.isdir(folder) == True:
					#get the content of the folder
					#file list
					#subfolder list
					subfolder_list = []
					file_list = {}
					parent_list = []
					parent_proxy =  folder

					folder_content = os.listdir(folder)


					#GET THE FOLDER CONTENT
					# FILE LIST
					# SUBFOLDER LIST
					for i in range(10):
						parent_proxy = os.path.dirname(parent_proxy)
						parent_proxy_slash = parent_proxy
						if parent_proxy_slash[-1] != "/":
							parent_proxy_slash = "%s/"%parent_proxy_slash
						
						parent_list.append(parent_proxy)
						if parent_proxy_slash == root_folder:
							break
					
					folder_size = 0
					for item in folder_content:
						if os.path.isfile(os.path.join(folder,item))==True:


							#create a dictionnary of information for that file
							file_size = os.path.getsize(os.path.join(folder,item))
							file_list[os.path.join(folder,item)] = file_size

							self.global_file_dictionnary[os.path.join(folder,item)] = {
								"fileSize": file_size
								}
							#add the file of the size to the folder size
							folder_size += file_size
							

							#add that size for each folder in dictionnary
						if os.path.isfile(os.path.join(folder, item))==True:
							subfolder_list.append(os.path.join(folder,item))

					

					#GET THE MATH VALUE FROM THE FOLDER
					#	average size
					# 	lowest size
					#	heaviest size
					average_file_size=self.get_average_size_function(file_list)
					max_file_size = self.get_extremum_size_function("max",file_list)
					min_file_size = self.get_extremum_size_function("min", file_list)
					#min_file_size = self.get_min_size_function(file_list)
					#self.get_highest_value_function(file_list)
					#self.get_lowest_value_function(file_list)


					#SET THE INITIAL SIZE OF THE FOLDER WITH THE FILES IT CONTAINS (WITHOUT SUBFOLDERS)
					if folder not in self.global_folder_dictionnary:
						self.global_folder_dictionnary[folder] = {
							"folderSize": folder_size,
							"fileContainedSize": folder_size,
							"subfoldersNumber":len(subfolder_list),
							"filesNumber": len(file_list),
							"averageFileSize":average_file_size,
							"maxFileSize":max_file_size,
							"minFileSize":min_file_size,
							"subfolderList": subfolder_list,
							"fileList": file_list,
						}


					


					#UPDATE THE SIZE OF PARENTS FOLDER WITH THE ACTUAL FOLDER SIZE
					for parent_folder in parent_list:
						if parent_folder not in self.global_folder_dictionnary:
							self.global_folder_dictionnary[parent_folder] = {
								"folderSize": folder_size
							}
						else:
							#get the value of the current folder size if it is in the dictionnary
							#except --> CREATE THE KEY
							folder_data = self.global_folder_dictionnary[parent_folder]
							if "folderSize" not in folder_data:
								folder_data["folderSize"] = folder_size
							else:
								folder_data["folderSize"] = folder_data["folderSize"] + folder_size
							#save the new value of the dictionnary
							self.global_folder_dictionnary[parent_folder] = folder_data
					#self.display_success_function("Size of the folder [%s]: %s"%(os.path.join(folder,item),folder_size))

				
				
	


	