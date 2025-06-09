# -*- coding: utf-8 -*-


from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
#from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen, ModalScreen
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on
from termcolor import *

from utils.ASPC_Widgets import MultiListView, MultiListItem
from utils.ASPC_Utils import ASPC_UTILS
from utils.ASPC_Snoop import ASPC_SNOOP

import shutil
import colorama
import os
import json
import traceback
import copy
import multiprocessing as mp
import threading
import queue
import zipfile
import ruamel.std.zipfile as zipdel
import pyfiglet
import rich

from rich.console import Console
from rich_pyfiglet import RichFiglet
from config import *

from datetime import datetime
from pathlib import Path
from time import sleep



colorama.init()





class ASPC_ARCHIVE_MULTIPROCESSING:
	def __init__(self, filter_dictionnary, origin_file_list, current_project_data):
		
		#check if similarity is enabled
		#if yes create the new file list
		if filter_dictionnary["FilterBySimilarity"]==True:

			print(colored("Checking similarity", "magenta"))

			new_file_list = []

			for i in range(len(origin_file_list)):
				if origin_file_list[i] not in new_file_list:
					#get the similarity list for this file
					sim_key = current_project_data["DATA_FILES"][origin_file_list[i]]["SIMKEY"]
					sim_parent = current_project_data["DATA_FILES"][origin_file_list[i]]["SIMPARENT"]

					#get the similarity list in the current project data
					try:
						sim_list = current_project_data["DATA_FOLDER"][sim_parent]["SIMILARITY"][sim_key]
					except Exception as e:
						print(colored("Impossible to get similarity data for this file : %s"%origin_file_list[i], "red"))
					else:
						#check if the sim list is big enough
						#if yes add each file from that list in the new_file_list
						if len(sim_list) >= int(filter_dictionnary["FilterSimilarityNumber"]):
							for f in sim_list:
								f = os.path.join(sim_parent,f)
								if f not in new_file_list:
									#print(colored("File added : %s"%f, "white"))
									new_file_list.append(f)

				else:
					print(colored("File skipped because already added in list : %s"%origin_file_list[i], "yellow"))
			origin_file_list = new_file_list

			print(colored("\nDone checking similarity", "green"))
			print("Origin file list replaced")

		#create self variables
		self.filter_dictionnary = filter_dictionnary
		self.current_project_data = current_project_data
		


		#multiprocessing manager
		with mp.Manager() as manager:
		
			#create the file queue
			self.file_queue = mp.Queue()
			for f in origin_file_list:
				self.file_queue.put(f)
	
			#define the multiprocessing shared variables
			self.final_filtered_list = manager.list()

			#launch multiprocessing
			process_pool = []
			#define the process number
			process_number = 5
			for i in range(process_number):
				try:
					x = mp.Process(target=self.filter_worker_function, args=(i,))
					x.start()
				except:
					print(colored("Impossile to launch process\n%s"%traceback.format_exc(), "red"))
				else:
					process_pool.append(x)
					print(colored("Process launched", "green"))


			for process in process_pool:
				process.join()
				print(colored("Process terminated : %s"%process, "yellow"))



			print("\n\nFiltered file list:")
			for file in self.final_filtered_list:
				print("%s"%file)


			try:
				with open("data/temp_filtered.dll", "w") as save_file:
					json.dump(list(self.final_filtered_list), save_file, indent=4)
			except Exception as e:
				print(colored("Impossible to save file\n%s"%traceback.format_exc(), "red"))
			else:
				print(colored("Filtered list saved", "green"))



	#FILTER FILE PROCESS
	def filter_worker_function(self,i):
		while True:
			try:
				file = self.file_queue.get(timeout=3)
				if file == None:
					break

				else:
					#print("\t[%s] -> %s"%(i,file))
					#APPLY FILTER ON THE GIVEN FILE

					value = True


					#FILTER SIZE
					if self.filter_dictionnary["FilterBySize"]==True:
						#get the size of the given file
						filesize = self.current_project_data["DATA_FILES"][file]["FILESIZE"] / (1024*1024)
						#check if the given filesize is superior to min size and inferior to max size
						#if max size == 0 convert it to inf
						min_value = int(self.filter_dictionnary["FilterMinSize"])
						if int(self.filter_dictionnary["FilterMaxSize"])==0:
							max_value = float("inf")
						else:
							max_value = int(self.filter_dictionnary["FilterMaxSize"])

						#print("%s ; %s ; %s"%(min_value,filesize,max_value))
						if (filesize < min_value) or (filesize > max_value):
							value=False


					#FILTER EXTENSION
					if self.filter_dictionnary["FilterByExtension"]==True:
						if os.path.splitext(file)[1] not in self.filter_dictionnary["FilterExtensionList"]:
							value=False


					#FILTER EXCLUDE KEYWORDS
					if self.filter_dictionnary["FilterKeywordExclude"]==True:
						for keyword in self.filter_dictionnary["FilterKeywordListExcluse"]:
							if keyword in os.path.splitext(os.path.basename(file))[0]:
								value=False
								break


					#FILTER KEYWORD
					if self.filter_dictionnary["FilterByKeyword"]==True:
						#ALL KEYWORDS MUST BE IN THE FILENAME
						if self.filter_dictionnary["FilterKeywordAbsolute"]==True:
							validated=True
							for keyword in self.filter_dictionnary["FilterKeywordList"]:
								if keyword not in os.path.splitext(os.path.basename(file))[0]:
									validated=False
									break
						

						#ONLY ONE KEYWORD NEEDS TO BE IN THE FILENAME
						else:
							validated=False
							for keyword in self.filter_dictionnary["FilterKeywordList"]:
								if keyword in os.path.splitext(os.path.basename(file))[0]:
									validated=True
									break

						value=validated





					if value == True:
						print(colored("True : %s"%file, "green"))

						if file not in self.final_filtered_list:
							self.final_filtered_list.append(file)
						else:
							print(colored("File skipped because already added", "yellow"))
					else:
						print(colored("False : %s"%file, "red"))



			except mp.queues.Empty:
					print(colored("process done", "red"))
					return

			except Exception as e:
				print(colored(traceback.format_exc(), "red"))
				return





class ASPC_FILL_ARCHIVE(ASPC_UTILS, ASPC_SNOOP):
	def __init__(self, theme_dictionnary, selection_to_archive, current_project, project_data, method = zipfile.ZIP_LZMA, overhead_checking=True, update_data=True):

		self.THEME = theme_dictionnary
		#console = Console()

		self.current_project = current_project 
		self.selection_to_archive = selection_to_archive
		self.current_project_data = project_data[current_project]
		self.project_data = project_data
		self.method = method
		self.overhead_checking=overhead_checking
		self.update_data = update_data

		
		#print(colored("\n\n\n%s"%pyfiglet.figlet_format("ARCHIVING PROCESS", font="the_edge"), "cyan"))
		#self.run(selection_to_archive, current_project, current_project_data)

	def run(self):

		console = Console()
		rich_title_archiving = RichFiglet("ARCHIVING PROCESS", font=ASCII_FONT_HOMEPAGE, colors=[self.THEME.primary, self.THEME.background], animation=None,quality=40)
		console.print(rich_title_archiving)
		console.log("[%s]Starting archiving process"%self.THEME.primary)
		"""
		check if the path of the archive is defined
		check if the path of the archive exists (create it if not)
		check the lengh of the selection to archive
		"""
		print("Current project selected : %s"%self.current_project)

		try:
			print("Archive path : %s"%self.current_project_data["ARCHIVE_PATH"])
		except KeyError:
			#print(colored("Path of the archive is not defined!", "red"))
			console.log("[%s]Path of the archive is not defined"%self.THEME.error)
			
		if os.path.isdir(os.path.dirname(self.current_project_data["ARCHIVE_PATH"]))==False:
			#print(colored("Path to archive isn't valid", "yellow"))
			console.log("[%s]Path to archive isn't valid"%self.THEME.warning)

			try:
				os.makedirs(os.path.dirname(self.current_project_data["ARCHIVE_PATH"]), exist_ok=True)
			except Exception as e:
				#print(colored("Impossible to create path to archive", "red"))
				#print(colored(traceback.format_exc(), "red"))
				console.log("[%s]Impossible to create path to archive\n%s"%(self.THEME.error, traceback.format_exc()))
				return
			else:
				#print(colored("Path to archive created", "green"))
				console.log("[%s]Path to archive created"%self.THEME.success)

		if len(self.selection_to_archive) == 0:
			#print(colored("No elements to archive!", "red"))
			console.log("[%s]No elements to archive"%self.THEME.error)
			return


		#os.system("pause")
		#return
		#create the multiprocessing manager
		with mp.Manager() as manager:

			folder_counter = 0 
			file_counter = 0 

			#print(colored("Creating the file queue ...", "cyan"))
			console.log("[%s]Creating the file queue ..."%self.THEME.primary)
			#create the filequeue for the multiprocesses
			self.file_queue = mp.Queue()



			self.archive_log = {}
			#create the dataset dictionnary
			self.archive_dataset = manager.dict()
			"""
			INFORMATIONS TO GATHER
			content to archive size (before archiving and after)
			size of the project (before archiving and after)
			archive size (before archiving and after)
			"""
			#add original size of the project
			self.archive_dataset["PROJECTSIZE_BEFORE"] = self.current_project_data["DATA_FOLDER"][self.current_project]["CHILDREN_SIZE"]
			self.archive_dataset["PROJECTSIZE_AFTER"] = 0
			self.archive_dataset["CONTENTSIZE_BEFORE"] = 0
			self.archive_dataset["CCONTENTSIZE_AFTER"] = 0
			self.archive_dataset["ARCHIVESIZE_BEFORE"] = 0
			self.archive_dataset["ARCHIVESIZE_AFTER"] = 0



			#CHECK IF THE ARCHIVE ALREADY EXISTS
			self.project_archive_content = []
			if os.path.isfile(self.current_project_data["ARCHIVE_PATH"])==True:

				#get the size of the current archive
				self.archive_dataset["ARCHIVESIZE_BEFORE"] = os.path.getsize(self.current_project_data["ARCHIVE_PATH"])

				#get the content of the archive
				#print(colored("Trying to get the content of the existing project archive...", "cyan"))
				console.log("[%s]Trying to get the content of the existing project archive"%self.THEME.primary)
				try:
					with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], mode="r") as read_archive:
						for file in read_archive.namelist():
							self.project_archive_content.append(Path(file))
				except Exception as e:
					#print(colored("Impossible to get the content of the existing project archive", "red"))
					console.log("[%s]Impossible to get the content of the existing project archive"%self.THEME.error)
				else:
					#print(colored("Existing archive content retrieved", "green"))
					console.log("[%s]Existing archive content retrieved"%self.THEME.success)

				#checking if the archive log exists as well
				if os.path.isfile(self.current_project_data["ARCHIVE_LOG"])==True:
					#print(colored("Archive log detected", "green"))
					console.log("[%s]Archive log detected"%self.THEME.success)

					#try to read the content of the archive log
					try:
						with open(self.current_project_data["ARCHIVE_LOG"], "r") as read_file:
							self.archive_log = json.load(read_file)
					except Exception as e:
						#print(colored("Impossible to read archive log content!\n%s"%traceback.format_exc(), "red"))
						console.log("[%s]Impossible to read archive log content\n%s"%(self.THEME.error, traceback.format_exc()))
					else:
						console.log("[%s]Archive log content retrieved successfully"%self.THEME.success)
						#print(colored("Archive log content retrieved successfully!", "green"))

				else:
					console.log("[%s]Impossible to find archive log"%self.THEME.error)
					#print(colored("Impossible to find archive log", "red"))




			#convert the dictionnary log into a manager dict
			self.archive_log = manager.dict(self.archive_log)

			for element in self.selection_to_archive:
				if os.path.isdir(element) == True:
					"""
					folder_counter += 1
					self.file_queue.put(element)
					"""
					#add all files contained in the folder
					console.log("[%s]\tExploring folder to find files to archive : %s"%(self.THEME.primary,element))
					for root, dirs, files in os.walk(element):
						#check if the file is not already in archive
						for f in files:
							filepath = os.path.join(root,f)
							relative_filepath = Path(filepath).relative_to(Path(self.current_project))

							if Path(relative_filepath) not in self.project_archive_content:
								file_counter+=1
								self.file_queue.put(filepath)
							else:
								console.log("[%s]\tFile skipped because already archived"%self.THEME.warning)
						self.file_queue.put(os.path.join(root, f))

				elif (os.path.isfile(element) == True):

					#check if the file is not already archived
					relative_filepath = Path(element).relative_to(Path(self.current_project))
					print("\t%s"%relative_filepath)

					if Path(relative_filepath) not in self.project_archive_content:
						file_counter += 1 
						self.file_queue.put(element)
					else:
						console.log("[%s]\t→ File skipped because already archived"%self.THEME.warning)
						#print(colored("\t-> File skipped because already archived", "yellow"))
				else:
					console.log("[%s]Item to archive : %s"%(self.THEME.error,element))
					#print(colored("Item not existing : %s"%element, "red"))
					continue 
				

			#print("FILE QUEUE SIZE : %s"%self.file_queue.qsize())
			console.log("[%s]File queue size"%self.THEME.primary)
			if self.file_queue.empty()==True:
				#print(colored("The file queue to archive is empty\nArchiving process stopped", "red"))
				console.log("The file queue to archive is empty\nArchiving process stopped"%self.THEME.error)
				return


			#open the zipfile manager for archive
			try:
				#print(colored("\nOpening archive...\nReady to archive", "cyan"))
				console.log("[%s]Opening archive...\nReady to archive"%self.THEME.primary)
				#with zipfile.ZipFile(current_project_data["ARCHIVE_PATH"], mode="a",compression=zipfile.ZIP_LZMA, compresslevel=9) as self.archive:


				self.ns = manager.Namespace()
				self.ns.global_count = 0
				self.ns.total_count = folder_counter + file_counter
				self.shared_current_project_data = manager.dict(self.current_project_data)
				self.new_archived_file_list = manager.list()
				#convert current project data as mp dictionnary
				#self.mp_current_project_data = manager.dict

				#create multiprocesses
				#CREATE TEMP ARCHIVE PROCESS
				process_pool = []
				temp_archive_list = []
				for i in range(mp.cpu_count()):
					temp_archive_name = os.path.join(os.path.dirname(self.current_project_data["ARCHIVE_PATH"]),"tempArchive_%s_%s.zip"%(os.path.basename(self.current_project),i))
					p = mp.Process(target=self.archive_item_worker,args=(i, temp_archive_name,self.current_project_data["ARCHIVE_PATH"], self.current_project, zipfile.ZIP_LZMA, self.overhead_checking, self.update_data))
					p.start()
					process_pool.append(p)
					temp_archive_list.append(temp_archive_name)
					#print("\t[%s] Process launched"%i)
					console.log("[%s]Process launched"%self.THEME.accent)


				for i in range(len(process_pool)):
					#print(colored("Process terminated : %s"%process_pool[i], "green"))
					console.log("[%s]Process terminated : %s"%(self.THEME.success, process_pool[i]))
					process_pool[i].join()



				#CONVERT BACK THE CURRENT PROJECT DATA
				self.current_project_data = dict(self.shared_current_project_data)
				#udpate the global project data dictionnary
				self.project_data[self.current_project] = self.current_project_data 
				#save the global project data dictionnary in file
				self.save_dictionnary_function()



				#MERGING ALL ARCHIVES
				#print(colored("\nMerging TEMP archives ...", "cyan"))
				console.log("[%s]Starting to merge TEMP archives..."%self.THEME.primary)

				#self.archive_stored_filelist = []
				#with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], "a", compression=self.method, compresslevel=9) as final_archive:
				for temp_archive in temp_archive_list:
					print("\n\t%s"%temp_archive)
					try:
						with zipfile.ZipFile(temp_archive, "r") as read_temp_archive:
							for info in read_temp_archive.infolist():
								print("\t\treading %s"%info.filename)
								try:
									with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], "a", compression=self.method, compresslevel=9) as final_archive:
										with read_temp_archive.open(info) as writer:
											final_archive.writestr(info, writer.read())
										
								except Exception as e:
									#try to open the archive as stored (no compression applied)
									with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], "a", compression=zipfile.ZIP_STORED) as final_archive:
										with read_temp_archive.open(info) as writer:
											final_archive.writestr(info, writer.read())

					except FileNotFoundError:
						#print(colored("\tTemp archive not existing", "red"))
						console.log("[%s]Temp archive not existing"%self.THEME.error)
					#remove the temp archive
					try:
						os.remove(temp_archive)
					except Exception as e:
						#print(colored("\tImpossible to remove archive", "red"))
						console.log("[%s]Impossible to remove archive"%self.THEME.error)
					else:
						#print(colored("\tArchive removed successfully", "green"))
						console.log("[%s]Archive removed successfully"%self.THEME.error)



					#GET DATA ABOUT NEW COMPRESSED FILES
					#print(colored("\nGetting data about new files in archive ...", "cyan"))
					console.log("[%s]Getting data about new files in archive"%self.THEME.primary)
					for filepath, filedata in self.archive_log.items():
						try:
							#get the path in archive
							file_archivepath = filedata["ARCHIVEPATH"].replace("\\", "/")
							#get info in zipfile
							file_archiveinfo = final_archive.getinfo(file_archivepath)
							#get size informations for each file and update the dictionnary
							self.archive_log[filepath]["ARCHIVE_FILESIZE"] = file_archiveinfo.file_size
							self.archive_log[filepath]["ARCHIVE_COMPRESSSIZE"] = file_archiveinfo.compress_size
							self.archive_dataset["CCONTENTSIZE_AFTER"] += file_archiveinfo.compress_size
							#print("%s\n\t%s\n\t%s"%(file_archivepath, file_archiveinfo.file_size, file_archiveinfo.compress_size))
						except Exception as e:
							#print(colored("Impossible to get data about %s"%filepath))
							console.log("[%s]Impossible to get data about %s"%(self.THEME.error,filepath))
					#print(colored("Informations from archive updated", "green"))
					console.log("[%s]Informations from archive updated"%self.THEME.accent)




				#read the content of the final archive writen
				#get the final filelist
				with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], "r") as read_final_archive:
					archive_final_filelist = read_final_archive.namelist()
					for i in range(len(archive_final_filelist)):
						archive_final_filelist[i] = os.path.normpath(archive_final_filelist[i])
						

				#REMOVING FILES FROM PROJECT
				#print(colored("Removing files from project after archiving...", "cyan"))
				console.log("[%s]Removing files from project after archiving..."%self.THEME.primary)
				for file in self.selection_to_archive:
					#check if the file is in the archive before removing it from project
					archive_filepath = os.path.normpath(str(Path(file).relative_to(Path(self.current_project))))
					if archive_filepath in archive_final_filelist:
						try:
							os.remove(file)
						except Exception as e:
							#print(colored("\tfailed to delete : %s"%file, "red"))
							console.log("[%s]Failed to delete file : %s"%(self.THEME.error, file))
						else:
							console.log("[%s]File removed")
							#print(colored("\tfile removed : %s"%file))
					else:
						console.log("[%s]Impossible to find file in archive : %s\nThe file was not removed from the original project"%(self.THEME.error,archive_filepath))
						#print(colored("\tImpossible to find file in archive : %s"%archive_filepath, "red"))
						#print(colored("\tThe file was not removed from the original project!"))
				#print(colored("Removing files from project terminated", "cyan"))
				console.log("[%s]Removing files from project terminated"%self.THEME.success)


				#os.system("pause")


				#UPDATE THE DATA FILE FOR THIS PROJECT
				#AFTER REMOVING ALL FILES
				#create instance of the class
				"""
				print(colored("\n\nScanning the project to gather new informations...\nCalling the scanning class...", "cyan"))
				try:
					ASPC_SNOOP(self.current_project)
					self.load_project_data_function()
					self.current_project_data = self.project_data[self.current_project]
				except Exception as e:
					print(colored("\n\nFatal error happened while scanning project\nImpossible to update project informations\n%s"%traceback.format_exc(), "red"))
				else:
					print(colored("\n\nProject scan terminated\nNew informations saved", "green"))
				"""



				#UPDATE LAST INFORMATIONS IN DATA SET
				self.archive_dataset["ARCHIVESIZE_AFTER"] = os.path.getsize(self.current_project_data["ARCHIVE_PATH"])
				#self.archive_dataset["PROJECTSIZE_AFTER"] = self.current_project_data["DATA_FOLDER"][self.current_project]["CHILDREN_SIZE"]
				#PROJECT SIZE AFTER ARCHIVING IS EQUAL TO THE PROJECT SIZE LESS THE WEIGHT ALL ALL ITEMS ARCHIVED
				self.archive_dataset["PROJECTSIZE_AFTER"] = self.current_project_data["DATA_FOLDER"][self.current_project]["CHILDREN_SIZE"]-self.archive_dataset["CONTENTSIZE_BEFORE"]


				#DISPLAY THE FINAL DATA SET
				#print(colored("\n\nGLOBAL INFORMATIONS AFTER ARCHIVING", "magenta"))
				console.log("[%s]\nGLOBAL INFORMATIONS AFTER ARCHIVING"%self.THEME.accent)
				for key, value in self.archive_dataset.items():
					#print(colored(key, "magenta"), " : %s"%value)
					console.print("\t[%s]%s[/%s][%s]%s"%(self.THEME.primary,key,self.THEME.primary,self.THEME.foreground,value))

				

				#SAVE THE ARCHIVE LOG
				try:
					with open(self.current_project_data["ARCHIVE_LOG"], "w") as save_file:
						json.dump(dict(self.archive_log), save_file, indent=4)

				except Exception as e:
					#print(colored("\nImpossible to save archive log\n%s"%traceback.format_exc(), "red"))
					console.log("[%s]Impossible to save archive log\n%s"%(self.THEME.error, traceback.format_exc()))
				else:
					console.log("[%s]Archive log saved successfully"%self.THEME.success)
					#print(colored("\nArchive log saved successfully", "green"))
				
	



			except Exception as e:
				console.log("[%s]Fatal error happened during archiving process\n%s"%(self.THEME.error, traceback.format_exc()))
				#print(colored("Fatal error happened during archiving process\n%s"%traceback.format_exc(), "red"))
			else:
				console.log("[%s]Archiving process terminated"%self.THEME.success)
				#print(colored("Archiving process terminated", "green"))
				return self.current_project_data


	def test_compression_method_function(self):
		console = Console()
		rich_title_archiving = RichFiglet("COMPRESSION TEST", font=ASCII_FONT_HOMEPAGE, colors=[self.THEME.primary, self.THEME.background], animation=None,quality=40)
		console.print(rich_title_archiving)

		self.compression_method_dictionnary = {}

		#define the compression list to test with a file for each of them
		"""
		for extension_name, extension_data in self.current_project_data["DATA_FILE_EXTENSION"].items():
			for file in extension_data["FILE_LIST"]:
				#get the size of the file
				if self.current_project_data["DATA_FILES"][file]["FILESIZE"] > 0:
					extension_dictionnary[extension_name] = file
					break
		"""
		extension_list = list(self.current_project_data["DATA_FILE_EXTENSION"].keys())
		extension_dictionnary = {}
		for index in self.selection_to_archive:
			extension_name = extension_list[index]
			#find a file
			for extension_file in self.current_project_data["DATA_FILE_EXTENSION"][extension_name]["FILE_LIST"]:
				#check the size of the file
				if self.current_project_data["DATA_FILES"][extension_file]["FILESIZE"] > 0:
					extension_dictionnary[extension_name] = extension_file
					break

		#display the test
		for key, value in extension_dictionnary.items():
			console.print("[%s]%s →[/%s] %s"%(self.THEME.primary,key,self.THEME.primary,value))

		method_list = [
			("ZIP_STORED",zipfile.ZIP_STORED),
			("ZIP_DEFLATED",zipfile.ZIP_DEFLATED),
			("ZIP_BZIP2",zipfile.ZIP_BZIP2),
			("ZIP_LZMA",zipfile.ZIP_LZMA),
			]

		#create the output path for the archive path
		extension_archive_path = os.path.join(os.getcwd(), "data/temp_compression")
		if os.path.isdir(extension_archive_path)==False:
			os.makedirs(extension_archive_path, exist_ok=True)
			console.log("[%s]Temp folder created"%(self.THEME.primary))
		else:
			console.log("[%s]Clean the content of the existing folder"%(self.THEME.primary))
			#clean the content of the folder
			for item in os.listdir(extension_archive_path):
				full_path = os.path.join(extension_archive_path,item)
				if os.path.isfile(full_path):
					os.remove(full_path)
				if os.path.isdir(full_path):
					shutil.rmtree(full_path)

		for extension_name, extension_file in extension_dictionnary.items():
			console.log("[%s]\n\n\n\n%s\nLAUNCHING TEST FOR EXTENSION → %s"%(self.THEME.accent,"="*150, extension_name))
			with mp.Manager() as manager:
				self.file_queue = [extension_file]

				

				#launching processes
				process_pool = []
				extension_archive_dirpath = os.path.join(extension_archive_path, extension_name)
				os.makedirs(extension_archive_dirpath, exist_ok=True)
				for i in range(len(method_list)):
					
					#extension_archive_filename = os.path.join(extension_archive_path,"temp_archive_%s.zip"%(str(method_list[i]).split(".")))
					extension_archive_filename = "temp_archive_%s.zip"%(str(method_list[i][0]))
					extension_archive_fullpath = os.path.join(os.path.join(extension_archive_path, extension_name), extension_archive_filename)
					console.log(extension_archive_fullpath)

					try:
						p = mp.Process(target=self.archive_item_worker, args=(i, None, extension_archive_fullpath, self.current_project, method_list[i][1], False,False))
						p.start()
						process_pool.append(p)
					except Exception as e:
						console.log("[%s]Impossible to launch process"%(self.THEME.error))
						console.log("[%s]%s"(self.THEME.error, traceback.format_exc()))
					else:
						console.log("[%s]Process launched"%self.THEME.success)

				for p in process_pool:
					p.join()
					console.log("[%s]Process terminated"%self.THEME.primary)

			console.log("[%s]\nGATHERING INFORMATIONS TO DEFINE BEST COMPRESSION RATIO"%self.THEME.accent)
			#explore each archive in the extension folder
			console.log("[%s]Original file size →[/%s] %s"%(self.THEME.primary,self.THEME.primary,self.current_project_data["DATA_FILES"][extension_file]["FILESIZE"]))
			output_data_dictionnary = {}
			for archive in os.listdir(extension_archive_dirpath):
				archive_path = os.path.join(extension_archive_dirpath, archive)
				#if (os.path.isfile(os.path.join(extension_archive_dirpath,archive))==True) and (os.path.splitext(archive)[1]=="zip"):
				#read the compress size
				with zipfile.ZipFile(archive_path, mode="r") as extension_archive:
					file_data = extension_archive.infolist()[0]
					#console.log("[%s]%s →[/%s] %s"%(self.THEME.primary,os.path.splitext(archive)[0].replace("temp_archive_",""),self.THEME.primary,file_data.compress_size))
					output_data_dictionnary[os.path.splitext(archive)[0].replace("temp_archive_", "")]=file_data.compress_size
			for method, method_size in output_data_dictionnary.items():
				if method_size == min(list(output_data_dictionnary.values())):
					console.log("[%s]%s →[/%s] %s"%(self.THEME.success,method,self.THEME.success,method_size))
				else:
					console.log("[%s]%s →[/%s] %s"%(self.THEME.secondary,method,self.THEME.secondary,method_size))





	def archive_item_worker(self, index, temp_archive=None, archive_path=None, project_path=None, method=zipfile.ZIP_LZMA, overhead_checking=True, update_data=True):
		if isinstance(self.file_queue, queue.Queue):
			while True:
				try:
					item_to_archive = self.file_queue.get(timeout=5)

					if item_to_archive == None:
						print(colored("\tProcess broken [%s]"%index, "yellow"))
						break
					else:
						#print("[%s] checking %s"%(index,item_to_archive))



						#OPEN THE ZIPFILE ARCHIVE
						archived=False
						with zipfile.ZipFile(temp_archive, mode="a", compression=method, compresslevel=9) as archive:

							if os.path.isfile(item_to_archive) == True:
								print("\t[%s] Archiving file : %s"%(index,os.path.basename(item_to_archive)))

								#add informations in archiving data set
								#self.archive_dataset["CONTENTSIZE_BEFORE"] += self.current_project_data["DATA_FILES"][item_to_archive]["FILESIZE"]
								
								try:
									archive.write(item_to_archive, arcname=Path(item_to_archive).relative_to(Path(project_path)))
								except Exception as e:
									self.ns.global_count += 1
									print(colored("\t[%s] Impossible to save file : %s"%(index,os.path.basename(item_to_archive)), "red"))
								else:
									archived=True
									self.ns.global_count += 1
									print(colored("\t[%s] %s/%s - File successfully archived : %s"%(index, self.ns.global_count, self.ns.total_count ,os.path.basename(item_to_archive)), "green"))
									

									#update the statut of the file in the dictionnary
									"""
									data_file = self.shared_current_project_data["DATA_FILES"]
									data_file[item_to_archive]["ARCHIVE"]=True
									
									self.shared_current_project_data["DATA_FILES"] = data_file
									"""

									if update_data==True:
										#update the global project data dictionnnary
										current_project_data_folder = self.shared_current_project_data["DATA_FOLDER"]
										current_folder_data = current_project_data_folder[os.path.dirname(item_to_archive)]
										#remove the file from the folder filelist
										current_folder_data["FILE_LIST"].remove(os.path.basename(item_to_archive))
										#check if archive list exists for this folder
										if "ARCHIVED_LIST" not in current_folder_data:
											current_folder_data["ARCHIVED_LIST"] = []
										#add the file to the archive list
										current_folder_data["ARCHIVED_LIST"].append(os.path.basename(item_to_archive))
										#update the global dictionnary
										current_project_data_folder[os.path.dirname(item_to_archive)] = current_folder_data
										self.shared_current_project_data["DATA_FOLDER"] = current_project_data_folder
										print(colored("\t[%s] Archive dictionnary updated for this folder : %s"%(index,os.path.dirname(item_to_archive))))





										self.new_archived_file_list.append(item_to_archive)

										#update the archiving data set
										self.archive_dataset["CONTENTSIZE_BEFORE"] += self.current_project_data["DATA_FILES"][item_to_archive]["FILESIZE"]

										#write the file in the archive dictionnary
										if item_to_archive not in self.archive_log:
											print("\tWriting dictionnary key")
											self.archive_log[item_to_archive] = {
												"ARCHIVEPATH": str(Path(item_to_archive).relative_to(Path(project_path))),
												"REALPATH": str(Path(item_to_archive)),
												"ARCHIVINGDATE": str(datetime.now()),
												"HARDRIVESIZE": self.current_project_data["DATA_FILES"][item_to_archive]["FILESIZE"],
											}
										else:
											print(colored("\t[%s] File already writen in archive log: %s"%(index,item_to_archive), "red"))


									


									#update the size amount removed from the main project with archiving (sum of all files archived)
									#self.current_project_data


						#display the archive content
						with zipfile.ZipFile(temp_archive, mode="r") as read_content:
							for data in read_content.infolist():
								print("\t%s"%data)
						if overhead_checking==True:
							self.check_for_overhead_file_function(temp_archive, item_to_archive, Path(item_to_archive).relative_to(Path(project_path)))


				except queue.Empty:
					#print(colored(traceback.format_exc(), "red"))
					return
				except Exception as e:
					print(colored("\t%s"%traceback.format_exc(), "red"))
		elif isinstance(self.file_queue, list):
			#print("\t\tLIST MODE DETECTED : %s"%self.file_queue[0])
			try:
				with zipfile.ZipFile(archive_path, mode="a", compression=method, compresslevel=9) as archive:
					for item in self.file_queue:
						archive.write(item,arcname=os.path.basename(item))
			except Exception as e:
				print(colored("\t\tImpossible to archive item\n%s"%traceback.format_exc(), "red"))
			else:
				print(colored("\t\tItem archived : %s"%os.path.basename(item)))
		else:
			print(colored("\t\tWrong file queue detected", "red"))

	def check_for_overhead_file_function(self, archive_path, filepath, archive_filepath):
		print(colored("\n\tChecking overheads ...", "cyan"))
		print("\tarchive path : %s\nfile path : %s"%(archive_path, archive_filepath))

		#try to read the content of the archive
		overhead=False
		with zipfile.ZipFile(archive_path, mode="r") as archive:
			archive_filedata = archive.getinfo((archive_filepath).as_posix())
			archive_filesize = archive_filedata.file_size
			archive_compresssize = archive_filedata.compress_size

			if archive_compresssize > archive_filesize:
				print(colored("\tOverhead detected for this file!", "red"))
				overhead=True
			else:
				print(colored("\tNo overhead detected for this file!", "green"))


		if overhead==True:
			#remove this file from the archive
			try:
				zipdel.delete_from_zip_file(archive_path, archive_filepath)
			except Exception as e:
				print(colored("\tImpossible to remove file from archive", "red"))
				print(colored(traceback.format_exc(), "red"))
			else:
				#rewrite this file in archive without compression
				print(colored("\tTrying to rewrite file without compression"))
				with zipfile.ZipFile(archive_path, mode="a", compression=zipfile.ZIP_STORED) as archive:
					archive.write(filepath, arcname=archive_filepath)
				print(colored("\tFile stored in archive successfully (no compression)", "green"))


class ModalASPCMoveArchive(ModalScreen):
	def compose(self) -> ComposeResult:
		with Vertical(id="modal_vertical_archive_move"):
			yield Label("ARE YOU SURE YOU WANT TO MOVE THE ARCHIVE PATH ?", id="modal_label_archive_move")

			with Horizontal(id="modal_horizontal_archive_options"):
				yield Button("Yes", id="modal_button_archive_move_true", classes="button_main")
				yield Button("No", id="modal_button_archive_move_false")

	def on_button_pressed(self,event:Button.Pressed) -> None:
		if event.button.id == "modal_button_archive_move_true":
			self.dismiss(True)
		if event.button.id == "modal_button_archive_move_false":
			self.dismiss(False)


class ASPC_ARCHIVE():
	def init_apply_filter_function(self):
		#apply filters on file list
		self.app.message_function("Starting to apply filter on file list", "notification")
		#create the list of index to highlight <==> filtered
		already_checked_list = []
		self.final_filtered_list = []
		#create the file queue
		



		#call the multiprocessing class
		with self.app.suspend():
			ASPC_ARCHIVE_MULTIPROCESSING(self.filter_dictionnary, self.filter_origin_list, self.app.current_project_data)
			os.system("pause")


		#try to load the temp file
		try:
			with open("data/temp_filtered.dll", "r") as read_file:
				self.final_filtered_list = json.load(read_file)
		except Exception as e:
			self.app.message_function("Impossile to load temp filtered file\n%s"%traceback.format_exc(), "error")
		else:
			self.app.message_function("Filtered list retrived", "success")
			#remove the temp filtered file
			try:
				os.remove("data/temp_filtered.dll")
			except Exception as e:
				self.app.message_function("Impossible to remove temp filtered file\n%s"%traceback.format_exc(), "error")
			else:
				self.app.message_function("Temp filtered file removed")


		#clear the index list
		#self.listview_modal_filterorigin.clear_list()
		self.listview_modal_filterorigin.clear_list()

		for children in self.listview_modal_filterorigin.children:
			children.highlighted = False
		
		#highlight filtered elements in the list
		for file in self.final_filtered_list:
			#get the index of the element in the list
			#self.app.message_function("[%s] %s"%(file in self.filter_origin_list, file))
			try:
				index = self.filter_origin_list.index(file)

				if index not in self.listview_modal_filterorigin.index_list:
					self.listview_modal_filterorigin.index_list.append(index)
					self.listview_modal_filterorigin.children[index].highlighted=True
			except ValueError:
				self.app.message_function("Impossible to find item in list : %s"%file, "error")
				self.app.message_function(traceback.format_exc(), "error")

	def check_move_archive(self, move:bool | None) -> None:
		try:
			if move==True:
				#self.message_function(self.new_archive_path)
				#self.message_function(str(quit))
				#create the new folder hierarchy for the new archive path
				os.makedirs(os.path.dirname(self.new_archive_path), exist_ok=True)
				#move the file with shutil
				shutil.move(self.current_project_data["ARCHIVE_PATH"],os.path.dirname(self.new_archive_path))
				#update the archive path in the project data
				self.current_project_data["ARCHIVE_PATH"] = self.new_archive_path
				self.project_data[self.current_project_name] = self.current_project_data 
				#save the new project file
				self.save_dictionnary_function()
				self.message_function("ARCHIVE MOVED", "success")
				self.message_function("New archive path : %s"%self.new_archive_path)
		except Exception as e:
			self.message_function("Impossible to change archive path", "error")
			self.message_function(traceback.format_exc(), "error")

	def move_archive_function(self):
		#get the path in the archive textfield
		archive_textfield_content = self.input_archive_path.value
		#get the folder path
		archive_textfield_dirpath = os.path.dirname(archive_textfield_content)
		#get the current archive path
		try:
			if "ARCHIVE_PATH" not in self.current_project_data:
				self.message_function("The archive is not defined for this project", "error")
				return 
			else:
				current_archive_path = self.current_project_data["ARCHIVE_PATH"]
				current_archive_filename = os.path.basename(current_archive_path)
				self.new_archive_path = os.path.join(archive_textfield_dirpath,current_archive_filename)

				#self.message_function("NEW ARCHIVE PATH → %s"%self.new_archive_path, "notification")

				self.move_archive=None
				#call validation screen	
				self.push_screen(ModalASPCMoveArchive(self.new_archive_path), self.check_move_archive)
				#self.message_function(str(value), "success")
		except AttributeError:
			self.message_function("No project selected", "error")


	def check_for_archive_content_function(self):
		#get the current project selected
		#check if the archive path is defined for this project
		if "ARCHIVE_PATH" in self.current_project_data:
			self.input_archive_path.value = self.current_project_data["ARCHIVE_PATH"]
			self.message_function(" ", "message", False)
			self.message_function("Project archive path : %s"%self.current_project_data["ARCHIVE_PATH"])
			self.message_function("Project archive log : %s"%self.current_project_data["ARCHIVE_LOG"])

			#clear the actual content of the listview
			self.listview_archive_content.clear()

			if os.path.isfile(self.current_project_data["ARCHIVE_PATH"])==False:
				self.message_function("Archive doesn't exists yet / anymore", "error")
			else:
				self.message_function("Archive file detected in folder", "notification")
				#get the content of the archive
				self.current_archive_content.clear()
				data_file = self.current_project_data["DATA_FILES"]
				changes = False
				try:
					with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], mode="r") as archive:
						for file in archive.namelist():

							#check the statut for the current file in settings
							"""
							if "ARCHIVE" not in data_file[os.path.normpath(os.path.join(self.current_project_name, file))]:
								#create the key

								self.message_function("  value updated in dictionnary for %s"%file, "message", False)
								file_data = data_file[os.path.normpath(os.path.join(self.current_project_name, file)).replace("\\", "/")]
								file_data["ARCHIVE"] = True
								data_file[os.path.join(self.current_project_name,file)] = file_data

								if changes==False:
									changes=True
							"""

							self.current_archive_content.append(file)

				except Exception as e:
					self.message_function("Impossible to get archive content\n%s"%traceback.format_exc(), "error")
					return

				"""
				if changes==True:
					self.message_function("Some files were updated in Main Data file\n-> Updating dictionary", "notification")
					#update the dictionnary content
					self.current_project_data["DATA_FILES"]=data_file
					#save the dictionnary
					self.project_data[self.current_project_name] = self.current_project_data
					self.save_dictionnary_function()
				"""


				
				#load the archive content in the list
				label_list = []
				for file in self.current_archive_content:
					label = Label(file)
					label_list.append(MultiListItem(label))
				self.listview_archive_content.extend(label_list)



		else:
			self.message_function("Impossible to get archive content for this project\nArchive path is not defined", "notification")


	def check_for_archive_function(self):
		#get the current project selected
		self.app.message_function("Checking for archive", "notification")
		if self.current_project_name != None:
			self.app.message_function("Current project selected : %s"%self.current_project_name)

			#check if the key is in the dictionnary
			try:
				
				archive_path = self.current_project_data["ARCHIVE_PATH"]
				archive_log = self.current_project_data["ARCHIVE_LOG"]
			except KeyError:
				self.app.message_function("Archive doesn't exists yet for this project", "warning")
				return False

			except Exception as e:
				self.app.message_function("Impossible to check for archive data\n%s"%traceback.format_exc(), "error")
				return False

			else:
				return True
		else:
			self.app.message_function("No project selected","error")
			return False




		if overhead==True:
			#remove this file from the archive
			try:
				zipdel.delete_from_zip_file(archive_path, archive_filepath)
			except Exception as e:
				print(colored("Impossible to remove file from archive", "red"))
				print(colored(traceback.format_exc(), "red"))
			else:
				#rewrite this file in archive without compression
				print(colored("Trying to rewrite file without compression"))
				with open(archive_path, mode="a", compression=zipfile.ZIP_STORED) as archive:
					archive.write(filepath, arcname=archive_filepath)
				print(colored("File stored in archive successfully (no compression)", "green"))



	def check_for_overhead_function(self):
		#get the current project selected
		#get the current archive path
		self.message_function("\n", "message", False)
		self.message_function("Trying to detect overheads in archive", "notification")
		try:
			archive_path = self.current_project_data["ARCHIVE_PATH"]
		except Exception as e:
			self.message_function("Impossible to get archive path","erorr")
			return 
		#try to open the archive
		overhead_counter = 0
		overhead_size = 0
		overhead_list = []
		#get all childrens in listview
		children_list = self.listview_archive_content.children

		try:
			with zipfile.ZipFile(archive_path, mode="r") as read_archive:
				#get the archive content in listview
				for i in range(len(self.current_archive_content)):
					#get data about file
					item_info = read_archive.getinfo(self.current_archive_content[i])
					#self.message_function("\n%s\n%s\n%s"%(os.path.basename(item), item_info.file_size, item_info.compress_size), "message", False)
					file_size = item_info.file_size
					compress_size = item_info.compress_size
					if compress_size > file_size:
						overhead_counter+=1
						overhead_size += (compress_size - file_size)
						#overhead_list.append(self.current_archive_content[i])
						#highlight the item
						children_list[i].highlight_item(children_list[i])
						if i not in self.listview_archive_content.index_list:
							self.listview_archive_content.index_list.append(i)
		except Exception as e:
			self.message_function("Error happened while reading the archive\n%s"%traceback.format_exc(), "error")
			return 
		else:
			self.message_function("Archive overhead scan terminated","notification")
		self.message_function("Number of overhead : %s\nOverhead size in archive : %s Go\n"%(overhead_counter,overhead_size/(1024**3)),"message", False)
		#for each file check if the compressed size is bigger than realsize
		#select items with overhead in the

	def fix_overhead_function(self):
		#get the filelist from the selection
		overhead_filelist = []
		for index in self.listview_archive_content.index_list:
			overhead_filelist.append(self.current_archive_content[index])
			#self.message_function(self.current_archive_content[index])
		#restore files from the archive
		with self.app.suspend():
			self.restore_filelist_function(self.current_project_data["ARCHIVE_PATH"], overhead_filelist)
			#after restoring files
			#archive them again with the archiving class
			#with the zipfile stored method

			#build the real file list joined with project path
			"""
			for i in range(len(overhead_filelist)):
				overhead_filelist[i] = os.path.join(self.current_project_name, overhead_filelist[i])
			"""
			fill_archive = ASPC_FILL_ARCHIVE(overhead_filelist, self.current_project_name, self.current_project_data, zipfile.ZIP_STORED)
			returned_dictionnary = fill_archive.run()
			os.system("pause")



	def archiving_display_message_function(self, message = "", type="message"):

		if type == "content":
			label = Label("  %s"%message)
		else:
			label = Label("[%s] %s"%(type.upper(),message))


		#get the color for the created label before printing it
		if type.upper() == "NOTIFICATION":
			color = "text-accent"
		elif type.upper() == "ERROR":
			color = "text-error"
		elif type.upper() == "SUCCESS":
			color = "text-success"

		else:
			color = "text-primary"

		#color the label
		label.styles.color = self.app.theme_variables[color]
		self.listview_modal_addarchive_filelog.append(ListItem(label))



	def restore_file_from_archive_function(self, skip_removing=False):
		console = Console()
		rich_title_restore = RichFiglet("RESTORE ARCHIVE CONTENT", font=ASCII_FONT_HOMEPAGE, colors=[self.THEME_DICTIONNARY.primary, self.THEME_DICTIONNARY.background], animation=None, quality=40)
		console.print(rich_title_restore)
		#print(colored("Restore file function starting...", "cyan"))
		#get items selected
		index_list = self.listview_archive_content.index_list
		if len(index_list)==0:
			#print(colored("Nothing to extract", "red"))
			console.log("[%s]Nothing to extract"%self.THEME_DICTIONNARY.error)
			return
		#file_to_restore_list = []
		#trying to find the zipfile
		elif "ARCHIVE_PATH" not in self.current_project_data:
			#print(colored("No archive is defined for this project", "red"))
			console.log("[%s]No archive is defined for this project"%self.THEME_DICTIONNARY.error)
			return 
		elif os.path.isfile(self.current_project_data["ARCHIVE_PATH"])==False:
			#print(colored("The archive doesn't exists anymore at this location", "red"))
			#print(colored(self.current_project_data["ARCHIVE_PATH"], "red"))
			console.log("[%s]The archive doesn't exists anymore at this location"%self.THEME_DICTIONNARY.error)
			console.log("[%s]%s"%(self.THEME_DICTIONNARY.error, self.current_project_data["ARCHIVE_PATH"]))
			return
		else:
			filelist = []
			for index in index_list:
				filelist.append(self.current_archive_content[index])

			self.restore_filelist_function(console,self.current_project_data["ARCHIVE_PATH"], filelist, skip_removing)

				


	def restore_filelist_function(self, console, archive_path, filelist=[], skip_removing=False):

		#print(colored("Trying to restore files from archive...", "cyan"))
		#print(colored("Opening the archive file...", "white"))
		console.log("[%s]Trying to restore files from archive..."%self.THEME_DICTIONNARY.primary)
		console.log("[%s]Opening the archive file..."%self.THEME_DICTIONNARY.primary)
		try:
			with zipfile.ZipFile(archive_path, mode="r") as archive:

				for file_to_restore in filelist:
					filepath_to_restore = os.path.join(self.current_project_name,file_to_restore).replace("\\", "/")


					#RESTORE THE FILE AT THE RIGHT LOCATION
					try:
						archive.extract(file_to_restore, self.current_project_name)
					except Exception as e:
						#print(colored("failed to restore file : %s\n%s"%(file_to_restore,traceback.format_exc()), "red"))
						console.log("[%s]Failed to restore file : %s\n%s"%(self.THEME_DICTIONNARY.error,file_to_restore, traceback.format_exc()))
					else:
						#print(colored("file extracted successfully : %s\n\tlocation : %s"%(file_to_restore,filepath_to_restore), "green"))
						console.log("[%s]File extracted successfully : %s\n\tLocation : %s"%(self.THEME_DICTIONNARY.success,file_to_restore, filepath_to_restore))
						#put back the file in the filelist of the current folder data
						folder_data = self.current_project_data["DATA_FOLDER"][os.path.dirname(filepath_to_restore).replace("/", "\\")]
						folder_data["FILE_LIST"].append(os.path.basename(filepath_to_restore))
						self.current_project_data["DATA_FOLDER"][os.path.dirname(filepath_to_restore)] = folder_data
						#print(colored("File added to folder filelist", "green"))
						console.log("[%s]File added to folder filelist"%self.THEME_DICTIONNARY.success)



			#print(colored("\nRemoving files in archive...", "cyan"))
			console.log("[%s]Removing files from archive..."%self.THEME_DICTIONNARY.primary)
			if skip_removing==False:
				#REMOVE FILES FROM THE ARCHIVE
				for file_to_restore in filelist:
					#for index in index_list:
					#file_to_restore = self.current_archive_content[index]
					#check if the file exists in project before removing it from archive!
					if os.path.isfile(os.path.join(self.current_project_name, file_to_restore))==True:
						try:
							zipdel.delete_from_zip_file(self.current_project_data["ARCHIVE_PATH"], file_to_restore)
						except Exception as e:
							#print(colored("failed to remove file : %s\n%s"%(file_to_restore, traceback.format_exc()), "red"))
							console.log("[%s]Failed to remove file : %s\n%s"%(self.THEME_DICTIONNARY.error, file_to_restore, traceback.format_exc()))
						else:
							console.log("[%s]File removed from archive : %s"%(self.THEME_DICTIONNARY.success,file_to_restore))
							#print(colored("file removed from archive : %s"%file_to_restore, "white"))
							#remove from the archive list for the folder data
							folder_data = self.current_project_data["DATA_FOLDER"][os.path.dirname(os.path.join(self.current_project_name, file_to_restore)).replace("/", "\\")]
							if ("ARCHIVED_LIST" in folder_data) and (os.path.basename(file_to_restore) in folder_data["ARCHIVED_LIST"]):
								folder_data["ARCHIVED_LIST"].remove(os.path.basename(file_to_restore))
								#udpate the data dictionnary
								self.current_project_data["DATA_FOLDER"][os.path.dirname(os.path.join(self.current_project_name, file_to_restore)).replace("/", "\\")]


			else:
				#print(colored("Skipped removing files", "cyan"))
				console.log("[%s]Skipped removing files"%self.THEME_DICTIONNARY.primary)
		except Exception as e:
			console.log("[%s]Impossible to extract content from archive\n%s"%(self.THEME_DICTIONNARY.error,traceback.format_exc()))
			#print(colored("Impossible to extract content from archive\n%s"%traceback.format_exc(), "red"))
			return 
		else:
			#update the global data dictionnary
			self.project_data[self.current_project_name] = self.current_project_data
			#save the new global dictionnary
			self.save_dictionnary_function()
			console.log("[%s]Extraction terminated"%self.THEME_DICTIONNARY.success)
			#print(colored("Extraction terminated", "green"))
			return







