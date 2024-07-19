import os
import multiprocessing 
import threading
import scandir
import time
import datetime
import sys
import queue
import json
import bisect

from multiprocessing import Manager
from termcolor import *
from functools import wraps

import pyfiglet


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
			self.display_message_function(" [%s] Ended after : %s\n\n\n\n"%(x,delta))

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
				self.display_notification_function("DETECT ALL CONTENT IN PROJECT ... ")
				

				thread_list = []
				thread_lock = threading.Lock()

				for content in root_content:
					thread = threading.Thread(target=self.get_folder_content_worker, args=(os.path.join(root_folder, content), thread_lock))
					try:
						thread.start()
						thread_list.append(thread)
						self.display_success_function("Thread started: [%s]" % thread)
					except:
						self.display_warning_function("Impossible to launch thread [%s]"%thread)
				self.display_message_function("Waiting for threads to terminate...")
				for thread in thread_list:
					self.display_success_function("Thread terminated : %s"%thread)
					thread.join()


				self.display_notification_function("ALL THREADS TERMINATED - FILE QUEUE CREATED")
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

		with open(os.path.join(os.getcwd(), "data_size_classement.json"), "w") as save_size:
			#json.dump(list(self.global_file_size_classement), save_size, indent=4)
			json.dump(list(zip(list(self.global_file_size_name_classement), list(self.global_file_size_size_classement))), save_size, indent=4)

		with open(os.path.join(os.getcwd(), "data_extension.json"), "w") as save_file:
			json.dump(dict(self.global_file_by_extension_dictionnary), save_file, indent=4)

		with open(os.path.join(os.getcwd(), "data_date.json"), "w") as save_file:
			json.dump(dict(self.global_file_date_dictionnary), save_file, indent=4)

		with open(os.path.join(os.getcwd(), "general_project_data.json"), "w") as save_file:
			json.dump(dict(self.project_general_informations_dictionnary), save_file, indent=4)

		with open(os.path.join(os.getcwd(), "data_speedtest.json"), "w") as save_file:
			json.dump(dict(self.project_speedtest_classement_heavy), save_file, indent=4)

		"""
		with open(os.path.join(os.getcwd(), "data_similary.json"), "w") as save_similar_data:
			json.dump(dict(self.global_similarity_dictionnary), save_similar_data, indent=4)
		"""


		self.display_notification_function("DATA SAVED IN FILES!")
		print(os.getcwd())







##############################################################################
# PART OF THE PROGRAM THAT COLLECT DATA (TRIGGERED)
##############################################################################

	@time_stamp
	def get_data_init(self,root_folder, folder_queue):


		self.display_notification_function("STARTING TO GET DATA FROM PROJECT\nReady to launch processes...")
		


		with Manager() as manager:
			self.global_folder_dictionnary = manager.dict()
			self.global_file_dictionnary = manager.dict()
			self.global_file_by_extension_dictionnary = manager.dict()
			self.global_file_date_dictionnary = manager.dict()
			#self.global_similarity_dictionnary = manager.dict()


			#GLOBAL PROJECT DATA OBJECTS
			self.global_project_size = multiprocessing.Value("d",0)
			self.global_project_filecount = multiprocessing.Value("i",0)
			self.global_project_foldercount = multiprocessing.Value("i",0)
			self.global_project_averagesize = multiprocessing.Value("i",0)
			self.global_project_heaviest = multiprocessing.Value("f",0)
			self.global_project_lightest = multiprocessing.Value("f",0)
			self.global_project_young = multiprocessing.Value("f",0)
			self.global_project_old = multiprocessing.Value("f",0)
			self.project_general_informations_dictionnary = manager.dict()

			self.project_speedtest_classement_heavy = manager.dict()
			self.project_speedtest_classement_light = manager.dict()

			self.global_project_heaviest_name = None
			self.global_project_lightest_name = None

			self.global_file_size_size_classement = manager.list()
			self.global_file_size_name_classement = manager.list()

			self.temp_path = os.path.join(os.getcwd(), "temp_speedtest")
			self.display_message_function("Path of the temp folder : %s"%self.temp_path)



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
					
					self.display_success_function("Process created successfully : %s"%p)
					p_list.append(p)
				except:
					self.display_error_function("Impossible to create process : %s"%p)
					break
			
			
			self.display_message_function("Waiting for processes to end!")


			for p in p_list:
				p.join()
				self.display_success_function("Process terminated successfully : %s"%p)

			self.display_notification_function("\n\nNumber of process created : %s"%len(p_list))





			#COMPUTE FINAL INFORMATIONS ABOUT PROJECT
			#average_output = self.get_average_function(self.global_project_filecount, self.global_project_size)
			
			#if average_output != None:
			#	self.global_project_averagesize = average_output
			#CREATE THE FINAL DICTIONNARY FOR GENERAL PROJECT INFORMATIONS
			"""
			self.project_general_informations_dictionnary = {
				"projectSize":self.global_project_size.value,
				"projectFileCount":self.global_project_filecount.value,
				"projectFolderCount":self.global_project_foldercount.value,
				#"projectAverageSize":self.global_project_averagesize
				"projectHeaviestSize":self.global_project_heaviest.value,
				"projectLightestSize":self.global_project_lightest.value
			}
			"""
			self.project_general_informations_dictionnary["ProjectSize"] = self.global_project_size.value
			self.project_general_informations_dictionnary["ProjectFileCount"] = self.global_project_filecount.value
			self.project_general_informations_dictionnary["ProjectFolderCount"] = self.global_project_foldercount.value
			self.project_general_informations_dictionnary["ProjectHeaviestFile"] = self.global_project_heaviest.value
			self.project_general_informations_dictionnary["ProjectLightestFile"] = self.global_project_lightest.value

			self.display_notification_function("GLOBAL INFORMATIONS ABOUT THE PROJECT")
			for key, value in self.project_general_informations_dictionnary.items():
				print("[ %s ] --> %s"%(key,value))
			self.save_data_function()
			#print(self.global_data_dictionnary)









	def get_data_worker(self, test_queue, root_folder):


		while not test_queue.empty():
			folder = test_queue.get()

			if folder == None:
				break
			else:
				self.display_ascii_function("")
				self.display_notification_function("Checking folder : %s"%root_folder)
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
					
					
					comparison_list = []
					folder_size = 0

					lightest_file = None
					lightest_filename = None
					heaviest_file = 0
					heaviest_filename = None

					for item in folder_content:
						if os.path.isfile(os.path.join(folder,item))==True:

							


							#create a dictionnary of information for that file
							file_size = os.path.getsize(os.path.join(folder,item))
							file_list[os.path.join(folder,item)] = file_size


							#update the lowest file on the folder
							if lightest_file == None:
								lightest_file = file_size
								lightest_filename = os.path.join(folder,item)
							if lightest_file > file_size:
								lightest_file = file_size
								lightest_filename = os.path.join(folder,item)
							#update the heaviest file of the folder
							if file_size > heaviest_file:
								heaviest_file = file_size
								heaviest_filename = os.path.join(folder,item)




							self.global_project_size.value += file_size
							#get the heaviest file
							if file_size > self.global_project_heaviest.value:
								self.global_project_heaviest.value = file_size
								self.project_general_informations_dictionnary["projectHeaviestFilename"] = os.path.join(folder,item)
							
							if self.global_project_filecount.value == 0:
								self.global_project_lightest.value = file_size
								self.project_general_informations_dictionnary["projectLightestFilename"] = os.path.join(folder,item)
								#print(colored("FIRST FILE SPOTED", "red"))
								#print(colored("%s : %s"%(self.project_general_informations_dictionnary["projectLightestFilename"], file_size)))

							else:
								if self.global_project_lightest.value > file_size:
									self.project_general_informations_dictionnary["projectLightestFilename"] = os.path.join(folder,item)
									#print(colored("New min file size : %s [%s]"%(file_size,self.project_general_informations_dictionnary["projectLightestFilename"])))
									self.global_project_lightest.value = file_size

							
							self.global_file_dictionnary[os.path.join(folder,item)] = {
								"fileSize": file_size
								}
							#add the file of the size to the folder size
							folder_size += file_size



							#UPDATE THE SIZE CLASSEMENT LIST
							file_size_tuple = (os.path.join(folder,item), file_size)
							#get the actual file size list

							position = bisect.bisect(self.global_file_size_size_classement, file_size)
							self.global_file_size_size_classement.insert(position,file_size)
							self.global_file_size_name_classement.insert(position,os.path.join(folder,item))
							#file_size_classement = list(map(lambda x:x[1], self.global_file_size_classement))
							#self.global_file_size_classement.insert(bisect.bisect(file_size_classement, file_size), file_size_tuple)
							#self.display_message_function("inserted")



							#GET DATA ABOUT EXTENSIONS
							#number of files for each extension
							#list of files of the given extension
							filename,extension = os.path.splitext(os.path.join(folder,item))
							if extension not in self.global_file_by_extension_dictionnary:
								self.global_file_by_extension_dictionnary[extension] = {
									"fileSizeAverage":file_size,
									"fileCount":1,
									"fileList": {
										os.path.join(folder,item):file_size,
									}
									}
							else:
								#get the actual file size and create the average value
								file_data = self.global_file_by_extension_dictionnary[extension]
								file_data["fileSizeAverage"] = (file_data["fileSizeAverage"]+file_size)/2
								file_data["fileCount"] = file_data["fileCount"] + 1
								
								
								file_data_list = file_data["fileList"]
								file_data_list[os.path.join(folder,item)] = file_size
								file_data["fileList"] = file_data_list

							
								self.global_file_by_extension_dictionnary[extension] = file_data



							#GET DATA ABOUT DATES
							creation_date,modification_date,time_delta = self.get_date_function(os.path.join(folder,item))
							self.global_file_date_dictionnary[os.path.join(folder,item)] = {
								"timeDelta":time_delta,
								"creationDate":creation_date,
								"modificationDate":modification_date
							}







							#update the global project informations
							self.global_project_size.value += file_size 
							self.global_project_filecount.value += 1
								
								


								



							


						if os.path.isdir(os.path.join(folder, item))==True:
							#self.display_message_function("subfolder added")
							#self.display_message_function(os.path.join(folder,item))
							subfolder_list.append(os.path.join(folder,item))



							#update the global project informations
							self.global_project_foldercount.value += 1

					
					#print(comparison_list)
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



					#COMPARE THE SIZE OF THE FILES COMPARED TO THEIR
					#FILENAME PROXIMITY
					
					files_in_folder_list = list(file_list.keys())
					checked_file = []
					final_dictionnary = {}




					for file in files_in_folder_list:

						if file not in checked_file:
							checked_file.append(file)
							#print(colored("PROXIMITY : %s"%file, "yellow"))

							proxi_list = [(file, os.path.getsize(file))]

							for comparison in files_in_folder_list:
								if comparison not in checked_file:
									if comparison != file:
										value = self.comparison_function(os.path.basename(comparison),os.path.basename(file))

										if value > 85:
											checked_file.append(comparison)
											proxi_list.append((file,os.path.getsize(file)))
							final_dictionnary[len(list(final_dictionnary.keys()))] = proxi_list
							#final_dictionnary[folder] = proxi_list




					#THIS IS THE FUCKING SPEED TEST TEST
					self.speed_test_data = {}
					
					if os.path.isdir(self.temp_path)==False:
						os.makedirs(self.temp_path, exist_ok=True)
					thread_heavy = threading.Thread(target=self.worker_speed_test_function, args=("heavy",self.temp_path,heaviest_filename,), daemon=True)
					thread_light = threading.Thread(target=self.worker_speed_test_function, args=("light",self.temp_path,lightest_filename,), daemon=True)

					thread_heavy.start()
					thread_light.start()

					thread_heavy.join()
					thread_light.join()

					#get the content of the actual speed test delta classement

					self.project_speedtest_classement_heavy[self.speed_test_data["heavy"]["filename"]] = self.speed_test_data["heavy"]["speedTestDelta"]
					"""
					speed_test_filename_list = list(self.project_speedtest_classement_heavy.keys())
					speed_test_size_list = list(self.project_speedtest_classement_heavy.values())

					if self.speed_test_data["heavy"] != None:


						thread_heavy_delta_position = bisect.bisect(speed_test_size_list, self.speed_test_data["heavy"]["speedTestDelta"])
						speed_test_filename_list.insert(thread_heavy_delta_position, self.speed_test_data["heavy"]["filename"])
						speed_test_size_list.insert(thread_heavy_delta_position, self.speed_test_data["heavy"]["speedTestDelta"])

						#save the new dictionnary
						self.project_speedtest_classement_heavy = dict(zip(speed_test_filename_list, speed_test_size_list))
						print("dict size : %s"%len(list(self.project_speedtest_classement_heavy.keys())))
					"""








						

					





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
							"fileBySimilarity":final_dictionnary,
							"speedTest":self.speed_test_data,
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

				
				
	


	