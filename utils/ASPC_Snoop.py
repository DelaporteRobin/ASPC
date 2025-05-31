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
import queue
import zipfile
import rich

from time import sleep
from rich.console import Console
from rich_pyfiglet import RichFiglet

from pathlib import Path
from termcolor import *
from datetime import datetime, timedelta
from config import *

colorama.init()




class ASPC_SNOOP():
	def __init__(self, root_folder, theme_dictionnary):
		
		self.THEME = theme_dictionnary
		#create the rich console
		
		console = Console()
		rich_title_snoop = RichFiglet("ASPC SNOOP", font=ASCII_FONT_HOMEPAGE, colors=[self.THEME.primary, self.THEME.secondary], animation=None, quality=30)
		console.print(rich_title_snoop)
		console.log("[%s]Starting exploring the project : %s"%(self.THEME.primary, root_folder))
		
		#sleep(5)

		#print(colored("ASPC SNOOP", "cyan"))

		if (root_folder == None) or (os.path.isdir(root_folder)==False):
			#print(colored("Project folder is not valid", "red"))
			console.log("[%s]Project folder is not valid"%(self.THEME.error))
			return

		self.root_folder = root_folder


		
		#create multiprocessing manager
		with mp.Manager() as manager:
			self.path = root_folder
			self.queue = mp.Queue()


			#add the root folder in the queue
			self.queue.put(str(root_folder))
			#call the creation of the file queue
			self.create_file_queue_function(console)

			process_number = mp.cpu_count()


			self.data_global = manager.dict()
			self.scan_global_data = manager.dict()
			self.data_folder = manager.dict()
			self.data_extension = manager.dict()
			self.data_file = manager.dict()
			self.data_file_size = manager.list()
			self.data_file_life = manager.list()
			self.data_file_modif = manager.list()
			#self.data_folder_global = manager.dict()

			#create min and max items number
			self.scan_global_data["MIN_ITEMS"] = float("inf")
			self.scan_global_data["MAX_ITEMS"] = float("-inf")


			process_pool = []
			for i in range(process_number):
				try:
					p = mp.Process(target=self.scanning_folder_function, args=(i,))
					p.start()
					process_pool.append(p)
				except Exception as e:
					#print(colored("Impossible to launch process\n%s"%e, "red"))
					console.log("[%s]Impossible to launch process\n%s"%(self.THEME.error,e))
				else:
					#print("Process launched : %s"%str(p))
					console.log("[%s]Process launched → %s"%(self.THEME.primary,p))

			for p in process_pool:
				#print(colored("Process terminated : %s"%str(p), "green"))
				console.log("[%s]Process terminated → %s"%(self.THEME.success, str(p)))
				p.join()

			#print(colored("All processes terminated", "green"))
			console.log("[%s]All processes terminated"%self.THEME.success)



			"""
			create the size classement for folders
			"""


			
			#print(colored("Sort size list", "yellow"))
			print("\n")
			console.log("[%s]Sort size list"%self.THEME.primary)
			self.data_file_size_list = list(self.data_file_size)
			self.data_file_life_list = list(self.data_file_life)
			self.data_file_modif_list = list(self.data_file_modif)
			try:
				self.data_file_size_list.sort(key=lambda x: x[1])
				self.data_file_life_list.sort(key=lambda x: x[1])
				self.data_file_modif_list.sort(key=lambda x: x[1])
			except Exception as e:
				#print(colored("Impossible to sort list\n%s"%e, "red"))
				console.log("[%s]Impossible to sort list\n%s"%(self.THEME.error,traceback.format_exc()))
			else:
				#print(colored("List sorted", "green"))
				console.log("[%s]List sorted"%self.THEME.success)


			self.data_global = {
				"SCAN_DATE":datetime.now().timestamp(),
				"SCAN_GLOBAL_DATA": dict(self.scan_global_data),
				"DATA_FOLDER":dict(self.data_folder),
				"DATA_FILES":dict(self.data_file),
				"DATA_FILE_SIZE":list(self.data_file_size_list),
				"DATA_FILE_LIFE":list(self.data_file_life_list),
				"DATA_FILE_MODIF":list(self.data_file_modif_list),
				"DATA_FILE_EXTENSION":dict(self.data_extension),
				"DATA_ITEM_SIZE":[],
				"DATA_CHILDREN_SIZE":[],
			}


			#print(colored("Create folder size classification", "yellow"))
			print("\n")
			console.log("[%s]Create folder size classification"%self.THEME.primary)
			#create the folder list
			folder_item_size_classification = []
			folder_children_size_classification = []

			try:
				for folder_name, folder_data in self.data_global["DATA_FOLDER"].items():
					#block of instructions for the items contained in folder
					if len(folder_item_size_classification) == 0:
						folder_item_size_classification.append((folder_name, folder_data["ITEMS_SIZE"]))
					else:
						bisect.insort(folder_item_size_classification, (folder_name, folder_data["ITEMS_SIZE"]), key=lambda x: x[1])

					
					#block of instructions for children contained in the folder
					if len(folder_children_size_classification) == 0:
						folder_children_size_classification.append((folder_name, folder_data["CHILDREN_SIZE"]))
					else:
						bisect.insort(folder_children_size_classification, (folder_name, folder_data["CHILDREN_SIZE"]), key=lambda x: x[1])

				#insert values in the final dictionnary
				self.data_global["DATA_ITEM_SIZE"] = folder_item_size_classification
				self.data_global["DATA_CHILDREN_SIZE"] = folder_children_size_classification
			except Exception as e:
				console.log("[%s]Impossible to create folder size classification\n%s"%(self.THEME.error,traceback.format_exc()))
				#print(colored("Impossible to create folder size classification","red"))
				#print(colored(e, "red"))
			else:
				#print(colored("Folder classification done", "green"))
				console.log("[%s]Folder classification done"%self.THEME.success)






			#print(colored("Replace all Path elements", "yellow"))
			print("\n")
			console.log("[%s]Replace all path elements"%self.THEME.primary)
			try:
				self.data_global = {k: str(v) if isinstance(v, Path) else v for k, v in self.data_global.items()}
			except Exception as e:
				#print(colored("Impossible to clean path elements\n%s"%traceback.format_exc(), "red"))
				console.log("[%s]Impossible to clean path elements\n%s"%(self.THEME.error,traceback.format_exc()))
			else:
				#print(colored("All path elements replaced", "green"))
				console.log("[%s]All path elements replaced"%self.THEME.success)


			
			archive_path = None
			archive_log = None
			
			if os.path.isfile(os.path.join(os.getcwd(), "data/data.json"))==True:
				#load the content file
				with open(os.path.join(os.getcwd(), "data/data.json"), "r") as read_file:
					content = json.load(read_file)
				#check if the project is already writen in the archive
				if str(root_folder) in content:
					if ("ARCHIVE_PATH" in content[str(root_folder)]) and ("ARCHIVE_LOG" in content[str(root_folder)]):
						archive_path = content[str(root_folder)]["ARCHIVE_PATH"]
						archive_log = content[str(root_folder)]["ARCHIVE_LOG"]
			
			else:
				content = {}

			print("\n")
			content[str(root_folder)] = self.data_global
			#if archive path and log different from None
			#recreate the archive path in the dictionnary
			if (archive_path != None) and (archive_log != None):
				content[str(root_folder)]["ARCHIVE_PATH"] = archive_path
				content[str(root_folder)]["ARCHIVE_LOG"] = archive_log
				#print(colored("Archive path and log detected for project", "cyan"))
				console.log("[%s]Archive path and log detected in this project"%self.THEME.accent)

				#reinject archived elements in data folder
				#try to open the archive
				#print(colored("Try to inject archived content", "cyan"))
				console.log("[%s]Try to inject archived content"%self.THEME.primary)
				try:
					with zipfile.ZipFile(content[str(root_folder)]["ARCHIVE_PATH"], mode="r") as archive:
						for file in archive.infolist():
							filepath=file.filename
							#print("\tinjecting %s"%os.path.basename(filepath))
							console.log("[%s]Injecting : %s"%(self.THEME.foreground,os.path.basename(filepath)))
							filefolder=os.path.join(root_folder,os.path.dirname(filepath)).replace("/", "\\")
							#get the folder dictionnary
							if "ARCHIVED_LIST" not in content[str(root_folder)]["DATA_FOLDER"][filefolder]:
								content[str(root_folder)]["DATA_FOLDER"][filefolder]["ARCHIVED_LIST"] = []
							content[str(root_folder)]["DATA_FOLDER"][filefolder]["ARCHIVED_LIST"].append(os.path.basename(filepath))
				except Exception as e:
					#print(colored("Impossible to inject archived elements", "red"))
					#print(colored(traceback.format_exc(), "red"))
					console.log("[%s]Impossible to inject archived elements\n%s"%(self.THEME.error,traceback.format_exc()))




			try:
				with open(os.path.join(os.getcwd(), "data/data.json"), "w") as save_file:
					json.dump(content, save_file, indent=4)
			except Exception as e:
				#print(colored("Failed to save dictionnary\n%s"%traceback.format_exc(), "red"))
				console.log("[%s]Failed to save dictionnary\n%s"%(self.THEME.error, traceback.format_exc()))
			else:
				#print(colored("Dictionnary saved", "green"))
				console.log("[%s]Dictionnary saved"%self.THEME.success)




	def create_file_queue_function(self,console):
		#print(colored("STARTING TO CREATE THE FILE QUEUE", "magenta"))
		console.log("[%s]Starting to create the file queue"%self.THEME.primary)

		for root, dirs, files in scandir.walk(self.path):
			for d in dirs:
				try:
					self.queue.put(os.path.join(root, d))
				except Exception as e:
					#print(colored("Impossible to add folder in queue\n%s"%e, "red"))
					console.log("[%s]Impossible to add folder in queue\n%s"%(self.THEME.error,traceback.format_exc()))
				else:
					#print(colored("Folder added in queue : %s"%d))
					console.log("[%s]Folder added in queue : %s"%(self.THEME.foreground,d))




	def scanning_folder_function(self, index):
		while True:
			try:
				folder = self.queue.get(timeout=5)

				if folder == None:
					print(colored("\tProcess broken [%s]"%i))
					break

				else:
					print(colored("\t[%s] Checking folder : %s"%(index, folder)))


					folder_content = os.listdir(folder)
					#print(folder_content)

					#check if the folder is already in the folder dictionnay
					if folder not in self.data_folder:


						#adapt the value of the min and max items values
						if len(folder_content) > self.scan_global_data["MAX_ITEMS"]:
							self.scan_global_data["MAX_ITEMS"] = len(folder_content)
						if len(folder_content) < self.scan_global_data["MIN_ITEMS"]:
							self.scan_global_data["MIN_ITEMS"] = len(folder_content)


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

	

					sim_checked = []
					for item in folder_content:
						print("\t	checking item in folder : %s ; %s"%(item , os.path.isfile(os.path.join(folder,item))))
						if os.path.isfile(os.path.join(folder,item))==True:
							#get informations about the file
							file_size = os.path.getsize(os.path.join(folder,item))
							file_creation = datetime.fromtimestamp(os.path.getctime(os.path.join(folder,item))).strftime("%Y-%m-%d %H:%M:%S")
							file_modification = datetime.fromtimestamp(os.path.getmtime(os.path.join(folder,item))).strftime("%Y-%m-%d %H:%M:%S")


							#update the extension dictionnary
							file_extension = os.path.splitext(item)[1]
							#check if the key exists in dictionnary
							if file_extension not in self.data_extension:
								self.data_extension[file_extension] = {
									"COUNT":0,
									"FILE_LIST":[],
									"SIZE":0
								}
							#update values with the current file
							extension_data = self.data_extension[file_extension]
							extension_data["COUNT"]+=1
							extension_data["FILE_LIST"].append(os.path.join(folder,item))
							extension_data["SIZE"]+=file_size
							#update the new dictionnary
							self.data_extension[file_extension] = extension_data
							
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

							#create the file dictionnary
							self.data_file[os.path.join(folder,item)] = {
								"FILESIZE":file_size,
								"FILECREATION":file_creation,
								"FILEMODIFICATION":file_modification,
							}


							#get the similarity dictionnary for the folder
							sim_dict = folder_data["SIMILARITY"]
							file_dict = self.data_file[os.path.join(folder,item)]

							if sim_dict == {}:
								sim_dict[item] = [item]
								file_dict["SIMKEY"] = item
								sim_checked.append(item)

							else:
								added = False
								for sim_key, sim_data in sim_dict.items():
									ratio = Levenshtein.ratio(os.path.splitext(sim_key)[0],os.path.splitext(item)[0])

									#ADD THE FILE TO THIS SIMILARITY KEY!
									if ratio > 0.9:
										sim_data.append(item)
										sim_dict[sim_key] = sim_data
										added=True

										#when adding a file to folder data dictionnary
										#create also a data in file data dictionnary
										file_dict["SIMKEY"] = sim_key
										break

								if added == False:
									sim_dict[item] = [item]
									file_dict["SIMKEY"] = item

							file_dict["SIMPARENT"] = folder
							self.data_file[os.path.join(folder,item)] = file_dict

							"""	
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
							"""



							#UPDATE THE PARENT FOLDER SIZE			
							parent_folder = folder 

							while True:
								#print("\tparent [%s] -> %s"%(parent_folder,os.path.join(folder,item)))
								#update the size
								try:
									parent_folder_data = self.data_folder[str(parent_folder)]
									children_size = parent_folder_data["CHILDREN_SIZE"]
									parent_folder_data["CHILDREN_SIZE"] += file_size
									self.data_folder[str(parent_folder)] = parent_folder_data
								except KeyError:
									break
									#pass
								except Exception as e:
									print(colored("\tImpossible to update parent : %s\n%s"%(item,traceback.format_exc()), "red"))
									break

								if parent_folder == self.root_folder:
									break
								else:
									parent_folder = Path(parent_folder).parent





							if os.path.isdir(os.path.join(folder,item))==True:
								folder_data["FOLDER_COUNT"] += 1

							
							#add the similarity back in dictionnary
							folder_data["SIMILARITY"] = sim_dict				
							#update the value of the global dictionnary						
							self.data_folder[folder] = folder_data
									
	

			except queue.Empty:
				return

			except Exception as e:
				#print(colored(e, "red"))
				print(colored("\t%s"%traceback.format_exc(), "red"))
				return
