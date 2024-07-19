import os
import sys
import time 
import multiprocessing

from rich.console import Console


from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual import events
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

from datetime import datetime
from pyfiglet import Figlet

import threading
import json
import colorama

from Data.ASPC_Common import ASPC_CommonApplication
from Data.ASPC_SearchingSystem import ASPC_SearchingApplication



colorama.init()




class ASPC_MainApplication(App, ASPC_CommonApplication):
	#CSS_PATH = ["Data/Style/styleGlobal.tcss"]


	def __init__(self):
		super().__init__()
		self.font_title = Figlet(font="delta_corps_priest_1")
		#self.font_title = Figlet(font="bloody")
		self.font_subtitle = Figlet(font="bubble")




	def show_message_function(self, message):
			self.notify(message, timeout=3)



	def compose(self) -> ComposeResult:

		"""
		INFORMATIONS TO DISPLAY ON THE TUI

		date delta classement <=> date of creation separated with modification date
		file size for extension (heaviest) -> compare with the container folder
		number of files by similiarity (compared to the number of files in the folder)
		highest difference of size in project (classement)
		speed test classement (for heavy)
		"""


		yield Header(show_clock=True)

		with Horizontal(classes="main_application_container"):
			yield Button("launch process", classes="button_launch", id="button_launch")
			yield Button("launch process", classes="button_launch")
			yield Button("launch process", classes="button_launch")
			yield Button("launch process", classes="button_launch")






	async def on_key(self, event: events.Key) -> None:
		if event.key == "p":
			self.exit()


	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button_launch":
			self.launch_process_function()




	def launch_process_function(self):
		self.root_folder = "D:/TRASH"

		#self.queue_size_limit = 50000
		self.main_data_set_dictionnary = {}
		self.main_log_list = []

		

		


		"""
		LIST OF INFORMATIONS TO RETURN

		FOR EACH FILES
			average file size in folder
			average file size for extension
			average file size in pipeline

			apply the performance test and get results

			name recognition algorythm
		FOR EACH FOLDERS
			get traffic for this folder
			average size in pipeline
			define if main folder?
			number of subfolders and files
			time to read files
			time to read folder

			size contained (global) compared to global size
			size contained (only files)
			--> size of the files contained compared to the number of files



		Set an observer file over time to follow folder hierarchy modification
			update the amount of time a folder or file is being used / modified.

		"""




		#IMPORT THE SIDE CLASS TO LAUNCH RESEARCH
		
		self.sa = ASPC_SearchingApplication()
		self.main_folder_queue = self.sa.file_queue_init_function(self.root_folder)
		#x = threading.Thread(target=self.sa.file_queue_init_function, args=(self.root_folder,), daemon=True)
		#x.start()
		#x.join()
		self.show_message_function("done")
		#self.display_message_function(type(self.main_folder_queue))
		#self.display_message_function(self.main_folder_queue)

		#display the content of the folder list
		#for folder in self.main_folder_list:
		#	print(folder)


		#create the test class
		#self.mpa = ASPC_ProcessApplication()
		#self.mpa.get_data_init(self.root_folder, self.main_folder_list)
		
		self.console = Console()
		with self.suspend():
			self.sa.get_data_init(self.console,self.root_folder, self.main_folder_queue)
			sys.exit()




if __name__ == "__main__":
	app = ASPC_MainApplication()
	app.run()