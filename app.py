# -*- coding: utf-8 -*-


from textual.app import App, ComposeResult
from textual.widgets import Tree, ProgressBar, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual.await_complete import AwaitComplete
from textual.await_remove import AwaitRemove
from textual.binding import Binding, BindingType
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive
from textual.await_complete import AwaitComplete 
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode
from textual.errors import TextualError
from textual.widgets._list_item import ListItem
from textual.widget import AwaitMount, Widget


from pathlib import Path
from time import sleep

import multiprocessing
import threading
import pyfiglet

import sys
import copy
import os

from config import *


from utils.ASPC_Log import ASPC_LOG
from utils.ASPC_Snoop import ASPC_SNOOP
from utils.ASPC_Utils import ASPC_UTILS
from utils.ASPC_GUI import ASPC_GUI
from utils.ASPC_Widgets import HighlightableDirectoryTree, MultiListItem, MultiListView

from styles.theme_file import *






class ASPC_HOMEPAGE(Screen):


	CSS_PATH = ["styles/layout.tcss"]


	def compose(self) -> ComposeResult:

		with Horizontal(id = "homepage_horizontal_container"):
			with Vertical(id = "homepage_vertical_container"):
				
				yield Static(pyfiglet.figlet_format("AUSPICIOUS", font=ASCII_FONT_HOMEPAGE), classes="static_title_homepage")

				with Vertical(id = "homepage_info_container"):
					yield Label(str("AUSPICIOUS v%s"%VERSION), classes="homepage_label_info")
					yield Label(str("Writen by %s"%AUTHOR), classes="homepage_label_info")
					yield Label(str("Star the repository :\n%s"%REPO), classes="homepage_label_info")


				yield Button("OPEN ASPC", id="homepage_button_open")



	def on_button_pressed(self, event:Button.Pressed) -> None:
		if event.button.id == "homepage_button_open":
			#kill the screen
			self.app.pop_screen()

	









class ASPC_MAIN(App, ASPC_LOG, ASPC_SNOOP, ASPC_UTILS, ASPC_GUI):


	CSS_PATH = ["styles/layout.tcss"]


	def __init__(self):
		super().__init__()

		self.global_root_path = Path("/")
		self.global_log = []
		self.global_log_backup = []

		self.selected_item = None

		self.build_path = None
		self.current_focused_folder = Path("/")
		self.current_project_name = None
		self.current_folder_selected = None

		self.current_folder_list = []
		self.current_file_list = []
		self.current_file_list_copy = []

		self.project_data = {}
		self.project_list = []

		self.stop_event_folder = threading.Event()
		self.stop_event_file = threading.Event()
		self.thread_update_folder_list = threading.Thread()
		self.thread_update_file_list = threading.Thread()


		#LOAD USER SETTINGS
		#OR CREATE IT
		#THAT IS THE QUESTION

		#first init user settings dictionnary
		self.user_settings = {}
		



		self.color_dictionnary = self.theme_variables

		





	def compose(self) -> ComposeResult:
		yield Header(show_clock=True)


		with Horizontal(id = "horizontal_container_main"):
			with VerticalScroll(id = "verticalscroll_container_left"):
				#file / folder explorer
				#define the 3d project folder
				#locate files in folder structure
				with Collapsible(title = "Project List", id="collapsible_project_list", collapsed=False):
					self.listview_projectlist = ListView(id="listview_projectlist")
					yield self.listview_projectlist

					yield Button("CRASHTEST", id="test_log")
					yield Button("Remove project from list", id="button_remove_project")
				self.input_global_root_path = Input(placeholder="Starting folder", id="input_global_root_path")
				yield self.input_global_root_path

				self.directorytree_main = HighlightableDirectoryTree(self.global_root_path, id="directorytree_main")
				yield self.directorytree_main

				self.label_global_root_path = Label("", id="label_global_root_path")
				yield self.label_global_root_path

				yield Button("ADD TO LIST AND\nEXPLORE PROJECT", id="button_explore_project")


			
			with Horizontal(id = "horizontal_container_center"):
				with Vertical(id = "vertical_container_center_left"):
					with Collapsible(title = "Folder Display Settings", id="collapsible_folder_display"):
						self.checkbox_find_folder = Checkbox("Find in DirTree", id="checkbox_find_folder")

						yield self.checkbox_find_folder

					self.progress_folder = ProgressBar(id="progress_folder")
					yield self.progress_folder

					self.listview_folders = ListView(id="listview_folders")
					yield self.listview_folders 
					self.listview_folders.border_title = "Folders list"

				with Vertical(id = "vertical_container_center_right"):

					with Collapsible(title="File Display Settings", id="collapsible_file_display"):
						self.checkbox_file_size = Checkbox("Sort by size", id="checkbox_file_size")
						self.checkbox_file_children = Checkbox("Only folder children's", id="checkbox_file_children")
						self.checkbox_file_gradient = Checkbox("Display size gradient", id="checkbox_size_gradient")

						yield self.checkbox_file_size
						yield self.checkbox_file_children
						yield self.checkbox_file_gradient

					self.progress_files = ProgressBar(id="progress_files")
					yield self.progress_files

					self.listview_files = MultiListView(id = "listview_files")
					yield self.listview_files
					self.listview_files.border_title = "Files list"





			with VerticalScroll(id = "verticalscroll_container_right"):
				self.listview_log = ListView(id = "listview_log")
				yield self.listview_log






	def on_mount(self) -> None:
		


		#self.read_log_thread = threading.Thread(target=self.read_log_function, daemon=True,args=())
		#self.read_log_thread.start()


		self.message_function("Log thread activated", "success")


		self.load_project_data_function()
		self.load_user_settings_function()


		for i in range(10):
			self.listview_files.append(MultiListItem(Label("hello world")))


		for checkbox_id, checkbox_value in self.user_settings["WIDGETS"].items():
			try:
				self.query_one("#%s"%checkbox_id).value = checkbox_value
			except Exception as e:
				self.message_function("Impossible to load value for widget : %s"%checkbox_id, "error")
			else:
				self.message_function("Value loaded for widget : %s"%checkbox_id, "notification")


		#install screens
		self.install_screen(ASPC_HOMEPAGE(), name="ASPC_HOMEPAGE")
		#push the homepage screen
		#self.push_screen("ASPC_HOMEPAGE")






	def on_key(self, event:events.Key) -> None:
		if (event.key == "enter") and (self.focused.id == "listview_files"):
			children_item = self.listview_files.children[self.listview_files.index]
			children_item.highlight_item(children_item)

		







	def on_list_view_selected(self, event: ListView.Selected) -> None:
		self.message_function("%s\n\n"%("_"*120), "message", False)
		if event.control.id == "listview_projectlist":
			#update the dictory tree starting folder
			self.input_global_root_path.value = self.project_list[self.listview_projectlist.index][1]
			self.directorytree_main.path = self.project_list[self.listview_projectlist.index][1]
			#self.update_dir_tree_starting_folder(self.project_list[self.listview_projectlist.index][1])

		
			#self.message_function("hello world : %s"%self.listview_projectlist.index)
			if self.thread_update_folder_list.is_alive():
				self.stop_event_folder.set()
				self.stop_event_folder.wait()
				#self.thread_update_list.join()
				return
			


			self.listview_folders.clear()
			self.listview_files.clear()
			 
			

			#clean the folder list
			self.current_folder_list = []


			#get the project name
			self.current_project_name = self.project_list[self.listview_projectlist.index][1]
			#get the current project data
			self.current_project_data = self.project_data[self.current_project_name]
			#self.message_function(len(list(self.project_data[self.current_project_name]["DATA_FOLDER"].keys())))   
			
			
			self.progress_folder.update(progress=0)
			self.progress_folder.update(total = len(list(self.project_data[self.current_project_name]["DATA_FOLDER"].keys())))
			
			try:
				
				self.thread_update_folder_list = threading.Thread(target=self.update_folder_list_function, daemon=True, args=())
				self.stop_event_folder.clear()  
				self.thread_update_folder_list.start()
			except Exception as e:
				self.message_function("Impossible to start thread", "error")
				self.message_function(e, "error")



		if event.control.id == "listview_folders":
			
			self.current_folder_selected = list(self.current_project_data["DATA_FOLDER"].keys())[self.listview_folders.index]


			#find folder in directory tree
			if (self.checkbox_find_folder.value == True):
				path = (self.current_folder_selected.replace(self.current_project_name, "")).replace("\\", "/").lstrip("/")
				#self.message_function(path)
				tree = self.query_one(HighlightableDirectoryTree)
				node = tree.highlight_path(path)
				tree.focus()

 

			self.reset_folder_children_color_function()
			self.highlight_folder_children_function()
			#self.query_one("#directorytree_main").focus()
			#self.update_directorytree_function()
			self.check_for_file_process_function()


			
			





	def get_tree_children(self, path):
		for children in path.children:
			self.message_function(children.label)
			self.dir_tree_children(children)






	def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
		#update the value in the dictionnary
		widget_dictionnary = self.user_settings["WIDGETS"]
		widget_dictionnary[event.control.id] = event.control.value
		self.user_settings["WIDGETS"] = widget_dictionnary
		#save the new setting file
		self.save_user_settings_function()

		if event.control.id in ["checkbox_file_size", "checkbox_file_children", "checkbox_size_gradient"]:
			self.check_for_file_process_function(True)






	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "test_log":
			self.message_function(self.current_folder_selected)
			



		if event.button.id == "button_explore_project":
			#get the path of the project
			self.message_function("Launching multiprocessing exploration...", "notification")
			with self.suspend():
				ASPC_SNOOP(self.selected_item)
				os.system("pause")

			self.message_function("Multiprocessing exploration done", "success")

		
			#reset all lists
			self.message_function("Trying to refresh project list")
			self.listview_projectlist.clear()
			value = self.load_project_data_function()
			if value == False:
				self.message_function("Project list refresh failed", "error")
			else:
				self.message_function("Project list refreshed", "success")


			"""
			self.listview_projectlist.clear()
			
			#load project data
			self.message_function("Refresh project list")
			value = self.load_project_data_function()
			"""






	def check_for_file_process_function(self, checkbox_change=False):
		#update the dictory tree
		
		if self.thread_update_file_list.is_alive():
			self.stop_event_file.set()
			self.stop_event_file.wait()
			return

		#self.listview_files.clear()

		#current folder selection
		
		#self.progress_files.update(total = len(self.current_project_data["DATA_FOLDER"][self.current_folder_selected]["FILE_LIST"]))
		self.progress_files.update(progress=0)


		
		try:
			self.thread_update_file_list = threading.Thread(target=self.update_file_list_function, daemon=True, args=(checkbox_change,))
			self.stop_event_file.clear()
			self.thread_update_file_list.start()
		except Exception as e:
			self.message_function("Impossible to start thread", "error")
			self.message_function(e,"error")









			

			




	def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
		self.selected_item = event.path
		
		
		
	def on_directory_tree_file_selected(self, event:DirectoryTree.FileSelected) -> None:
		self.selected_item = event.path





	def on_input_submitted(self, event:Input.Submitted) -> None:
		if event.input.id == "input_global_root_path":
			if os.path.isdir(self.input_global_root_path.value)==True:
				self.directorytree_main.path = self.input_global_root_path.value
				self.message_function("Starting folder updated\n%s"%self.input_global_root_path.value, "notification")
			else:
				self.message_function("Folder doesn't exists\n%s"%self.input_global_root_path.value, "error")









if __name__ == "__main__":
	App = ASPC_MAIN()
	App.run()