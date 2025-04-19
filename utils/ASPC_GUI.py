from textual.app import App, ComposeResult
from textual.widgets import Tree, ProgressBar, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

from pathlib import Path
from time import sleep

import datetime
import traceback
import multiprocessing
import threading
import pyfiglet

import sys
import copy
import os
import zipfile

from utils.ASPC_Widgets import MultiListView, MultiListItem



class ASPC_GUI:

	def update_markdown_function(self, mode=None):

		"""
		INFORMATIONS TO DISPLAY
		PROJECT INFORMATIONS:
			name of the project
			size of the project
			number of items
			number of files
			number of folders

		ARCHIVE INFORMATIONS
			path of the archive
			path of the archive log
			number of items in the archive

			total file size contained
			total file size compressed
			extension contained in archive

			creation date of the archive
			last modification date

		SELECTED FOLDER INFORMATION
			number of items contained
			child folders
			child files
			maximum file size
			minimum file size
			extension contained

		SELECTED FILE INFORMATION
			extension of the file
			size of the file
			filepath
			file creation date
			file last modification date
			file size classement
		"""



		markdown_general = ""

		#if mode == "project":
		project_name = os.path.basename(self.current_project_name)
		project_size = self.current_project_data["DATA_FOLDER"][self.current_project_name]["CHILDREN_SIZE"] / (1024 ** 3)
		number_of_files = len(list(self.current_project_data["DATA_FILES"].keys()))
		number_of_folders = len(list(self.current_project_data["DATA_FOLDER"].keys()))-1
		markdown_general += """
# Project global informations
- project name : %s
- project path : %s
- project size : %s Go
- number of file contained : %s
- number of folders contained : %s
""" % (os.path.basename(self.current_project_name), os.path.dirname(self.current_project_name), project_size, number_of_files, number_of_folders)


		#TRY TO UPDATE FOR ARCHIVE IF ARCHIVE PATH IS DEFINED
		if "ARCHIVE_PATH" in self.current_project_data:
			markdown_general += "# Global archive informations"
			try:
				with zipfile.ZipFile(self.current_project_data["ARCHIVE_PATH"], mode="r") as project_archive:

					archive_size = os.path.getsize(self.current_project_data["ARCHIVE_PATH"]) / (1024 ** 3)
					archive_filesize_contained = 0
					archive_compresssize_contained = 0

					number_of_archive_files = len(project_archive.infolist())

					archive_file_max_size = {
						"FILEPATH":None,
						"FILESIZE":float("-inf"),
						"FILECOMPRESS":0
						}
					archive_file_min_size = {
						"FILEPATH":None,
						"FILESIZE":float("inf"),
						"FILECOMPRESS":0
					}

					archive_path = self.current_project_data["ARCHIVE_PATH"]
					archive_log = self.current_project_data["ARCHIVE_LOG"]
					archive_creation = datetime.datetime.fromtimestamp(os.path.getctime(self.current_project_data["ARCHIVE_PATH"]))
					archive_modification = datetime.datetime.fromtimestamp(os.path.getmtime(self.current_project_data["ARCHIVE_PATH"]))

					#get the size informations from file info in archive
					for info in project_archive.infolist():
						archive_filesize_contained += info.file_size
						archive_compresssize_contained += info.compress_size

						if info.file_size > archive_file_max_size["FILESIZE"]:
							archive_file_max_size["FILEPATH"] = info.filename
							archive_file_max_size["FILESIZE"] = info.file_size
							archive_file_max_size["FILECOMPRESS"] = info.compress_size
						if info.file_size <= archive_file_min_size["FILESIZE"]:
							archive_file_min_size["FILEPATH"] = info.filename 
							archive_file_min_size["FILESIZE"] = info.file_size
							archive_file_min_size["FILECOMPRESS"] = info.compress_size

					markdown_general += """
- archive path : %s
- archive log path : %s
- archive creation date : %s
- archive last modification date : %s
\n
- archive size : %s
- archive file size contained : %s Go
- archive file compressed size : %s Go
- number of files in archive : %s
\n
## Smallest file in archive:
- filename : %s
- filesize : %s Go
- compresssize : %s Go
\n
## Largest file in archive:
- filename : %s
- filesize : %s Go
- compresssize : %s Go
""" % (archive_path, archive_log, archive_creation, archive_modification, archive_size, archive_filesize_contained, archive_compresssize_contained, number_of_archive_files, archive_file_min_size["FILEPATH"], archive_file_min_size["FILESIZE"]/(1024**3), archive_file_min_size["FILECOMPRESS"]/(1024**3), archive_file_max_size["FILEPATH"], archive_file_max_size["FILESIZE"]/(1024**3), archive_file_max_size["FILECOMPRESS"]/(1024**3))
			except FileNotFoundError:
				markdown_general += "\n\nDefine an archive path to display archive informations"
				self.message_function("Archive not defined for this project", "notification")	
			except Exception as e:
				markdown_general += "\n\nImpossible to get data from archive\n%s"%traceback.format_exc()
				self.message_function("Impossible to get data from archive\n%s"%traceback.format_exc(), "error")




		#try to get the selection of folder
		markdown_general += "# Informations about selected folder"
		try:
			folder_selected = list(self.current_project_data["DATA_FOLDER"].keys())[self.listview_folders.index]
			folder_data = self.current_project_data["DATA_FOLDER"][folder_selected]

			item_contained = len(folder_data["ITEMS_LIST"])
			file_contained = len(folder_data["FILE_LIST"])
			folder_contained = len(folder_data["FOLDER_LIST"])

			size_contained = folder_data["ITEMS_SIZE"] / (1024 ** 3)
			size_children = folder_data["CHILDREN_SIZE"] / (1024 ** 3)

			markdown_general += """
- selected folder : %s
- number of items contained : %s
- number of files contained : %s
- number of folders contained : %s

## Size contained informations
- size contained in folder : %s
- size contained in folder children : %s
"""%(folder_selected, item_contained, file_contained, folder_contained, size_contained, size_children)

			if type(folder_data["HEAVIEST_FILE"]) == str:
				heaviest_file = folder_data["HEAVIEST_FILE"]
				heaviest_file_size = self.current_project_data["DATA_FILES"][heaviest_file]["FILESIZE"] / (1024 ** 3)

				markdown_general += """
## Largest file in folder
- largest filename : %s
- largest file size : %s Go
"""%(heaviest_file, heaviest_file_size)

			if type(folder_data["LIGHTEST_FILE"]) == str:
				lightest_file = folder_data["LIGHTEST_FILE"]
				lightest_file_size = self.current_project_data["DATA_FILES"][lightest_file]["FILESIZE"] / (1024 ** 3)

				markdown_general += """
## Lightest file in folder
- lightest filename : %s
- lightest file size : %s Go
"""%(heaviest_file, heaviest_file_size)

		except TypeError:
			markdown_general += "\n\nSelect a folder to display data"
			self.message_function("You must select a folder to display data", "notification")

		except Exception as e:
			markdown_general += "\n\nImpossible to get data from selected folder"
			self.message_function("Impossible to get data from folder\n%s"%traceback.format_exc(), "error")




		markdown_general += "# Informations about the selected file"
		try:
			filename = self.current_file_list[self.listview_files.index]
			filepath = os.path.join(self.current_project_name, self.current_folder_selected)

			filedata = self.current_project_data["DATA_FILES"][os.path.join(filepath, filename)]

			markdown_general += """
- filename: %s
- filepath: %s 
- file size: %s Go
- file creation date: %s
"""%(filename, filepath, filedata["FILESIZE"]/(1024**3), filedata["FILECREATION"])
		except TypeError:
			markdown_general += "\n\nSelect a file to display data"
			self.message_function("You must select a file to display data", "notification")
		except KeyError:
			self.message_function("Impossible to find data about file", "error")



		

		#self.markdown_project.update(markdown_general)
		self.markdown_viewer.document.update(markdown_general)







	def update_folder_list_function(self):
		self.message_function("Thread started")

		try:

			#self.call_from_thread(self.add_list_line_function, self.current_project_data["SCAN_DATE"], "listview_folders")
			#self.current_folder_list = (self.current_project_data["DATA_FOLDER"].keys())


			#create the label list
			label_folder_list = []


			folder_min_size = False 
			folder_max_size = False

			folder_list = self.current_project_data["DATA_FOLDER"].keys()

			#get the folder list according to checkbox selection
			if self.checkbox_folder_children.value==True:
				folder_list = [item[0] for item in self.current_project_data["DATA_CHILDREN_SIZE"]]
				folder_min_size = self.current_project_data["DATA_CHILDREN_SIZE"][0][1]
				folder_max_size = self.current_project_data["DATA_CHILDREN_SIZE"][-1][1]

			elif self.checkbox_folder_items.value==True:
				folder_list = [item[0] for item in self.current_project_data["DATA_ITEM_SIZE"]]
				folder_min_size = self.current_project_data["DATA_ITEM_SIZE"][0][1]
				folder_max_size = self.current_project_data["DATA_ITEM_SIZE"][-1][1]

			else:
				folder_min_size = self.current_project_data["DATA_ITEM_SIZE"][0][1] + self.current_project_data["DATA_CHILDREN_SIZE"][0][1]
				folder_max_size = self.current_project_data["DATA_ITEM_SIZE"][-1][1] + self.current_project_data["DATA_CHILDREN_SIZE"][-1][1]

			self.message_function("%s %s"%(self.checkbox_folder_children.value,self.checkbox_folder_items.value))
			self.message_function("Min folder size : %s\nMax folder size : %s"%(folder_min_size, folder_max_size), "message", False)


			#update the value of the current folder list
			self.current_folder_list = list(folder_list)

			#for folder_name, folder_data in self.current_project_data["DATA_FOLDER"].items():
			for folder_name in folder_list:
				folder_data = self.current_project_data["DATA_FOLDER"][folder_name]

				


				#create the folder label 
				if folder_name.replace(self.current_project_name, "") == "":
					label = Label("\\")
				else:
					label = Label(folder_name.replace(self.current_project_name, ""))

				#check if the data still exists in the project

				"""
				if os.path.isdir(folder_name)==False:
					label.styles.color = self.theme_variables["text-secondary"]
				"""

				#check if the color gradient variable is engaged
				if (self.checkbox_folder_gradient.value==True):
					if self.checkbox_folder_children.value==True:
						folder_size = self.current_project_data["DATA_FOLDER"][folder_name]["CHILDREN_SIZE"]
						#gradient_number = ((folder_size - folder_min_size)/(folder_max_size - folder_min_size)) * 100

					elif self.checkbox_folder_items.value==True:
						folder_size = self.current_project_data["DATA_FOLDER"][folder_name]["ITEMS_SIZE"]

					else:
						folder_size = self.current_project_data["DATA_FOLDER"][folder_name]["CHILDREN_SIZE"] + self.current_project_data["DATA_FOLDER"][folder_name]["ITEMS_SIZE"]

					#self.message_function(folder_size, "message")
					try:
						gradient_number = ((folder_size - folder_min_size) / (folder_max_size - folder_min_size)) * 100
					except Exception as e:
						#self.message_function("Impossible to get folder gradient value", "error")
						self.message_function(traceback.format_exc(), "error", False)
						pass
					else:
						#self.message_function("Folder gradient value : %s"%gradient_number, "notification")
						#color the label according to the gradient value
						if (gradient_number <= 10):
							pass
						elif (gradient_number > 10) and (gradient_number <= 45):
							label.styles.color = self.user_settings["COLOR"]["warning"]
						elif (gradient_number > 45) and (gradient_number <= 75):
							label.styles.color = self.user_settings["COLOR"]["important"]
						else:
							label.styles.color = self.user_settings["COLOR"]["alert"]

				try:
					if self.checkbox_folder_items_gradient.value == True:
						#get the min and max value
						min_items_value = self.current_project_data["SCAN_GLOBAL_DATA"]["MIN_ITEMS"]
						max_items_value = self.current_project_data["SCAN_GLOBAL_DATA"]["MAX_ITEMS"]
						#get the current number of children for this folder
						items_number = self.current_project_data["DATA_FOLDER"][folder_name]["ITEMS_NUMBER"]
						#get the ratio
						items_ratio = ((items_number - min_items_value) / (max_items_value - min_items_value)) * 100
						#add a border to the text
						#and adapt the color to the value of the ratio
						if (items_ratio <= 10):
							label.styles.border_left = ("heavy", "white")
						
						elif (items_ratio > 10) and (items_ratio <= 50):
							label.styles.border_left = ("heavy", self.user_settings["COLOR"]["warning"])
						elif (items_ratio > 50) and (items_ratio <= 75):
							label.styles.border_left = ("heavy", self.user_settings["COLOR"]["important"])
						else:
							label.styles.border_left = ("heavy", self.user_settings["COLOR"]["alert"])
					else:
						label.styles.border = None
				except Exception as e:
					self.message_function(traceback.format_exc(), "error")
				else:
					pass





				label_folder_list.append(MultiListItem(label))



			#clear the content of the index list for folders
			self.listview_folders.clear_list()
			#update the content of the listview
			self.call_from_thread(self.listview_folders.extend, label_folder_list)
			#self.current_folder_list = label_folder_list
			"""
			for folder_name, folder_data in self.current_project_data["DATA_FOLDER"].items():
				
				if self.stop_event_folder.is_set():

					return


				self.progress_folder.advance(1)

				if folder_name.replace(self.current_project_name, "") == "":
					label = Label("\\")
				else:
					label = Label(folder_name.replace(self.current_project_name, ""))

				self.current_folder_list.append(folder_name)
				
				if os.path.isdir(folder_name)==False:
					label.styles.color = self.theme_variables["text-error"]
				self.call_from_thread(self.add_list_line_function, label, "listview_folders")
			"""
			

		except Exception as e:
			self.notify(e, timeout=2)










	def update_file_list_function(self, checkbox_change):
		self.message_function("Thread started")

		try:
			self.current_file_list= []


			#APPLY ALL THE FILTERS TO BUILD THE CURRENT FILE LIST TO DISPLAY IN THE LISTVIEW
			list_listitem = []
			#folder_selected = list(self.current_project_data["DATA_FOLDER"].keys())[self.listview_folders.index]
			#CREATE THE SIZE RANGE

			if self.current_project_name == None:
				self.message_function("No project selected, refreshing aborted...", "notification")
				return
			
			#get the size for each file
			try:
				folder_heaviest = self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["HEAVIEST_FILE"]
				folder_lightest = self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["LIGHTEST_FILE"]
				folder_heaviest_size = self.current_project_data["DATA_FILES"][folder_heaviest]["FILESIZE"]
				folder_lightest_size = self.current_project_data["DATA_FILES"][folder_lightest]["FILESIZE"]
			except KeyError:
				pass
			except AttributeError:
				pass

			"""
			heaviest is equivalent to 100%
			lightest is equivalent to 0%
			for each file find the position in this
			"""

			#self.message_function("%s\n%s"%(folder_heaviest_size, folder_lightest_size), "error", False)

		
			if self.checkbox_file_similarity.value == True:
				self.message_function("option1")
				self.current_file_list = []
				similarity_data = self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["SIMILARITY"]
				for key, value in similarity_data.items():
					if len(self.current_file_list) != 0:
						self.current_file_list.append("_"*40)

					for v in value:
						self.current_file_list.append(v)


			elif self.checkbox_file_children.value == True:
				self.message_function("option2")
				
				
				self.current_file_list = self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["FILE_LIST"]
			

				if self.checkbox_file_size.value == True:
					#self.message_function("HELLO WORLD")
					
						data_size_filename = [t[0] for t in self.current_project_data["DATA_FILE_SIZE"]]

						#self.message_function(data_size_filename)
						#self.message_function(self.current_file_list)

						#get the data file size data from the original file size
						for i in range(len(self.current_file_list)):

							if type(self.current_file_list[i]) == str:
								index = data_size_filename.index(os.path.join(self.current_folder_selected,self.current_file_list[i]))
							else:
								index = data_size_filename.index(os.path.join(self.current_folder_selected,self.current_file_list[i][0]))
							self.current_file_list[i] = self.current_project_data["DATA_FILE_SIZE"][index]
							#self.message_function(self.current_file_list[i])

						#sort the final file size
						sorted_data = sorted(self.current_file_list, key=lambda x: x[1])
						self.current_file_list = [os.path.basename(t[0]) for t in sorted_data]
				


			else:
				self.message_function("Getting from data file")
				self.current_file_list = list(self.current_project_data["DATA_FILES"].keys())

			
			self.message_function("Updating file list...", "notification")

			self.progress_files.update(total = len(self.current_file_list))
			#self.call_from_thread(self.progress_folder.update, len(self.current_file_list))

			
			"""
			if checkbox_change == False:
				if self.current_file_list == self.current_file_list_copy:
					self.message_function(self.current_file_list)
					self.message_function(self.current_file_list_copy)
					self.message_function("Both list are similar", "error")
					return
			"""
			

			
			self.call_from_thread(self.listview_files.clear)
			self.current_file_list_copy = copy.copy(self.current_file_list)

			#self.call_from_thread(self.listview_folders.clear)






			#GO THROUGH EACH ELEMENT IN THE CURRENT FILE LIST AND CREATE LABELS AND LISTITEMS
			for file in self.current_file_list:
				if type(file) == list:
					file = file[0]
				#self.message_function("adding file : %s"%file)
				label = Label(os.path.basename(file))

				if file == "_"*40:
					pass

				
				#elif os.path.isfile(os.path.join(folder_selected, file))==False:
				#	label.styles.color = self.theme_variables["text-secondary"]
				

				else:


					#CHECK FIRST IF THE FILE IS ARCHIVED!!!!
					if os.path.isfile(os.path.join(self.current_folder_selected,file))==False:
						self.message_function(os.path.join(self.current_folder_selected,file))
						label.styles.color = "gray"
					else:
						#get data about this file in the current project data
						file_data = self.current_project_data["DATA_FILES"][os.path.join(self.current_folder_selected,file)]
						if ("ARCHIVE" in file_data) and (file_data["ARCHIVE"]==True):
							label.styles.background = self.theme_variables["background"]
							label.styles.width = "1fr"

					
						#check if the gradient checkbox is checked
						if self.checkbox_file_gradient.value==True:
							#apply the gradient for the file
							#find the size of the file
							try:
								file_size = self.current_project_data["DATA_FILES"][os.path.join(self.current_folder_selected,file)]["FILESIZE"]
								gradient_number = ((file_size - folder_lightest_size)/(folder_heaviest_size - folder_lightest_size)) * 100
								#apply the color
								"""
								COLOR RANGE
								0 - 25 -> white
								25 - 50 -> accent
								50 - 75 -> warning
								75 - 100 -> error
								"""
								if (gradient_number <= 25):
									pass
								elif (gradient_number > 25) and (gradient_number <= 50):
									label.styles.color = self.user_settings["COLOR"]["warning"]
								elif (gradient_number > 50) and (gradient_number <= 75):
									label.styles.color = self.user_settings["COLOR"]["important"]
								else:
									label.styles.color = self.user_settings["COLOR"]["alert"]
							except ZeroDivisionError:
								pass
							except UnboundLocalError:
								pass
							#self.message_function(gradient_number)

				if file == "_"*40:
					list_listitem.append(MultiListItem(label, classes="separator"))
				else:
					list_listitem.append(MultiListItem(label))
				self.progress_files.advance(1)

			self.message_function("Refreshing file list...\nThis process can take some while", "notification")

			#clear the content of the list
			self.listview_files.clear_list()
			#update the content of the listview
			self.call_from_thread(self.listview_files.extend, list_listitem)
			#self.call_from_thread(self.add_list_line_function, label, "listview_files")

			#update the file list backup list
			self.current_file_list_copy = copy.copy(self.current_file_list)


		except Exception as e:
			#self.message_function("error")
			self.message_function(traceback.format_exc(), "error")

		else:
			self.message_function("terminated")
		









	def add_list_line_function(self, label, id):
		widget = self.query_one("#%s"%id)
		widget.append(ListItem(label))
		#self.listview_folders.append(ListItem(Label("hello world")))












	def update_directorytree_function(self):


		tree = self.query_one("#directorytree_main")
		root = tree.root
		last_line_init = tree.last_line

		self.message_function(root)

		new_node = self.search_folder_function(tree, root, last_line_init)


		self.message_function(self.query_one("#directorytree_main").last_line)
		



	def search_folder_function(self, tree, root, last_line):
		self.message_function("searching", "notification")

		self.message_function(last_line, "notification")


		for i in range(last_line):
			try:
				tree.scroll_to_line(i, animate=True)
				tree.focus()
				#self.message_function("line : %s"%i)

				node_selected = self.query_one(DirectoryTree).get_node_at_line(i)
				node_path = node_selected.data.path
				self.message_function("%s : %s"%(str(node_path) in str(self.current_folder_selected), node_path))

				if i != 0:
					if (str(node_path) in str(self.current_folder_selected)):
						if node_selected.is_expanded == False:
							self.message_function("NEW FOLDER LOCATED", "notification")
							
							#self.message_function(node_selected.id)
							node_selected.expand_all()
							self.automatic_refresh()

							return node_selected
						else:
							self.message_function("CONTINUE", "error")
							continue
							

					

					
					#self.update_directorytree_function()
				#self.message_function(node_selected)
				

			except Exception as e:
				self.message_function("no line anymore", "error")
				self.message_function(e, "error")
				return




	def reset_folder_children_color_function(self):

		for list_item in self.query_one("#listview_folders").children:
			list_item.children[0].styles.color = "white"


	def highlight_folder_children_function(self):
		#clean all children colors before updating
		for children in self.current_folder_children_list:
			children.styles.background = None

		#clean the children list
		self.current_folder_children_list.clear()

		if self.checkbox_folder_highlight_children.value==True:
			#get all children for the given / selected folder
			list_children = self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["FOLDER_LIST"]
			#get children of the current listview (folders)
			list_listview_children = self.listview_folders.children

			

			#get the index of each children in the current folder list
			for children in list_children:
				self.message_function("children detected : %s"%children)
				children_index = self.current_folder_list.index(os.path.join(self.current_folder_selected,children))
				#get the list item for this index in the listview
				listitem = list_listview_children[children_index]
				#get the label
				label_children = listitem.children[0]
				#color the label
				label_children.styles.background = self.theme_variables["secondary"]
				self.current_folder_children_list.append(label_children)
			#highlight each item/children









	def update_file_list_displaymode_function(self):

		self.message_function("apply changes")
