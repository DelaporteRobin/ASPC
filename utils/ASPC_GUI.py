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

import traceback
import multiprocessing
import threading
import pyfiglet

import sys
import copy
import os





class ASPC_GUI:




	def update_folder_list_function(self):
		self.message_function("Thread started")

		try:

			#self.call_from_thread(self.add_list_line_function, self.current_project_data["SCAN_DATE"], "listview_folders")
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
			

		except Exception as e:
			self.notify(e, timeout=2)








	def update_file_list_function(self, checkbox_change):
		self.message_function("Thread started")


		self.current_file_list = []


		#APPLY ALL THE FILTERS TO BUILD THE CURRENT FILE LIST TO DISPLAY IN THE LISTVIEW
		list_listitem = []
		folder_selected = list(self.current_project_data["DATA_FOLDER"].keys())[self.listview_folders.index]
		#CREATE THE SIZE RANGE
		folder_heaviest = self.current_project_data["DATA_FOLDER"][folder_selected]["HEAVIEST_FILE"]
		folder_lightest = self.current_project_data["DATA_FOLDER"][folder_selected]["LIGHTEST_FILE"]
		#get the size for each file
		folder_heaviest_size = self.current_project_data["DATA_FILES"][folder_heaviest]["FILESIZE"]
		folder_lightest_size = self.current_project_data["DATA_FILES"][folder_lightest]["FILESIZE"]
		"""
		heaviest is equivalent to 100%
		lightest is equivalent to 0%
		for each file find the position in this
		"""

		#self.message_function("%s\n%s"%(folder_heaviest_size, folder_lightest_size), "error", False)

		try:
			if self.checkbox_file_children.value == True:
				
				
				self.current_file_list = self.current_project_data["DATA_FOLDER"][folder_selected]["FILE_LIST"]
			

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
				self.current_file_list = self.current_project_data["DATA_FILES"]

			
			self.message_function("Updating file list\n%s"%self.current_file_list, "notification")

			self.progress_files.update(total = len(self.current_file_list))
			#self.call_from_thread(self.progress_folder.update, len(self.current_file_list))

			
			if checkbox_change == False:
				if self.current_file_list == self.current_file_list_copy:
					self.message_function("Both list are similar", "error")
					return

			
			self.call_from_thread(self.listview_files.clear)
			self.current_file_list_copy = copy.copy(self.current_file_list)

			#self.call_from_thread(self.listview_folders.clear)






			#GO THROUGH EACH ELEMENT IN THE CURRENT FILE LIST AND CREATE LABELS AND LISTITEMS
			for file in self.current_file_list:
				if type(file) == list:
					file = file[0]
				#self.message_function("adding file : %s"%file)
				label = Label(os.path.basename(file))

				#self.current_file_list.append(file)
				if os.path.isfile(os.path.join(folder_selected, file))==False:
					label.styles.color = self.theme_variables["text-secondary"]
				else:
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
						#self.message_function(gradient_number)

				list_listitem.append(ListItem(label))
				self.progress_files.advance(1)

			self.message_function("Refreshing file list...\nThis process can take some while", "notification")
			self.call_from_thread(self.listview_files.extend, list_listitem)
			#self.call_from_thread(self.add_list_line_function, label, "listview_files")

			#update the file list backup list
			self.current_file_list_copy = copy.copy(self.current_file_list)


		except Exception as e:
			self.message_function(traceback.format_exc(), "error")
		









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
		self.message_function("Checking children from folder selection\n%s"%self.current_folder_selected, "notification")

		#get all children in the folder listview
		#self.message_function(self.current_folder_selected, "notification")
		children_list = self.query_one("#listview_folders").children

		for i in range(len(self.current_folder_list)):
			if self.current_folder_list[i].startswith(self.current_folder_selected):
				#self.message_function("detected : %s"%self.current_folder_list[i], "notification")
				label = children_list[i].children[0]
				label.styles.color = self.theme_variables["text-accent"]











	def update_file_list_displaymode_function(self):

		self.message_function("apply changes")
