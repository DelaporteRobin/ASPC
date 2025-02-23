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


import queue
import time
import copy
import json
import os 
import threading
import traceback





class ModalASPCFilterScreen(ModalScreen, ASPC_UTILS, ASPC_ARCHIVE):
	CSS_PATH = ["styles/layout.tcss"]



	def __init__(self):


		self.filter_origin_list = []
		self.filter_destination_list = []
		self.final_file_list = []
		super().__init__()



	def compose(self) -> ComposeResult:

		with VerticalScroll(id = "vertical_modal_container"):
			with Horizontal(id = "horizontal_modal_container"):
				with VerticalScroll(id = "vertical_modal_container_left"):

					self.progress_filterorigin = ProgressBar(id="progress_filterorigin")
					yield self.progress_filterorigin

					self.listview_modal_filterorigin = MultiListView(id = "listview_modal_filterorigin")
					yield self.listview_modal_filterorigin
					self.listview_modal_filterorigin.border_title = "Origin list"

				with VerticalScroll(id = "vertical_modal_container_right"):

					self.checkbox_archive_filter_extension = Checkbox("Filter by extension", id="checkbox_archive_filter_extension")
					self.input_archive_filter_extension = Input(placeholder = "Extension list", id="input_archive_filter_extension")

					self.checkbox_archive_filter_size = Checkbox("Filter by size", id="checkbox_archive_filter_size")
					self.input_archive_filter_minsize = Input(placeholder = "File min size (Mo)", id="input_archive_filter_minsize", type="integer")
					self.input_archive_filter_maxsize = Input(placeholder = "File max size (Mo)", id="input_archive_filter_maxsize", type="integer")

					#self.checkbox_archive_filter_age = Checkbox("Filter by age", id="checkbox_archive_filter_age")
					self.checkbox_archive_filter_similarity = Checkbox("Filter by similarity", id="checkbox_archive_filter_similarity")
					self.input_archive_filter_similarity = Input(placeholder="similarity number threshold", id="input_archive_filter_similarity", type="integer")

					self.checkbox_archive_filter_number = Checkbox("Filter by file number in folder", id="checkbox_archive_filter_number")
					self.input_archive_filter_number = Input(placeholder="Minimum file number", id="input_archive_filter_number", type="integer")

					self.checkbox_archive_filter_keyword = Checkbox("Filter by keywords", id="checkbox_archive_filter_keyword")
					self.input_archive_filter_keyword = Input(placeholder="Keyword list", id="input_archive_filter_keyword")
					self.checkbox_archive_filter_absolutekeyword = Checkbox("All keywords filter", id = "checkbox_archive_filter_absolutekeyword")
					
					self.checkbox_archive_filter_exclusekeyword = Checkbox("Excluse keywords", id="checkbox_archive_filter_exclusekeyword")
					self.input_archive_filter_exclusekeyword = Input(placeholder="Excluse keyword list", id="input_archive_filter_exclusekeyword")

					yield self.checkbox_archive_filter_extension
					yield self.input_archive_filter_extension

					yield self.checkbox_archive_filter_size
					yield self.input_archive_filter_minsize
					yield self.input_archive_filter_maxsize

					yield self.checkbox_archive_filter_similarity
					yield self.input_archive_filter_similarity

					yield self.checkbox_archive_filter_number
					yield self.input_archive_filter_number

					yield self.checkbox_archive_filter_keyword
					yield self.input_archive_filter_keyword
					yield self.checkbox_archive_filter_absolutekeyword

					yield Rule(line_style="heavy")
					yield self.checkbox_archive_filter_exclusekeyword
					yield self.input_archive_filter_exclusekeyword

					yield Rule(line_style="heavy")

					with RadioSet(id = "radioset_archivefilter_mode"):
						yield RadioButton("Filter all file list")
						yield RadioButton("Filter only filtered elements")



					yield Button("Apply Filter", id="button_applyfilter")
					yield Button("Clear selection", id="button_clearselection")

					yield Rule(line_style="heavy")

					yield Button("Validate selection", id="button_modal_validateselection")

			"""
			#self.progress_modal_filtered = ProgressBar(id = "progress_modal_filtered")
			self.listview_modal_filtered = MultiListView(id="listview_modal_filtered")
			#yield self.progress_modal_filtered
			yield self.listview_modal_filtered
			"""
			yield Button("ADD ELEMENT", id="button_modal_add")
			yield Button("QUIT", id="button_modal_quit", disabled=False)


	def on_button_pressed(self, event: Button.Pressed) -> None:
		#if event.button.id == "test":
		#	self.display_message_function(self.query("#modal_newcontactname"))

		if event.button.id == "button_clearselection":
			self.listview_modal_filterorigin.clear_list()
			self.app.message_function("list : %s"%self.listview_modal_filterorigin.index_list)

			for children in self.listview_modal_filterorigin.children:
				children.highlighted = False

		if event.button.id == "button_modal_validateselection":
			#add the highlighted selection to the listview in the lobby
			filtered_item_list = []
			for index in self.listview_modal_filterorigin.index_list:
				if self.filter_origin_list[index] not in self.app.content_to_archive:
					filtered_item_list.append(ListItem(Label(os.path.basename(self.filter_origin_list[index]))))
					self.app.content_to_archive.append(self.filter_origin_list[index])
			self.app.listview_addarchive_selected.extend(filtered_item_list)
			self.app.pop_screen()



		if event.button.id == "button_applyfilter":
			#create the filter dictionnary
			self.filter_dictionnary = {
				#"FilterOnlySelected":self.checkbox_archive_filter_selected.value,
				"FilterByExtension":self.checkbox_archive_filter_extension.value,
				"FilterExtensionList":self.input_archive_filter_extension.value.split(" "),
				"FilterBySize":self.checkbox_archive_filter_size.value,
				"FilterMinSize":self.input_archive_filter_minsize.value,
				"FilterMaxSize":self.input_archive_filter_maxsize.value,
				"FilterBySimilarity":self.checkbox_archive_filter_similarity.value,
				"FilterSimilarityNumber":self.input_archive_filter_similarity.value,
				"FilterByFileNumber":self.checkbox_archive_filter_number.value,
				"FilterFileNumber":self.input_archive_filter_number.value,
				"FilterByKeyword":self.checkbox_archive_filter_keyword.value,
				"FilterKeywordList":self.input_archive_filter_keyword.value.split(" "),
				"FilterKeywordAbsolute":self.checkbox_archive_filter_absolutekeyword.value,
				"FilterKeywordExclude":self.checkbox_archive_filter_exclusekeyword.value,
				"FilterKeywordListExcluse":self.input_archive_filter_exclusekeyword.value.split(" "),
			}
			self.init_apply_filter_function()

		if event.button.id == "button_modal_quit":
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
					
					#thonself.app.message_function("appened : %s"%children_item)


	
	def on_mount(self) -> None:
		#get the origin sample of files and folders
		#from the checkbox selection on the aspc lobby
		#get only children of the folder selection
		try:
			#clear the list
			origin_folder_list = []
			self.filter_origin_list.clear()
			#clear the listview
			self.listview_modal_filterorigin.clear()
			origin_listitem_list = []

			if self.app.checkbox_filter_fromselection.value==True:
				origin_index_list = self.app.listview_folders.index_list
				for index in origin_index_list:
					origin_folder_list.append(self.app.current_folder_list[index])

				self.progress_filterorigin.total = len(self.filter_origin_list)
				for file in self.app.current_project_data["DATA_FILES"].keys():
					for root_folder in origin_folder_list:
						if Path(root_folder).resolve() in Path(file).resolve().parents:
							self.filter_origin_list.append(file)

					self.progress_filterorigin.advance(1)
			#--> check all folders
			else:
				#create multilistitem list		
				self.filter_origin_list.extend(self.app.current_project_data["DATA_FILES"].keys())



			
			self.progress_filterorigin.total = len(self.filter_origin_list)
			self.progress_filterorigin.progress=0

			for file in self.filter_origin_list:
				origin_listitem_list.append(MultiListItem(Label(os.path.basename(file))))
				self.progress_filterorigin.advance(1)
			self.listview_modal_filterorigin.extend(origin_listitem_list)

		except AttributeError:
			self.app.message_function("You must select a project before launching filter system!", "error")
			self.app.pop_screen()










