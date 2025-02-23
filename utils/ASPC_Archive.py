# -*- coding: utf-8 -*-


from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen, ModalScreen
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on
from termcolor import *

from utils.ASPC_Widgets import MultiListView, MultiListItem


import colorama
import os
import json
import traceback
import copy
import multiprocessing as mp
import threading
import queue

from datetime import datetime
from pathlib import Path
from time import sleep



colorama.init()




"""
class ASPC_ARCHIVE:
	def __init__(self, filter_dictionnary, origin_list, current_project_data):
		self.filter_dictionnary = filter_dictionnary
		self.current_project_data = current_project_data
		self.origin_list = origin_list


		

		#define the multiprocressing manager
		with mp.Manager() as manager:
		
			#create the file queue
			self.queue = mp.Queue()
			for folder in origin_list:
				self.queue.put(folder)

			
			
			#define the multiprocessing shared variables
			self.final_filtered_list = manager.list()



			#launch multiprocessing
			process_pool = []
			#define the process number
			process_number = mp.cpu_count()
			for i in range(process_number):
				try:
					p = mp.Process(target=self.filter_folder_function, args=(i,))
					p.start()
					process_pool.append(p)
				except Exception as e:
					print(colored("\nFailed to launch process", "red"))
					print(colored(traceback.format_exc(), "red"))
				else:
					print(colored("Process launched : %s"%p, "green"))


			for p in process_pool:
				print(colored("Process terminated : %s"%str(p), "green"))
				p.join()

			print(colored("All processes terminated", "green"))
			

			try:
				with open("temp_filtered.dll", "w") as save_file:
					json.dump(list(self.final_filtered_list), save_file, indent=4)
			except Exception as e:
				print(colored("Error while exporting filtered list", "red"))
				print(colored(traceback.format_exc(), "red"))
			else:
				print(colored("Filtered list exported successfully", "green"))

	def filter_folder_function(self, index):
		while True:
			try:
				self.folder = self.queue.get(timeout=5)
				if self.folder == None:
					break
				else:
					#print(colored("[%s] Checking folder : %s"%(index,self.folder)))

					#get folder data
					folder_data = self.current_project_data["DATA_FOLDER"][self.folder]
					#get folder file list
					folder_file_list = folder_data["FILE_LIST"]



					#FILENUMBER FILTER
					if self.filter_dictionnary["FilterByFileNumber"]==True:
						if len(folder_file_list) < int(self.filter_dictionnary["FilterFileNumber"]):
							print(colored("File Number Filter : Folder skipped : %s"%self.folder, "yellow"))
							continue


					#SIMILARITY FILTER
					#CREATE A NEW FILELIST
					if self.filter_dictionnary["FilterBySimilarity"]==True:
						
						#get the sim dictionnary for this folder
						for folder_sim_name, folder_sim_filelist in folder_data["SIMILARITY"].items():
							if len(folder_sim_filelist) >= int(self.filter_dictionnary["FilterSimilarityNumber"]):
								self.apply_filter_on_files_function(folder_sim_filelist)

					else:
						self.apply_filter_on_files_function(folder_file_list)

			except mp.queues.Empty:
				print(colored("process done", "red"))
				return

			except Exception as e:
				print(colored(traceback.format_exc(), "red"))
				return

	def apply_filter_on_files_function(self, filelist):
		#print(filelist)
		for file in filelist:


			#EXTENSION FILTER
			if self.filter_dictionnary["FilterByExtension"]==True:
				if len(self.filter_dictionnary["FilterExtensionList"]) == 0:
					pass
				else:
					if os.path.splitext(file)[1] not in self.filter_dictionnary["FilterExtensionList"]:
						continue

			#SIZE FILTER
			if self.filter_dictionnary["FilterBySize"] == True:
				#print("checking size")
				min_size = int(self.filter_dictionnary["FilterMinSize"])
				max_size = int(self.filter_dictionnary["FilterMaxSize"])

				if max_size == 0:
					max_size = float("inf")

				#convert filesize to mo
				mo_filesize = self.current_project_data["DATA_FILES"][os.path.join(self.folder,file)]["FILESIZE"] / (1024 * 1024)

				#print("%s ; %s; %s"%(min_size,mo_filesize,max_size))
				if (mo_filesize < min_size) or (mo_filesize > max_size):
					continue



			#KEYWORD FILTER
			if self.filter_dictionnary["FilterByKeyword"] == True:
				#get keyword list 
				keyword_list = [keyword.lower() for keyword in self.filter_dictionnary["FilterKeywordList"]]
				if len(keyword_list) == 0:
					pass
				else:
					is_keyword=False
					for keyword in keyword_list:
						if keyword in os.path.splitext(file)[0]:
							is_keyword=True
					if is_keyword==False:
						continue





			print(colored("File filtered successfully : %s"%os.path.join(self.folder,file), "white"))
			self.final_filtered_list.append(os.path.join(self.folder,file))

	def check_for_filtered_function(self, filter_dictionnary):


		self.filtered_list = []
		self.filter_dictionnary = copy.copy(filter_dictionnary)

		try:
			
			#define the target
			#self.app.call_from_thread(self.add_filtered_line_function, filter_dictionnary["FilterOnlySelected"])
			if filter_dictionnary["FilterOnlySelected"]==True:
				#get folder selected
				index_list = self.app.listview_folders.index_list
				origin_folder_list = []
				origin_list = []

				if len(index_list) == 0:
					self.app.mesage_function("You must select folders to apply filters!")
					self.query_one("#button_modal_quit").disabled=False
					return
				
				for index in index_list:
					#add the source folder to the list
					origin_folder_list.append(self.app.current_folder_list[index])	
				#for each folder selected check that there is no folder in the list that is parent of this folder

				for x in origin_folder_list:

					if len(origin_list) == 0:
						origin_list.append(x)
					else:
						folder_checked = False

						for y in origin_list:
							if (Path(x).resolve() in Path(y).resolve().parents) or (Path(y).resolve() in Path(x).resolve().parents):
								folder_checked=True
								break

						if folder_checked == False:
							origin_list.append(x)
						else:
							self.app.message_function("Folder skipped because children or parent of an other folder in the list\n%s\n%s\n"%(x,y), "warning")
							continue


				

			else:
				try:
					origin_list = self.app.current_project_data["DATA_FOLDER"].keys()
				except Exception as e:
					self.app.message_function("You have to select a project before applying filters", "error")
					self.query_one("#button_modal_quit").disabled=False
					return





			self.progress_modal_filtered.update(progress=0)
			self.progress_modal_filtered.update(total = len(origin_list))
			#initiate the progress bar before starting to filter elements
			#self.progress_modal_filtered.update(total = len(origin_list))

			#check each element of the list to filter
			for element in origin_list:
				#self.progress_modal_filtered.advance(1)


				self.explore_function(element)
				self.progress_modal_filtered.advance(1)





				#self.app.call_from_thread(self.add_filtered_line_function, element)


			#enable the button at the end of the process
			self.query_one("#button_modal_quit").disabled=False



		except Exception as e:
			self.app.message_function(traceback.format_exc(), "error")
			self.query_one("#button_modal_quit").disabled=False
		else:
			self.app.message_function("Arching thread terminated", "success")

	def explore_function(self, element):
		self.app.message_function("checking folder : %s"%element, "message", False)


		#udpate the total of the progress bar
		self.progress_modal_filtered.update(total=(self.progress_modal_filtered.total + len(self.app.current_project_data["DATA_FOLDER"][element]["FILE_LIST"])))
		self.progress_modal_filtered.update(total=(self.progress_modal_filtered.total + len(self.app.current_project_data["DATA_FOLDER"][element]["FOLDER_LIST"])))
		
		#GET THE FILE LIST FOR THIS FOLDER
		for file in self.app.current_project_data["DATA_FOLDER"][element]["FILE_LIST"]:
			
			#self.app.message_function("checking file : %s"%file)
			#get dictionnary informations about the current file that 
			#could be useful when filter checking
			filepath = os.path.join(element, file)
			filesize = self.app.current_project_data["DATA_FILES"][filepath]["FILESIZE"]


			if filepath in self.filtered_list:
				self.app.message_function("File already filtered : %s"%filepath,"notification")
				continue


			valid=True
			checked_sim_list = []
			#CHECK EACH FILTER SELECTED BY THE USER




			
			#EXTENSION FILTER
			if self.filter_dictionnary["FilterByExtension"]==True:
				if os.path.splitext(filepath)[1] not in self.filter_dictionnary["FilterExtensionList"]:
					#valid=False
					continue

			#SIZE FILTER
			if self.filter_dictionnary["FilterBySize"]==True:
				#get min size
				min_size = int(self.filter_dictionnary["FilterMinSize"])
				max_size = int(self.filter_dictionnary["FilterMaxSize"])

				if max_size == 0:
					#convert the max size into inf
					max_size = float('inf')

				if (min_size < 0) or (max_size <= min_size):
					self.app.message_function("Error on min / max size values", "error")
					return
				else:
					#convert in mo
					filesize_mo = filesize / (1024 * 1024)
					#check for the interval
					if (filesize_mo < min_size) or (filesize_mo > max_size):
						#valid=False
						continue

			#SIMILARITY FILTER
			if self.filter_dictionnary["FilterBySimilarity"]==True:
				#get the number of similarity
				try:
					sim_threshold = int(self.filter_dictionnary["FilterSimilarityNumber"])
				except Exception as e:
					self.app.mesage_function(e, "error")
					return
				#get the simdata for file
				try:
					sim_key = self.app.current_project_data["DATA_FILES"][filepath]["SIMKEY"]
					sim_parent = self.app.current_project_data["DATA_FILES"][filepath]["SIMPARENT"]
					#get sim dictionnary
					sim_list = self.app.current_project_data["DATA_FOLDER"][sim_parent]["SIMILARITY"][sim_key]
					if len(sim_list) >= sim_threshold:
						self.app.message_function("BINGO", "success")
				except Exception as e:
					self.app.message_function(traceback.format_exc(), "warning")
					continue












			#if valid == true add the file to the final list
			
			self.filtered_list.append(file)
			self.app.call_from_thread(self.add_filtered_line_function, os.path.basename(filepath))

			self.progress_modal_filtered.advance(1)


		#GET THE CURRENT FOLDER LIST AND CALL FUNCTION FOR CHILDRENS
		for folder in self.app.current_project_data["DATA_FOLDER"][element]["FOLDER_LIST"]:
			
			self.explore_function(os.path.join(element, folder))

			self.progress_modal_filtered.advance(1)

	def add_filtered_line_function(self, message):
		try:
			self.listview_modal_filtered.append(MultiListItem(Label(str(message))))
		except Exception as e:
			self.app.message_function(traceback.format_exc, "error")

	def extend_filtered_line_function(self, message):
		try:
			self.listview_modal_filtered.extend(message)
		except Exception as e:
			self.app.message_function(traceback.format_exc, "error")
		
"""

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
				print("\t%s"%file)


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









class ASPC_ARCHIVE:
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
			index = self.filter_origin_list.index(file)

			if index not in self.listview_modal_filterorigin.index_list:
				self.listview_modal_filterorigin.index_list.append(index)
				self.listview_modal_filterorigin.children[index].highlighted=True

			


		







							





		


	def check_for_archive_function(self):
		#get the current project selected
		self.app.message_function("Checking for archive", "notification")
		if self.current_project_name != None:
			self.app.message_function("Current project selected : %s"%self.current_project_name)

			#check if the key is in the dictionnary
			try:
				archive_data = self.current_project_data["ARCHIVE_DATA"]
				archive_path = archive_data["ARCHIVE_PATH"]
				archive_log = archive_data["ARCHIVE_LOG"]
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






