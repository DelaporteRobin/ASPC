# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.widgets import Tree, ProgressBar, Input, RadioSet, RadioButton, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen, ModalScreen 
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



from utils.ASPC_Log import ASPC_LOG
from utils.ASPC_Snoop import ASPC_SNOOP
from utils.ASPC_Utils import ASPC_UTILS
from utils.ASPC_GUI import ASPC_GUI
from utils.ASPC_Archive import ASPC_ARCHIVE
from utils.ASPC_Widgets import MultiListView, MultiListItem


from pathlib import Path


import copy
import json
import os 
import threading
import traceback





class ModalASPCFilterScreen(ModalScreen, ASPC_UTILS, ASPC_ARCHIVE):
	CSS_PATH = ["styles/layout.tcss"]



	def __init__(self):
		super().__init__()



	def compose(self) -> ComposeResult:

		with VerticalScroll(id = "vertical_modal_container"):
			#self.progress_modal_filtered = ProgressBar(id = "progress_modal_filtered")
			self.listview_modal_filtered = MultiListView(id="listview_modal_filtered")
			#yield self.progress_modal_filtered
			yield self.listview_modal_filtered
			yield Button("ADD ELEMENT", id="button_modal_add")
			yield Button("QUIT", id="button_modal_quit", disabled=False)


	def on_button_pressed(self, event: Button.Pressed) -> None:
		#if event.button.id == "test":
		#	self.display_message_function(self.query("#modal_newcontactname"))

		if event.button.id == "button_modal_quit":
			self.app.pop_screen()

		if event.button.id == "button_modal_add":
			self.add_item_function()




	def add_item_function(self):
		#create the final filtered list
		self.app.message_function(self.listview_modal_filtered.index_list)
		final_filtered_list = []
		for index in self.listview_modal_filtered.index_list:
			final_filtered_list.append(self.filtered_list[index])
		#for each file check if there is already a container in the list
		final_filtered_list_copy = copy.copy(final_filtered_list)

		for file in final_filtered_list_copy:
			for element in self.app.content_to_archive:
				if os.path.isdir(element)==True:
					#check if the given folder is a container of the current file
					#if yes remove the file from the filtered list
					if Path(element).resolve() in Path(file).resolve().parents:
						try:
							final_filtered_list.remove(file)
						except Exception as e:
							self.app.message_function("Impossible to remove file from list\n%s"%file, "error")
							self.app.message_function(traceback.format_exc(), "error")
						else:
							self.app.message_function("File removed because container already in list", "notification")

		#add the filtered list to content to archive
		self.app.content_to_archive.extend(final_filtered_list)
		#extend the listview
		#create listitems
		filtered_item_list = []
		for file in final_filtered_list:
			self.app.message_function("Filtered file added : %s"%file)
			filtered_item_list.append(ListItem(Label(os.path.basename(file))))
		self.app.listview_addarchive_selected.extend(filtered_item_list)
		#pop the screen
		self.app.pop_screen()






	def on_key(self, event:events.Key) -> None:
		if (event.key == "enter") and (self.focused.id == "listview_modal_filtered"):
			children_item = self.listview_modal_filtered.children[self.listview_modal_filtered.index]
			children_item.highlight_item(children_item)


		if (event.key == "space") and (self.focused.id == "listview_modal_filtered"):
			#check if the selection list is empty
			if len(self.listview_modal_filtered.index_list) != 0:
				#get the last index selected
				last_children = self.listview_modal_filtered.index_list[-1]
				#sort the list
				start,end = sorted([last_children,self.listview_modal_filtered.index])
				#intermediate list
				for i in range(start,end):

					if i not in self.listview_modal_filtered.index_list:
						self.listview_modal_filtered.index_list.append(i)
					else:
						self.listview_modal_filtered.index_list.remove(i)
					children_item = self.listview_modal_filtered.children[i]
					children_item.highlight_item(children_item)
					
					#self.app.message_function("appened : %s"%children_item)


	
	def on_mount(self) -> None:
		#launch the thread with selection
		#gather all informations
		filter_dictionnary = {
			"FilterOnlySelected":self.app.checkbox_archive_filter_selected.value,
			"FilterByExtension":self.app.checkbox_archive_filter_extension.value,
			"FilterExtensionList":self.app.input_archive_filter_extension.value.split(" "),
			"FilterBySize":self.app.checkbox_archive_filter_size.value,
			"FilterMinSize":self.app.input_archive_filter_minsize.value,
			"FilterMaxSize":self.app.input_archive_filter_maxsize.value,
			"FilterBySimilarity":self.app.checkbox_archive_filter_similarity.value,
			"FilterSimilarityNumber":self.app.input_archive_filter_similarity.value,
			"FilterByFileNumber":self.app.checkbox_archive_filter_number.value,
			"FilterFileNumber":self.app.input_archive_filter_number.value,
			"FilterByKeyword":self.app.checkbox_archive_filter_keyword.value,
			"FilterKeywordList":self.app.input_archive_filter_keyword.value.split(" "),
			"FilterKeywordListExcluse":self.app.input_archive_filter_exclusekeyword.value.split(" "),
		}
		


		
		

		
			
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


		#LAUNCH THE INIT FILTER FUNCTION
		self.app.message_function("Launching multiprocessing exploration...", "notification")
		with self.app.suspend():
	
			ASPC_ARCHIVE(filter_dictionnary, origin_list, self.app.current_project_data)
			os.system("pause")


		self.filtered_list = []
		self.filtered_multilistitem = []
		#try to read the content of the filtered file if it exists
		try:
			with open("temp_filtered.dll", "r") as read_file:
				self.filtered_list = json.load(read_file)
			os.remove("temp_filtered.dll")
		except Exception as e:
			self.app.message_function("Impossible to get the filtered list", "error")
			self.app.message_function(traceback.format_exc(), "error")
		else:
			self.app.message_function("Filtered list retrived", "success")

			#create the multilistitem list
			for file in self.filtered_list:
				self.filtered_multilistitem.append(MultiListItem(Label(str(os.path.basename(file)))))

			self.listview_modal_filtered.extend(self.filtered_multilistitem)


		#THREAD MODE

		"""
		try:
			thread_filtered = threading.Thread(target=self.check_for_filtered_function, daemon=True, args=(filter_dictionnary,))
			thread_filtered.start()
			#thread_filtered.join()

			#self.query_one("#button_modal_quit").disabled=False
		except Exception as e:
			self.app.message_function(traceback.format_exc(), "error")
		else:
			self.app.message_function("LAUNCHED")
		"""

		#self.listview_modal_filtered.append(ListItem(Label("added")))
	
