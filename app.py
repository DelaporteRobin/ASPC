# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.widgets import Tree, ProgressBar, Input, RadioSet, RadioButton, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
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
#from utils.ASPC_Widgets import HighlightableDirectoryTree, MultiListItem, MultiListView
from utils.ASPC_Widgets import MultiListView, MultiListItem

from styles.theme_file import *




#IMPORT MAIN CLASSES OF CUSTOMIZED WIDGETS FROM TEXTUAL
class HighlightableDirectoryTree(DirectoryTree):
    """DirectoryTree with path highlighting support."""

    class PathNotFoundError(TextualError):
        def __init__(self, path: Path) -> None:
            self.path = path

    def highlight_path(self, path: Path) -> AwaitComplete:
        """Highlight a path in the tree.

        Highlights a path that may be nested several levels deep in the tree.
        This can be done at all times, even when the tree has never been
        expanded and thus the directory contents containing the path have not
        been cached yet. This method will walk the tree, expanding nodes when
        necessary and waiting on the contents before taking another step until
        it arrives at the requested path. The node containing the path is
        subsequently highlighted.

        Args:
            path (Path): the path to highlight.

        Returns:
            AwaitComplete: An optionally awaitable that ensures the path is
                highlighted.
        """
        return AwaitComplete(self._highlight_path(path))

    async def _highlight_path(self, path: Path) -> None:
        """Highlight a path in the tree, while expanding parents.

        Args:
            path (Path): the path to highlight.
        """
        node = await self._expand_parents_and_find_node(path)
        self.move_cursor(node)

    async def _expand_parents_and_find_node(self, path: Path) -> TreeNode[DirEntry]:
        """Traverse all parts of the path and expand all parents.

        This method will traverse all parts of the path and expand all parents
        in the tree when necessary. Finally, the node containing the requested
        path is returned.

        Args:
            path (Path): the requested path that must become visible.

        Returns:
            TreeNode[DirEntry]: the tree node containing the requested path.
        """
        node = self.root
        for part in Path(path).parts:
            node = self._find_node_from_path(node, part)
            if not node.children:
                await self.reload_node(node)
            node.expand()
        return node

    def _find_node_from_path(
        self, parent: TreeNode[DirEntry], path: str
    ) -> TreeNode[DirEntry]:
        """Search a node's children for a specific path.

        The path must be a direct child of the parent. For example, if the
        parent's path is /home/alice, then the path may be /home/alice/work, or
        /home/alice/documents, but _not_ /home/alice/work/software since that is
        not a direct child of /home/alice.

        Args:
            parent (TreeNode[DirEntry]): the parent node.
            path (str): the path to search for.

        Raises:
            PathNotFoundError: raised when the path is not found.

        Returns:
            TreeNode[DirEntry]: the node containing the requested path.
        """
        root = parent.data.path.absolute()
        for node in parent.children:
            if str(node.data.path.relative_to(root)) == path:
                return node
        raise self.PathNotFoundError(path)








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

		self.current_folder_children_list = []
		self.current_folder_list = []
		self.current_file_list = []
		self.current_file_list_copy = []

		self.content_to_archive = []

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
						self.checkbox_folder_highlight_children = Checkbox("Highlight children", id = "checkbox_folder_highlight_children")
						self.checkbox_find_folder = Checkbox("Find in DirTree", id="checkbox_find_folder")
						self.checkbox_folder_children = Checkbox("Sort by children size", id="checkbox_folder_children")
						self.checkbox_folder_items = Checkbox("Sort by items contained size", id="checkbox_folder_items")
						self.checkbox_folder_gradient = Checkbox("Display size gradient", id = "checkbox_folder_gradient")
						self.checkbox_folder_items_gradient = Checkbox("Display items number gradient", id = "checkbox_folder_items_gradient")

						yield self.checkbox_folder_highlight_children
						yield self.checkbox_find_folder
						yield self.checkbox_folder_children
						yield self.checkbox_folder_items
						yield self.checkbox_folder_gradient
						yield self.checkbox_folder_items_gradient

					self.progress_folder = ProgressBar(id="progress_folder")
					yield self.progress_folder

					self.listview_folders = MultiListView(id="listview_folders")
					yield self.listview_folders 
					self.listview_folders.border_title = "Folders list"

				with Vertical(id = "vertical_container_center_right"):

					with Collapsible(title="File Display Settings", id="collapsible_file_display"):
						self.checkbox_file_size = Checkbox("Sort by size", id="checkbox_file_size")
						self.checkbox_file_children = Checkbox("Only folder children's", id="checkbox_file_children")
						self.checkbox_file_gradient = Checkbox("Display size gradient", id="checkbox_size_gradient")
						self.checkbox_file_similarity = Checkbox("Display by similarity", id="checkbox_file_similarity")

						yield self.checkbox_file_similarity
						yield self.checkbox_file_size
						yield self.checkbox_file_children
						yield self.checkbox_file_gradient
						

					self.progress_files = ProgressBar(id="progress_files")
					yield self.progress_files

					self.listview_files = MultiListView(id = "listview_files")
					yield self.listview_files
					self.listview_files.border_title = "Files list"





			with VerticalScroll(id = "verticalscroll_container_right"):
				with TabbedContent(id = "tabbedcontent_right"):
					with TabPane(title = "ARCHIVE CONTENT", id = "tabpane_archive"):

						with Horizontal(id = "tab_horizontal_archivecontent"):
							with VerticalScroll(id = "tab_vertical_archivecontent_left"):

								self.listview_addarchive_selected = MultiListView(id="listview_addarchive_selected")
								yield self.listview_addarchive_selected
								self.listview_addarchive_selected.border_title = "Items to archive"

								with VerticalScroll(id = "tab_vertical_archiveoptions"):
									yield Button("Clear Items in list", id = "button_addarchive_clearlist")

									yield Rule(line_style="heavy")

									yield Button("Add selected folder", id="button_addarchive_selectedfolder")
									yield Button("Add selected files", id ="button_addarchive_selectedfiles")
									
									yield Rule(line_style="heavy")

									with Collapsible(title="FILTERS", id="collapsible_archive_filters"):

										self.checkbox_archive_filter_foldertarget = Checkbox("Filter only on selected folders", id="checkbox_archive_filter_foldertarget")

										self.checkbox_archive_filter_extension = Checkbox("Filter by extension", id="checkbox_archive_filter_extension")
										self.input_archive_filter_extension = Input(placeholder = "Extension list", id="input_archive_filter_extension")

										self.checkbox_archive_filter_size = Checkbox("Filter by size", id="checkbox_archive_filter_size")
										self.input_archive_filter_size = Input(placeholder = "File size threshold", id="input_archive_filter_size", type="integer")

										#self.checkbox_archive_filter_age = Checkbox("Filter by age", id="checkbox_archive_filter_age")
										self.checkbox_archive_filter_similarity = Checkbox("Filter by similarity", id="checkbox_archive_filter_similarity")
										self.input_archive_filter_similarity = Input(placeholder="similarity number threshold", id="input_archive_filter_similarity", type="integer")

										self.checkbox_archive_filter_number = Checkbox("Filter by file number in folder", id="checkbox_archive_filter_number")
										self.input_archive_filter_number = Input(placeholder="Minimum file number", id="input_archive_filter_number", type="integer")

										self.checkbox_archive_filter_keyword = Checkbox("Filter by keywords", id="checkbox_archive_filter_keyword")
										self.input_archive_filter_keyword = Input(placeholder="Keyword list", id="input_archive_filter_keyword")

										
										yield self.checkbox_archive_filter_foldertarget

										yield Rule(line_style="heavy")

										yield self.checkbox_archive_filter_extension
										yield self.input_archive_filter_extension

										yield self.checkbox_archive_filter_size
										yield self.input_archive_filter_size

										yield self.checkbox_archive_filter_similarity
										yield self.input_archive_filter_similarity

										yield self.checkbox_archive_filter_number
										yield self.input_archive_filter_number

										yield self.checkbox_archive_filter_keyword
										yield self.input_archive_filter_keyword

										yield Rule(line_style="heavy")

										with RadioSet(id = "radioset_archivefilter_mode"):
											yield RadioButton("Replace selection")
											yield RadioButton("Add to selection")



										yield Button("Apply Filter", id="button_addarchive_applyfilter")
										yield Button("Highlight Filtered", id="button_addarchive_highlightfiltered")
										yield Button("Add Filtered Items", id="button_addarchive_addfiltered")

									yield Rule(line_style="heavy")

	

									yield Button("Add to archive", id="button_add_to_archive")


							with Vertical(id = "tab_vertical_archivecontent_right"):
								self.listview_archive_content = MultiListView(id="listview_archive_content")
								yield self.listview_archive_content
								self.listview_archive_content.border_title = "Archive content"

					with TabPane(title = "FOLDER INFORMATIONS", id = "tabpane_folderinformation"):
						yield Label("folder informations tab")

					with TabPane(title = "LOG", id = "tabpane_log"):
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

		if (event.key == "enter") and (self.focused.id == "listview_folders"):
			children_item = self.listview_folders.children[self.listview_folders.index]
			children_item.highlight_item(children_item)

		










			
			





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

		if (event.control.id == "checkbox_file_similarity"):
			self.checkbox_file_size.disabled = self.checkbox_file_similarity.value

		if (event.control.id == "checkbox_folder_items") and (self.checkbox_folder_items.value==True):
			self.checkbox_folder_children.value = not self.checkbox_folder_items.value
		if (event.control.id == "checkbox_folder_children") and (self.checkbox_folder_children.value==True):
			self.checkbox_folder_items.value = not self.checkbox_folder_children.value

		if event.control.id in ["checkbox_file_size", "checkbox_file_children", "checkbox_size_gradient", "checkbox_file_similarity"]:
			self.check_for_file_process_function(True)

		if event.control.id in ["checkbox_folder_items", "checkbox_folder_gradient", "checkbox_folder_children", "checkbox_folder_items_gradient"]:
			self.check_for_folder_process_function(True)

		





	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "test_log":
			self.message_function(self.current_folder_selected)



		#add archive buttons
		if event.button.id == "button_addarchive_selectedfiles":
			#get selected files
			selected_files_label = []
			selected_index = self.listview_files.index_list

			#get the last folder selected to build the full path for each file
			selected_folder = self.current_folder_list[self.listview_folders.index]

			#self.message_function("CURRENT FOLDER\n%s"%selected_folder, "notification",False)
			try:
				for index in selected_index:
					filepath = os.path.join(selected_folder,self.current_file_list[index])
					label = Label(os.path.basename(filepath))

					if os.path.isfile(filepath)==False:
						label.styles.color = self.theme_variables["text-secondary"]
					self.content_to_archive.append(filepath)
					selected_files_label.append(ListItem(label))
			except IndexError:
				self.message_function("Filelist content has changed", "warning")
			

			self.listview_addarchive_selected.extend(selected_files_label)

		if event.button.id == "button_addarchive_selectedfolder":

			selected_folder_label = []
			selected_index = self.listview_folders.index_list

			for index in selected_index:
				folder = self.current_folder_list[index]
				label = Label(os.path.basename(folder))

				if os.path.isdir(folder)==False:
					label.styles.color = self.theme_variables["text-secondary"]

				self.content_to_archive.append(folder)
				selected_folder_label.append(ListItem(label))

			self.listview_addarchive_selected.extend(selected_folder_label)
			



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





	def check_for_folder_process_function(self, checkbox_change=False):

		self.message_function("hello world : %s"%self.listview_projectlist.index)
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
		try:
			self.current_project_name = self.project_list[self.listview_projectlist.index][1]
			#get the current project data
			self.current_project_data = self.project_data[self.current_project_name]
			#self.message_function(len(list(self.project_data[self.current_project_name]["DATA_FOLDER"].keys())))   
		except TypeError:
			return
		
		
		self.progress_folder.update(progress=0)
		self.progress_folder.update(total = len(list(self.project_data[self.current_project_name]["DATA_FOLDER"].keys())))
		
		try:
			
			self.thread_update_folder_list = threading.Thread(target=self.update_folder_list_function, daemon=True, args=())
			self.stop_event_folder.clear()  
			self.thread_update_folder_list.start()
		except Exception as e:
			self.message_function("Impossible to start thread", "error")
			self.message_function(e, "error")







	def on_list_view_selected(self, event: ListView.Selected) -> None:
		self.message_function("%s\n\n"%("_"*120), "message", False)
		if event.control.id == "listview_projectlist":
			#update the dictory tree starting folder
			self.input_global_root_path.value = self.project_list[self.listview_projectlist.index][1]
			self.directorytree_main.path = self.project_list[self.listview_projectlist.index][1]
			#self.update_dir_tree_starting_folder(self.project_list[self.listview_projectlist.index][1])

			#call the threading checking function
			self.check_for_folder_process_function()

		


		if event.control.id == "listview_folders":
			

			self.current_folder_selected = self.current_folder_list[self.listview_folders.index]
			#self.message_function(self.current_folder_selected, "message", False)
			#display information about the selected widget
			label = event.control.children[self.listview_folders.index].children[0]
			#self.message_function(label.styles.color)
			#self.message_function(label.styles.border_left)


			#find folder in directory tree
			if (self.checkbox_find_folder.value == True):
				path = (self.current_folder_selected.replace(self.current_project_name, "")).replace("\\", "/").lstrip("/")
				#self.message_function(path)
				tree = self.query_one(HighlightableDirectoryTree)
				try:
					node = tree.highlight_path(path)
					tree.focus()
				except Exception as e:
					self.message_function("Impossible to focus directory in tree", "error")
					self.message_function(traceback.format_exc(), "error")
				else:
					self.message_function("Folder node found in tree : %s"%node, "success")
						



			#call function to update the file list content
			self.check_for_file_process_function()
			#call function to highlight children if highlight children is checked
			self.highlight_folder_children_function()








			

			




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