# -*- coding: utf-8 -*-
import os
import scandir
import multiprocessing as mp
import json
import pickle
import sys
import pyfiglet
import colorama
import Levenshtein
import bisect
import heapq
import traceback

from pathlib import Path
from termcolor import *
from datetime import datetime, timedelta

colorama.init()




class ASPC_SNOOP():
	def __init__(self, root_folder):
		


		print(colored("ASPC SNOOP", "cyan"))
		print("Exploring : %s"%root_folder)

		if (root_folder == None) or (os.path.isdir(root_folder)==False):
			print(colored("Project folder is not valid", "red"))
			return

		self.root_folder = root_folder

		
		#create multiprocessing manager
		with mp.Manager() as manager:
			self.path = root_folder
			self.queue = mp.Queue()


			#add the root folder in the queue
			self.queue.put(str(root_folder))
			#call the creation of the file queue
			self.create_file_queue_function()

			process_number = mp.cpu_count()


			self.data_global = manager.dict()
			self.data_folder = manager.dict()
			self.data_file = manager.dict()
			self.data_file_size = manager.list()
			self.data_file_life = manager.list()
			self.data_file_modif = manager.list()


			process_pool = []
			for i in range(process_number):
				try:
					p = mp.Process(target=self.scanning_folder_function, args=(i,))
					p.start()
					process_pool.append(p)
				except Exception as e:
					print(colored("Impossible to launch process\n%s"%e, "red"))
				else:
					print("Process launched : %s"%str(p))

			for p in process_pool:
				print(colored("Process terminated : %s"%str(p), "green"))
				p.join()

			print(colored("All processes terminated", "green"))


			
			print(colored("Sort size list", "yellow"))
			self.data_file_size_list = list(self.data_file_size)
			self.data_file_life_list = list(self.data_file_life)
			self.data_file_modif_list = list(self.data_file_modif)
			try:
				self.data_file_size_list.sort(key=lambda x: x[1])
				self.data_file_life_list.sort(key=lambda x: x[1])
				self.data_file_modif_list.sort(key=lambda x: x[1])
			except Exception as e:
				print(colored("Impossible to sort list\n%s"%e, "red"))
			else:
				print(colored("List sorted", "green"))


			self.data_global = {
				"SCAN_DATE":datetime.now().timestamp(),
				"DATA_FOLDER":dict(self.data_folder),
				"DATA_FILES":dict(self.data_file),
				"DATA_FILE_SIZE":list(self.data_file_size_list),
				"DATA_FILE_LIFE":list(self.data_file_life_list),
				"DATA_FILE_MODIF":list(self.data_file_modif_list)
			}



			print(colored("Replace all Path elements", "yellow"))
			try:
				self.data_global = {k: str(v) if isinstance(v, Path) else v for k, v in self.data_global.items()}
			except Exception as e:
				print(colored("Impossible to clean path elements\n%s"%traceback.format_exc(), "red"))
			else:
				print(colored("All path elements replaced", "green"))



			if os.path.isfile(os.path.join(os.getcwd(), "data/data.json"))==True:
				#load the content file
				with open(os.path.join(os.getcwd(), "data/data.json"), "r") as read_file:
					content = json.load(read_file)
			else:
				content = {}

			content[str(root_folder)] = self.data_global

			with open(os.path.join(os.getcwd(), "data/data.json"), "w") as save_file:
				json.dump(content, save_file, indent=4)


		






	def create_file_queue_function(self):
		print(colored("STARTING TO CREATE THE FILE QUEUE", "magenta"))

		for root, dirs, files in scandir.walk(self.path):
			for d in dirs:
				try:
					self.queue.put(os.path.join(root, d))
				except Exception as e:
					print(colored("Impossible to add folder in queue\n%s"%e, "red"))






	def scanning_folder_function(self, index):
		while True:
			try:
				folder = self.queue.get(timeout=5)

				if folder == None:
					print(colored("Process broken [%s]"%i))
					break

				else:
					print(colored("[%s] Checking folder : %s"%(index, folder)))


					folder_content = os.listdir(folder)

					#check if the folder is already in the folder dictionnay
					if folder not in self.data_folder:

						#get the folder content size 
						self.data_folder[folder] = {
							"ITEMS_LIST":folder_content,
							"ITEMS_NUMBER":len(folder_content),
							"FILE_LIST":[],
							"FOLDER_LIST":[],
							"ITEMS_SIZE":0,
							"CHILDREN_SIZE":0,
							"FILE_COUNT":0,
							"SIMILARITY": {},
							"FOLDER_COUNT":0,
						}
						file_list = []
						folder_list = []

						heaviest_file = float("-inf")
						lightest_file = float("inf")

						for item in folder_content:
							if os.path.isfile(os.path.join(folder,item)):
								file_size = os.path.getsize(os.path.join(folder,item))
								file_list.append(item)

								#check heaviest and lightest file
								if type(heaviest_file) == float:
									if file_size > heaviest_file:
										heaviest_file = os.path.join(folder,item)
								if type(heaviest_file) == str:
									if file_size > os.path.getsize(heaviest_file):
										heaviest_file = os.path.join(folder,item)

								if type(lightest_file) == float:
									if file_size < lightest_file:
										lightest_file = os.path.join(folder,item)
								if type(lightest_file) == str:
									if file_size < os.path.getsize(lightest_file):
										lightest_file = os.path.join(folder,item)



							if os.path.isdir(os.path.join(folder,item)):
								folder_list.append(item)

						data_folder = self.data_folder[folder]
						data_folder["FILE_LIST"] = file_list 
						data_folder["FOLDER_LIST"] = folder_list
						data_folder["HEAVIEST_FILE"] = heaviest_file
						data_folder["LIGHTEST_FILE"] = lightest_file


						

						
						self.data_folder[folder] = data_folder





					for item in folder_content:
						if os.path.isfile(os.path.join(folder,item))==True:
							#get informations about the file
							file_size = os.path.getsize(os.path.join(folder,item))
							file_creation = datetime.fromtimestamp(os.path.getctime(os.path.join(folder,item))).strftime("%Y-%m-%d %H:%M:%S")
							file_modification = datetime.fromtimestamp(os.path.getmtime(os.path.join(folder,item))).strftime("%Y-%m-%d %H:%M:%S")


							

							#and lightest file

							#update dictionnary about file size
							self.data_file_size.append((os.path.join(folder,item), file_size))
							self.data_file_life.append((os.path.join(folder,item), datetime.now().timestamp() - os.path.getctime(os.path.join(folder,item))))
							self.data_file_modif.append((os.path.join(folder,item), datetime.now().timestamp() - os.path.getmtime(os.path.join(folder,item))))



							#update the value for the parent folder size
							folder_data = self.data_folder[folder]
							folder_data["ITEMS_SIZE"] += file_size
							#update the filecount in folder data
							folder_data["FILE_COUNT"] += 1







							#get the similarity dictionnary for the folder
							similarity_dictionnary = folder_data["SIMILARITY"]




							#starting to create the similarity dictionnary
							if similarity_dictionnary == {}:
								similarity_dictionnary[item] = [item]
							else:
								found=False
								for similarity_key in list(similarity_dictionnary.keys()):
									#get the levenshtein distance
									distance = Levenshtein.distance(item, similarity_key)
									max_l = max(len(item), len(similarity_key))
									sim = (1 - distance / max_l) * 100

									if sim > 80:
										#add the file to the similarity list for this key
										sim_data = similarity_dictionnary[similarity_key]
										#print(sim_data)
										sim_data.append(item)
										similarity_dictionnary[similarity_key] = sim_data

								if found == False:
									similarity_dictionnary[item] = [item]

						



							self.data_file[os.path.join(folder,item)] = {
								"FILESIZE":file_size,
								"FILECREATION":file_creation,
								"FILEMODIFICATION":file_modification,
							}

							#update all the parent folder size in dictionnary
							parent_folder = folder

							if parent_folder != self.root_folder:
								while True:
									parent_folder = Path(parent_folder).parent
									if parent_folder == self.root_folder:
										break
									else:

										#print("%s parent for folder %s : %s"%(str(parent_folder) in self.data_folder, folder, parent_folder))
										#add the file size to each parent
										try:
											parent_folder_data = self.data_folder[str(parent_folder)]
											children_size = parent_folder_data["CHILDREN_SIZE"]
											parent_folder_data["CHILDREN_SIZE"] = children_size + file_size
											self.data_folder[str(parent_folder)] = parent_folder_data
										except Exception as e:
											print(colored("Impossible to update parent : %s"%e))
											break

							if os.path.isdir(os.path.join(folder,item))==True:
								folder_data["FOLDER_COUNT"] += 1

							
							#add the similarity back in dictionnary
							folder_data["SIMILARITY"] = similarity_dictionnary				
							#update the value of the global dictionnary						
							self.data_folder[folder] = folder_data
									





					



			except Exception as e:
				print(colored(e, "red"))
				print(colored(traceback.format_exc(), "red"))
				return
				