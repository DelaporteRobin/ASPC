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
			try:
				index = self.filter_origin_list.index(file)

				if index not in self.listview_modal_filterorigin.index_list:
					self.listview_modal_filterorigin.index_list.append(index)
					self.listview_modal_filterorigin.children[index].highlighted=True
			except ValueError:
				self.app.message_function("Impossible to find item in list : %s"%file, "error")
				self.app.message_function(traceback.format_exc(), "error")

			


		







							





		


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





	def archiving_thread(self):
		#launch notification


		try:
			#self.app.call_from_thread(self.archiving_display_message_function, "hello world")
			self.app.call_from_thread(self.archiving_display_message_function, "Starting archiving process")

			#get the filelist in the listview
			#self.app.content_to_archive
			self.app.call_from_thread(self.archiving_display_message_function, "Number of item to archive : %s"%len(self.app.content_to_archive), "message")
			#get the project selected
			self.app.call_from_thread(self.archiving_display_message_function, "Current project selected : %s"%self.app.current_project_name, "message")
			#get the archive path
			try:
				archive_path = self.app.current_project_data["ARCHIVE_PATH"]
				archive_log = self.app.current_project_data["ARCHIVE_LOG"]
				self.app.call_from_thread(self.archiving_display_message_function, "Archive path : %s"%archive_path, "message")

			except KeyError:
				self.app.call_from_thread(self.archiving_display_message_function, "Archive path not defined", "error")
			else:
				pass
			

		except Exception as e:
			self.app.message_function("Error happened", "error")
			self.app.message_function(traceback.format_exc(), "error")

		else:
			self.app.message_function("Thread terminated", "success")




	def archiving_display_message_function(self, message = "", type="message"):


		if type == "content":
			label = Label("   %s"%message)
		else:
			label = Label("[%s] %s"%(type.upper(),message))


		self.listview_modal_addarchive_filelog.append(ListItem(label))




