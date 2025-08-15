# -*- coding: utf-8 -*-
from textual.app import App, ComposeResult
from textual.widgets import Sparkline, Tree, ProgressBar, Input, RadioSet, MarkdownViewer, RadioButton, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
#from textual.widgets.option_list import Option, Separator
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
from textual.binding import Binding
#import textual_pyfiglet
from textual_pyfiglet import FigletWidget
from textual_plotext import PlotextPlot


from pathlib import Path
from time import sleep

import multiprocessing
import threading
import traceback
import pyfiglet

import sys
import copy
import os

from config import *

from utils.ASPC_Log import ASPC_LOG
from utils.ASPC_Snoop import ASPC_SNOOP
from utils.ASPC_Utils import ASPC_UTILS
from utils.ASPC_GUI import ASPC_GUI
from utils.ASPC_Archive import ASPC_ARCHIVE, ASPC_FILL_ARCHIVE
from modal import ModalASPCFilterScreen
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


class ASPC_HOMEPAGE(ModalScreen):


	CSS_PATH = ["styles/layout.tcss"]
	def __init__(self, theme_dictionnary):
		super().__init__()
		self.THEME = theme_dictionnary

		self.welcome_page_text = """


[bold]AUSPICIOUS[/bold] VERSION V%s
Writen by [bold][%s]%s[/%s][/bold]
Github Repository → %s
[bold]Don't hesitate to star the Repository :)[/bold]

[italic][bold]Thank you for downloading AUSPICIOUS
Hope it will be useful to you[/bold][/italic]
"""%(VERSION,self.THEME.primary,AUTHOR,self.THEME.primary,REPO)

	def compose(self) -> ComposeResult:

		with Horizontal(id= "homepage_horizontal_container"):
			with Vertical(id = "homepage_vertical_container"):
				
				#yield Static(pyfiglet.figlet_format("AUSPICIOUS", font=ASCII_FONT_HOMEPAGE), classes="static_title_homepage")
				yield FigletWidget("AUSPICIOUS", font=ASCII_FONT_HOMEPAGE, justify="center", colors=["$primary", "$secondary", "$background","$panel"], animate=True, gradient_quality=30, id="homepage_title")

				with Vertical(id = "homepage_info_container"):
					"""
					yield Label(str("AUSPICIOUS v%s"%VERSION), classes="homepage_label_info")
					yield Label(str("Writen by %s"%AUTHOR), classes="homepage_label_info")
					yield Label(str("Star the repository :\n%s"%REPO), classes="homepage_label_info")
					"""
					yield Static(self.welcome_page_text, id="static_welcome_text")


				yield Button("OPEN ASPC", id="homepage_button_open")



	def on_button_pressed(self, event:Button.Pressed) -> None:
		if event.button.id == "homepage_button_open":
			#kill the screen
			self.app.pop_screen()


class ModalASPCCreateArchive(ModalScreen, ASPC_UTILS):
	CSS_PATH = ["styles/layout.tcss"]

	def __init__(self):

		super().__init__()


	def compose(self) -> ComposeResult:

		with VerticalScroll(id = "modal_archive_vertical_container"):

			yield Label("No archive detected for this project\nDo you want to create a new one?", id="label_modal_question")

			self.input_modal_archive_path = Input(placeholder = "Archive path", id = "input_modal_archive_path")
			#self.input_modal_archivelog_path = Input(placeholder = "Archive log path", id="input_modal_archivelog_path")
			yield self.input_modal_archive_path
			#yield self.input_modal_archivelog_path

			with Horizontal(id = "modal_archive_horizontal_container"):
				yield Button("Create", id="button_modal_create_archive")
				yield Button("Dismiss", id="button_modal_dismiss_archive")


	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button_modal_dismiss_archive":
			self.dismiss(True)

		if event.button.id == "button_modal_create_archive":

			if self.app.current_project_name == None:
				self.app.message_function("You must select a project to create an archive!")
				return
			#check if the path is correct
			if os.path.isdir(self.input_modal_archive_path.value)==False:
				self.app.message_function("The path isn't valid!", "error")

			else:
				try:
					self.app.project_data[self.app.current_project_name]["ARCHIVE_PATH"] = os.path.join(self.input_modal_archive_path.value, "ASPC_Archive_%s.zip"%os.path.basename(self.app.current_project_name))
					#archive log file located next to the archive
					#self.app.project_data[self.app.current_project_name]["ARCHIVE_LOG"] = os.path.join(self.input_modal_archive_path.value, "ASPC_ArchiveLog_%s"%os.path.basename(self.app.current_project_name))
					
					#archive log file located in data
					self.app.project_data[self.app.current_project_name]["ARCHIVE_LOG"] = os.path.join(os.getcwd(), "data/ASPC_ArchiveLog_%s.json"%os.path.basename(self.app.current_project_name))

					#save the content of the new project dictionnary in file
					self.save_dictionnary_function()


				except Exception as e:
					self.app.message_function("Impossible to save the archive path", "error")
					self.app.message_function(traceback.format_exc(), "error")
				else:
					self.app.message_function(os.path.basename(self.app.current_project_name), "success")

					self.dismiss(False)


class ModalASPCRemoveProject(ModalScreen):
	CSS_PATH = ["styles/layout.tcss"]

	def __init__(self):
		super().__init__()


	def compose(self) -> ComposeResult:
		with Vertical(id = "modal_archive_vertical_container"):
			yield Label("Before removing the project\nDo you want to restore the content of the project archive")
			with Horizontal(id = "horizontal_modal_removearchive"):
				yield Button("YES", id="button_modal_removearchive_true")
				yield Button("NO", id="button_modal_removearchive_false")
			yield Button("QUIT", id="button_modal_removearchive_quit")

	def on_button_pressed(self, event:Button.Pressed) -> None:
		if event.button.id == "button_modal_removearchive_quit":
			self.app.pop_screen()
		elif event.button.id == "button_modal_removearchive_true":
			self.dismiss(True)
		elif event.button.id == "button_modal_removearchive_false":
			self.dismiss(False)


class ModalASPCAddToArchive(ModalScreen, ASPC_ARCHIVE, ASPC_FILL_ARCHIVE, ASPC_UTILS):
	CSS_PATH = ["styles/layout.tcss"]


	def __init__(self, THEME_DICTIONNARY):
		self.THEME_DICTIONNARY = THEME_DICTIONNARY
		super().__init__()


	def compose(self) -> ComposeResult:
		with Vertical(id = "vertical_modal_addarchive"):

			self.listview_modal_addarchive_filelog = ListView(id = "listview_modal_addarchive_filelog")
			yield self.listview_modal_addarchive_filelog
			self.listview_modal_addarchive_filelog.border_title = "Archiving log"
					
			yield Button("QUIT", id="button_modal_quit")


	def on_button_pressed(self, event:Button.Pressed) -> None:
		if event.button.id == "button_modal_quit":
			self.app.pop_screen()



	def on_mount(self):

		#THREAD MODE
		"""
		try:
			self.thread_archiving = threading.Thread(target=self.archiving_thread, args=())
			#call the thread
			self.thread_archiving.start()
		except Exception as e:
			self.app.message_function("Impossible to launch archiving thread", "error")
			self.app.message_function(traceback.format_exc(), "error")
		else:
			self.app.message_function("Archiving thread launched", "success")
		"""


		self.app.message_function("Archiving process started", "notification")
		#MULTIPROCESSING MODE
		#create instance of the archiving class
		with self.app.suspend():
			#fill_archive = ASPC_FILL_ARCHIVE(self.app.content_to_archive, self.app.current_project_name, self.app.current_project_data)
			fill_archive = ASPC_FILL_ARCHIVE(self.THEME_DICTIONNARY, self.app.user_settings, self.app.content_to_archive, self.app.current_project_name, self.app.project_data)
			returned_dictionnary = fill_archive.run()
			os.system("pause")
		
		self.app.message_function("Archiving process terminated", "notification")


		#load new project data?
		
		self.app.load_project_data_function()
		self.app.pop_screen()

		"""
		if type(returned_dictionnary)==dict:
			self.app.current_project_data = returned_dictionnary	
			self.app.project_data[self.app.current_project_name] = self.app.current_project_data
			self.app.message_function("Dictionnary updated")

			self.app.current_project_name = self.app.project_list[self.app.listview_projectlist.index][1]
			#get the current project data
			self.app.current_project_data = self.app.project_data[self.app.current_project_name]

		

			self.app.message_function(type(self.app.current_project_data))
			try:
				
				self.save_dictionnary_function()
			except Exception as e:
				self.app.message_function("Impossible to update the dictionnary\n%s"%traceback.format_exc(), "error")
			else:
				self.app.message_function("Archiving changes saved successfully", "success")

		else:
			pass
		"""


class ModalASPCHelpCenter(ModalScreen):
	CSS_PATH = ["styles/layout.tcss"]
	BINDINGS = [
		Binding("enter","binding_leavehelp", description="Binding leave help"),
	]

	def __init__(self, theme_dictionnary):
		super().__init__()
		self.theme = theme_dictionnary
		self.MARKDOWN_HELP = """
[bold][%s]AUSPICIOUS[/%s][/bold] is a program that helps you list items in your projects/folders that are unnecessary, 
that are present in large numbers, take up space and that you would like (at least temporarily) 
to archive in a compressed file to limit the space used.\n
These files may be important and useful, but you don't necessarily need to keep them on your main hard disk all the time.

[bold][italic][%s]Github link[/%s][/italic][/bold]
https://github.com/DelaporteRobin/ASPC

[bold][italic][%s]Documentation link[/%s][/italic][/bold]
This documentation is not available yet
"""%(self.theme.primary,self.theme.primary, self.theme.primary,self.theme.primary,self.theme.primary, self.theme.primary)

	def compose(self) -> ComposeResult:
		with Vertical(id = "vertical_help_container"):

			yield FigletWidget("AUSPICIOUS HELP", font=ASCII_FONT_HOMEPAGE, justify="center",colors=["$primary", "$secondary", "$background","$panel"], animate=True, gradient_quality=30, id="help_title")
			self.markdown_help = Static(self.MARKDOWN_HELP, id="markdown_help")
			yield self.markdown_help

			yield Button("Leave help", id="button_leavehelp", classes="button_main")


	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button_leavehelp":
			self.app.pop_screen()





class ASPC_MAIN(App, ASPC_LOG, ASPC_SNOOP, ASPC_UTILS, ASPC_GUI, ASPC_ARCHIVE):


	CSS_PATH = ["styles/layout.tcss"]
	BINDINGS = [
		Binding("ctrl+j", "binding_fill", description="Binding Fill Selection"),
		Binding("!", "binding_welcome", description="Binding Show Welcome Page"),
		Binding(
			key="question_mark",
			action="binding_help",
			description="Show help",
			key_display="?"
			)
	]


	def __init__(self):
		super().__init__()


		#load visual themes in the application
		#apply the theme specified in config file
		self.THEME_REGISTRY = THEME_REGISTRY
		self.THEME_DICTIONNARY = None
		for theme in self.THEME_REGISTRY:
			self.register_theme(theme)
			if theme.name == THEME:
				self.THEME_DICTIONNARY = theme

		self.theme = THEME
		

		self.global_root_path = Path("/")
		self.global_log = []
		self.global_log_backup = []

		self.selected_item = None

		#define the color theme
		self.color_theme = "downtown"

		self.build_path = None
		self.current_focused_folder = Path("/")
		self.current_project_name = None
		self.current_folder_selected = None

		self.current_folder_children_list = []
		self.current_folder_list = []
		self.current_file_list = []
		self.current_file_list_copy = []
		self.current_archive_content = []

		self.content_to_archive = []

		self.project_data = {}
		self.project_list = []

		self.stop_event_folder = threading.Event()
		self.stop_event_file = threading.Event()
		self.thread_update_folder_list = threading.Thread()
		self.thread_update_file_list = threading.Thread()

		self.markdown_base_content = """
Global project informations
"""


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

					#yield Button("CRASHTEST", id="test_log")
					yield Button("Remove project from list", id="button_remove_project")
				with VerticalScroll(id = "verticalscroll_bottomcontainer_left"):
					self.input_global_root_path = Input(placeholder="Starting folder", id="input_global_root_path")
					yield self.input_global_root_path

					self.directorytree_main = HighlightableDirectoryTree(self.global_root_path, id="directorytree_main")
					yield self.directorytree_main

					self.label_global_root_path = Label("", id="label_global_root_path")
					yield self.label_global_root_path

					yield Button("ADD TO LIST AND\nEXPLORE PROJECT", id="button_explore_project", classes="button_main")


			
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
						self.checkbox_show_archived = Checkbox("Show archived content", id="checkbox_show_archived")
						yield self.checkbox_file_similarity
						yield self.checkbox_file_size
						yield self.checkbox_file_children
						yield self.checkbox_file_gradient
						yield self.checkbox_show_archived
						

					self.progress_files = ProgressBar(id="progress_files")
					yield self.progress_files

					self.listview_files = MultiListView(id = "listview_files")
					yield self.listview_files
					self.listview_files.border_title = "Files list"





			with VerticalScroll(id = "verticalscroll_container_right"):
				with TabbedContent(id = "tabbedcontent_right"):
					with TabPane(title = "ARCHIVE CONTENT", id = "tabpane_archive"):
						with Collapsible(title = "ARCHIVE COMPRESSION SETTINGS", id="collapsible_compression_settings"):
							
							#yield Button("Get extension list in project", id="button_extensionlist_get")	
							self.listview_extensionlist = MultiListView(id="listview_extensionlist")
							yield self.listview_extensionlist
							self.listview_extensionlist.border_title = "Extension list in project"

							yield Button("TEST COMPRESSION METHODS", id="button_compression_test", classes="button_main")



						with Collapsible(title = "MODIFY ARCHIVE", id="collapsible_archive_modify"):
							with VerticalScroll(id="verticalscroll_archive_modify"):
								with Horizontal(id = "tab_horizontal_archivecontent"):
									with VerticalScroll(id = "tab_vertical_archivecontent_left"):

										self.listview_addarchive_selected = MultiListView(id="listview_addarchive_selected")
										yield self.listview_addarchive_selected
										self.listview_addarchive_selected.border_title = "Items to archive"

										with VerticalScroll(id = "tab_vertical_archiveoptions"):
											yield Button("Clear Items in list", id = "button_addarchive_clearlist", classes="button_main")

											yield Rule(line_style="heavy")

											yield Button("Add selected folder", id="button_addarchive_selectedfolder")
											yield Button("Add selected files", id ="button_addarchive_selectedfiles")
											
											yield Rule(line_style="heavy")


											self.checkbox_filter_fromselection = Checkbox("Apply only on folder selection",id="checkbox_filter_fromselection")
											yield self.checkbox_filter_fromselection
											yield Button("Filter window", id="button_addarchive_applyfilter")

											yield Rule(line_style="heavy")

			

											yield Button("Add to archive", id="button_add_to_archive", classes="button_main")


									with Vertical(id = "tab_vertical_archivecontent_right"):
										with Collapsible(id = "collapsible_archive_settings", title="ARCHIVE SETTINGS"):
											#self.checkbox_custom_archivepath = Checkbox("Custom archive path", id="checkbox_custom_archivepath")
											self.input_archive_path = Input(placeholder="Archive path", id="input_archive_path")
											#yield self.checkbox_custom_archivepath
											yield self.input_archive_path	

											with Horizontal(id="horizontal_archive_features"):
												yield Button("Move archive", id="button_archive_move", classes="button_main")

										with Collapsible(id = "collapsible_archive_features", title="ARCHIVE TOOLS"):
											yield Button("Check for Overheads", id="button_archive_check_overhead")
											yield Button("FIX OVERHEADS", id="button_archive_fix_overhead", classes="button_main")

											self.checkbox_archive_get_below = Checkbox("Select files below", id="checkbox_archive_get_below")
											self.checkbox_archive_get_same = Checkbox("Select files in the same folder", id="checkbox_archive_get_same")

											#yield self.checkbox_archive_get_below
											#yield self.checkbox_archive_get_same

										self.listview_archive_content = MultiListView(id="listview_archive_content")
										yield self.listview_archive_content
										self.listview_archive_content.border_title = "Archive content"


										yield Button("RESTORE FILES", id="button_restore_file", classes="button_main")

					with TabPane(title = "GLOBAL INFORMATIONS", id = "tabpane_folderinformation"):
						#yield Label("folder informations tab")
						#self.markdown = Markdown(self.markdown_base_content, id="markdown")

						"""
						self.markdown_project = Markdown(id = "markdown_project")
						yield self.markdown_project
						"""
						
						with Collapsible(title = "Markdown Data", id="collapsible_data_markdown"):
							with Collapsible(title = "Markdown update settings", id="collapsible_markdown_settings"):
								self.checkbox_update_project = Checkbox("Update when selecting project", id="checkbox_update_project")
								self.checkbox_update_folder = Checkbox("Update when selecting folder", id="checkbox_update_folder")
								self.checkbox_update_file = Checkbox("Update when selecting file", id = "checkbox_update_file")
								self.checkbox_update_archive = Checkbox("Show archive informations", id="checkbox_update_archive")
								yield self.checkbox_update_project
								yield self.checkbox_update_folder
								yield self.checkbox_update_file
								yield self.checkbox_update_archive

							self.markdown_viewer = MarkdownViewer(self.markdown_base_content, id="markdown_viewer")
							yield self.markdown_viewer

						with Collapsible(title = "Graph Data", id="collapsible_data_graph"):
							with VerticalScroll(id = "verticalscroll_collapsible_graphdata"):

								"""
								self.plotext_filesize = PlotextPlot(id="plotext_filesize")
								yield self.plotext_filesize
								with Horizontal(id="horizontal_plotext_filesize"):
									self.input_plotext_fileitems = Input(type="number", value="0",placeholder="Number of file to display", id="input_plotext_filesize")
									yield self.input_plotext_fileitems
									yield Button("Show largest files", id="button_plotext_filesize", classes="button_main")
								"""
								self.plotext_foldersize = PlotextPlot(id="plotext_foldersize")
								yield self.plotext_foldersize
								with Horizontal(id="horizontal_plotext_foldersize"):
									self.input_plotext_foldersize = Input(type="number", value="0", placeholder="Number of folders to display", id="input_plotext_foldersize")
									yield self.input_plotext_foldersize
									yield Button("Show largest folders", id="button_plotext_foldersize", classes="button_main")

								#self.sparkline_extension = Sparkline(id="sparkline_extension")
								#self.sparkline_extension.border_title = "Extension data"
								self.plotext_extension = PlotextPlot(id="plotext_extension")
								yield self.plotext_extension
								yield Button("Show extension Data", id="button_graph_extension", classes="button_main")

								self.plotext_archive_compression = PlotextPlot(id="plotext_archive_compression")
								yield self.plotext_archive_compression
								yield Button("Show Compression\nData", id="button_graph_compression", classes="button_main")

								self.plotext_project_extension_size = PlotextPlot(id="plotext_extension_size")
								yield self.plotext_project_extension_size
								yield Button("Show extension ratio in project", id="button_extension_size", classes="button_main")

						
						

					with TabPane(title = "LOG", id = "tabpane_log"):
						self.listview_log = ListView(id = "listview_log")
						yield self.listview_log

			yield Footer()
					
					





	def on_mount(self) -> None:
		
		

		#self.read_log_thread = threading.Thread(target=self.read_log_function, daemon=True,args=())
		#self.read_log_thread.start()


		#self.message_function(self.theme.primary)
		self.message_function("Log thread activated", "success")

		self.load_project_data_function()
		self.refresh_project_list_function()
		self.load_user_settings_function()
		#self.load_archive_content_function()


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
		self.install_screen(ASPC_HOMEPAGE(self.THEME_DICTIONNARY), name="ASPC_HOMEPAGE")
		#push the homepage screen
		#show_homepage
		self.push_screen("ASPC_HOMEPAGE")

		self.message_function("possible : %s"%self.query_one("#collapsible_data_markdown").allow_maximize)






	def action_binding_fill(self) -> None:
		if self.focused.id == "listview_files":
			#get the index of the current index selected
			#self.message_function(self.listview_files.index)
			#check if the index list isn't empty
			if len(self.listview_files.index_list) != 0:
				#self.message_function("%s ; %s"%(self.listview_files.index_list[-1], self.listview_files.index))
				index_range = sorted([self.listview_files.index_list[-1], self.listview_files.index])

				for i in range(index_range[0], index_range[1]):
					children_item = self.listview_files.children[i]
					children_item.highlight_item(children_item)
					self.listview_files.index_list.append(i)
					#self.message_function("%s ; %s"%(i,children_item))

		if self.focused.id == "listview_extensionlist":
			if len(self.listview_extensionlist.index_list) != 0:
				index_range = sorted([self.listview_extensionlist.index_list[-1], self.listview_extensionlist.index])

				for i in range(index_range[0], index_range[1]):
					children_item = self.listview_extensionlist.children[i]
					children_item.highlight_item(children_item)
					self.listview_extensionlist.index_list.append(i)

		if self.focused.id == "listview_archive_content":
			#get the index of the current index selected
			#self.message_function(self.listview_files.index)
			#check if the index list isn't empty
			if len(self.listview_archive_content.index_list) != 0:
				#self.message_function("%s ; %s"%(self.listview_files.index_list[-1], self.listview_files.index))
				index_range = sorted([self.listview_archive_content.index_list[-1], self.listview_archive_content.index])

				for i in range(index_range[0], index_range[1]):
					children_item = self.listview_archive_content.children[i]
					children_item.highlight_item(children_item)
					#self.message_function("%s ; %s"%(i,children_item))
					self.listview_archive_content.index_list.append(i)


		#self.message_function(self.listview_files.index_list)
		#self.message_function(self.listview_archive_content.index_list)


	def action_binding_help(self) -> None:
		self.message_function("Call help center", "notification")
		self.push_screen(ModalASPCHelpCenter(self.THEME_DICTIONNARY))

	def action_binding_welcome(self) -> None:
		self.message_function("Show welcome page", "notification")
		self.push_screen(ASPC_HOMEPAGE(self.THEME_DICTIONNARY))





	def on_key(self, event:events.Key) -> None:
		if (event.key == "enter") and (self.focused.id == "listview_files"):
			children_item = self.listview_files.children[self.listview_files.index]
			children_item.highlight_item(children_item)

		if (event.key == "enter") and (self.focused.id == "listview_folders"):
			children_item = self.listview_folders.children[self.listview_folders.index]
			children_item.highlight_item(children_item)

		if (event.key == "enter") and (self.focused.id == "listview_archive_content"):
			children_item = self.listview_archive_content.children[self.listview_archive_content.index]
			children_item.highlight_item(children_item)

		if (event.key == "enter") and (self.focused.id == "listview_extensionlist"):
			children_item = self.listview_extensionlist.children[self.listview_extensionlist.index]
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




	def check_for_archive_create_dismiss_function(self, quit_value: bool | None) -> None:
		#self.message_function("dismiss value : %s"%quit_value)
		if quit_value == False:
			try:
				self.push_screen(ModalASPCAddToArchive(self.THEME_DICTIONNARY))
			except Exception as e:
				self.message_function("Impossible to call screen\n%s"%traceback.format_exc(), "error")
			else:
				self.message_function("Screen called", "success")

		

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "test_log":
			self.message_function(self.current_folder_selected)

		if event.button.id == "button_compression_test":
			#launch the class to test extension with multiprocessing
			with self.suspend():
				ASPC_FILL_ARCHIVE_CLASS = ASPC_FILL_ARCHIVE(self.THEME_DICTIONNARY, self.user_settings, self.listview_extensionlist.index_list, self.current_project_name, self.project_data, None, False, False)
				returned_compression_dictionnary = ASPC_FILL_ARCHIVE_CLASS.test_compression_method_function()
				#print(returned_compression_dictionnary)
				#get the type of the returned dictionnary and add it in user settings file
				if "COMPRESSION" in self.user_settings:
					user_compression_dictionnary = self.user_settings["COMPRESSION"]
					#replace values in dictionnary
					for extension_name, compression_method in returned_compression_dictionnary.items():
						user_compression_dictionnary[extension_name] = compression_method
				else:
					self.user_settings["COMPRESSION"] = returned_compression_dictionnary
				#save user settings
				self.save_user_settings_function()
				os.system("pause")

		if event.button.id == "button_archive_move":
			self.move_archive_function()

		if event.button.id == "button_graph_extension":
			self.load_data_extension()

		if event.button.id == "button_plotext_foldersize":
			self.load_graph_foldersize_function()

		if event.button.id == "button_plotext_filesize":
			self.load_graph_filesize_function()

		if event.button.id == "button_graph_compression":
			self.load_data_compression()

		if event.button.id == "button_extension_size":
			self.load_data_project_extension_ratio()

		if event.button.id == "button_addarchive_applyfilter":
			
			#launch the screen
			self.push_screen(ModalASPCFilterScreen())



		if event.button.id == "button_archive_check_overhead":
			self.check_for_overhead_function()

		if event.button.id == "button_archive_fix_overhead":
			self.fix_overhead_function()



		if event.button.id == "button_remove_project":

			#get the project selected
			try:
				project = list(self.project_data.keys())[self.listview_projectlist.index]
			except:
				self.message_function("You have to select a project to remove", "error")
			else:
				self.message_function("Trying to remove this project from data : %s"%project)

				#if there is an archive for this project
				#ask if the user want to restore archive in project before 
				#self.remove_project_function()
				if "ARCHIVE_PATH" in self.current_project_data:
					self.push_screen(ModalASPCRemoveProject(), self.remove_project_function)
				else:
					self.remove_project_function(False)



		if event.button.id == "button_addarchive_clearlist":
			self.content_to_archive.clear()
			self.listview_addarchive_selected.clear()
			self.message_function("Content to archive cleared", "notification")

		



		if event.button.id == "button_add_to_archive":
			#CHECK FOR ARCHIVE PATH
			archive_exists = self.check_for_archive_function()

			if archive_exists == False:
				self.push_screen(ModalASPCCreateArchive(), self.check_for_archive_create_dismiss_function)

			else:
				#self.push_screen(ModalASPCAddToArchive())
				self.message_function("Archiving process started", "notification")
				#MULTIPROCESSING MODE
				#create instance of the archiving class
				with self.app.suspend():
					#fill_archive = ASPC_FILL_ARCHIVE(self.app.content_to_archive, self.app.current_project_name, self.app.current_project_data)
					fill_archive = ASPC_FILL_ARCHIVE(self.THEME_DICTIONNARY, self.user_settings, self.content_to_archive, self.current_project_name, self.project_data)
					returned_dictionnary = fill_archive.run()
					os.system("pause")
				
				self.message_function("Archiving process terminated", "notification")


				#load new project data?
				
				self.load_project_data_function()
				#self.pop_screen()




		if event.button.id == "button_restore_file":
			self.message_function("Starting restore file process...", "notification")
			with self.suspend():
				self.restore_file_from_archive_function()
				#print("Waiting...")
				#sleep(4)
				#UPDATE THE DATA FILE 
				#ASPC_SNOOP(self.current_project_name)

				os.system("pause")

			#reset all listview
			self.listview_folders.clear()
			self.listview_files.clear()
			self.listview_archive_content.clear()
			#reload project data
			self.load_project_data_function()
			self.message_function("Restore file process done", "notification")
	
			

			


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

					#before adding the file in the filelist check if there is a container in the list
					container_in_list = False
					pathlib_filepath = Path(filepath).resolve()
					for element in self.content_to_archive:
						#get the parent and create the pathlib values
						if Path(element).resolve() in pathlib_filepath.parents:
							container_in_list=True 
							break
					if container_in_list == True:
						self.message_function("File skipped : %s\nContainer folder is already in the list"%filepath, "error")
						return
					#check if the filepath is already in the list
					if filepath not in self.content_to_archive:
						self.content_to_archive.append(filepath)
						selected_files_label.append(ListItem(label))
			except IndexError:
				self.message_function("Filelist content has changed", "warning")
			

			self.listview_addarchive_selected.extend(selected_files_label)

		if event.button.id == "button_addarchive_selectedfolder":

			selected_folder_label = []
			selected_index = self.listview_folders.index_list


			"""
			ADD FOLDER CONDITIONS
			-check if children (files / folders) are already in list
				- yes : remove all children and replace by the parent folder
				- no : just add the folder
			-check if parent folder are already in list
				- yes: don't add and show error
				- no: add the folder to the list
			"""

			for index in selected_index:
				folder = self.current_folder_list[index]
				label = Label(os.path.basename(folder))

				if os.path.isdir(folder)==False:
					label.styles.color = self.theme_variables["text-secondary"]


				#check if children are already in list
				#create a list of children to remove
				children_to_remove_list = []
				for i in range(len(self.content_to_archive)):
					#check if the list item is a parent of the selected folder
					#if it is a folder of course
					if Path(self.content_to_archive[i]).resolve() in Path(folder).resolve().parents:
						self.message_function("A parent of this folder is already in the list", "error")
						return

					#check if the list item is a children of the selected folder
					if Path(folder).resolve() in Path(self.content_to_archive[i]).resolve().parents:
						self.message_function("Children of the selected folder detected in list\n%s"%self.content_to_archive[i], "warning")
						children_to_remove_list.append(i)

				#remove children from the content to archive list
				#remove children from the listview
				for index in children_to_remove_list:
					self.content_to_archive.pop(index)
					self.listview_addarchive_selected.remove_items([index])


				#finally add the folder and the label to the list
				self.content_to_archive.append(folder)
				selected_folder_label.append(ListItem(label))

			self.listview_addarchive_selected.extend(selected_folder_label)
			



		if event.button.id == "button_explore_project":
			#get the path of the project
			self.message_function("Launching multiprocessing exploration...", "notification")
			with self.suspend():
				ASPC_SNOOP(self.selected_item, self.THEME_DICTIONNARY)
				os.system("pause")

			self.message_function("Multiprocessing exploration done", "success")

		
			#reset all lists
			self.message_function("Trying to refresh project list")
			self.listview_projectlist.clear()
			value = self.load_project_data_function()
			self.refresh_project_list_function()
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

		#self.message_function("hello world : %s"%self.listview_projectlist.index)
		if self.thread_update_folder_list.is_alive():
			self.stop_event_folder.set()
			self.stop_event_folder.wait()
			#self.thread_update_list.join()
			return
		


		self.listview_folders.clear()
		self.listview_files.clear()
		 
		

		#clean the folder list
		self.current_folder_list.clear()
		self.current_file_list.clear()


		#get the project name
		try:
			self.current_project_name = self.project_list[self.listview_projectlist.index][1]
			#get the current project data
			self.current_project_data = self.project_data[self.current_project_name]
			#self.message_function(len(list(self.project_data[self.current_project_name]["DATA_FOLDER"].keys())))   
		except TypeError:
			return
		except IndexError:
			self.message_function("No project selected","error")
		
		
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
		#self.message_function("%s\n\n"%("_"*120), "message", False)

		if event.control.id in ["listview_project", "listview_folders", "listview_files"]:
			self.update_markdown_function()
			#self.message_function("hello world")

		if event.control.id == "listview_projectlist":
			#update the dictory tree starting folder
			self.input_global_root_path.value = self.project_list[self.listview_projectlist.index][1]
			self.directorytree_main.path = self.project_list[self.listview_projectlist.index][1]
			#self.update_dir_tree_starting_folder(self.project_list[self.listview_projectlist.index][1])

			#call the threading checking function
			self.check_for_folder_process_function()
			self.check_for_archive_content_function()
			self.check_for_extension_function()
			



		if event.control.id == "listview_addarchive_selected":
			#get the list of children
			self.message_function("Item removed from list : %s"%self.listview_addarchive_selected.index)
			index = self.listview_addarchive_selected.index
			self.message_function(index)

			self.message_function(len(self.listview_addarchive_selected.children))

			if type(index)==int:
				self.listview_addarchive_selected.pop(index)
			"""
			self.listview_addarchive_selected.remove_items([index])
			#remove the index in the list as well
			self.content_to_archive.pop(self.listview_addarchive_selected.index)
			"""
		


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
			#self.highlight_folder_children_function()



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