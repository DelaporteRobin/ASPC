import os
import sys
import time 
import multiprocessing

from rich.console import Console


from textual.app import App, ComposeResult
from textual.widgets import RadioSet, RadioButton, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
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
	CSS_PATH = ["Data/Style/style_Global.tcss", "Data/Style/Style_Main.tcss"]


	def __init__(self):
		super().__init__()
		self.font_title = Figlet(font="delta_corps_priest_1")
		#self.font_title = Figlet(font="bloody")
		self.font_subtitle = Figlet(font="bubble")


		self.manual_scan_data = None




	def show_message_function(self, message):
		self.notify(str(message), timeout=3)

	def show_error_function(self, message):
		self.notify(str(message), timeout=3, severity="error")



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

		with Horizontal(classes="main_horizontal_container"):

			with Vertical(classes="main_leftcolumn"):
				
				#collapsible containing all the scan settings
				#saved into a JSON Files
				#coming in the next updates as soon as the whole
				#system of statistics in working
				with Collapsible(title="MANUAL SCAN SETTINGS", classes="collapsible_manual_scan"):
					yield Static("All the settings that can be changed to customize the manual scan\nComing soon...")

				yield Button("Launch Scan", id="button_launch")


			with Vertical(classes="main_rightcolumn"):
				with TabbedContent():
					with TabPane("Classement"):
						with Horizontal(classes="classement_horizontal"):

							
							with VerticalScroll(classes="folder_column"):
								with RadioSet(id="radio_folder_options"):
									yield RadioButton("Sort by size")
									yield RadioButton("Sort by size contained")
									yield RadioButton("Number of subfolders contained")
									yield RadioButton("Number of files contained")
									yield RadioButton("Ratio of the project contained")

								self.optionlist_folder = OptionList(id="optionlist_folder")
								self.optionlist_folder.border_title = "FOLDER LIST"
								yield self.optionlist_folder

							with Vertical(classes="files_column"):
								yield Button("hello world")
					with TabPane("Global Project View"):
						yield Button("hello world")









	async def on_key(self, event: events.Key) -> None:
		if event.key == "p":
			self.exit()


	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button_launch":
			self.launch_process_function()




	def launch_process_function(self):
		self.root_folder = "D:/WORK/LIGHTING/prospect/"

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
		
		#self.display_message_function(type(self.main_folder_queue))
		#self.display_message_function(self.main_folder_queue)

		#display the content of the folder list
		#for folder in self.main_folder_list:
		#	print(folder)


		#create the test class
		#self.mpa = ASPC_ProcessApplication()
		#self.mpa.get_data_init(self.root_folder, self.main_folder_list)
		
		
		self.manual_scan_value = None
		with self.suspend():
			try:
				self.main_folder_queue = self.sa.file_queue_init_function(self.root_folder)
				#x = threading.Thread(target=self.sa.file_queue_init_function, args=(self.root_folder,), daemon=True)
				#x.start()
				#x.join()
				self.show_message_function("done")
				print(self.main_folder_queue)

				self.manual_scan_data = self.sa.get_data_init(self.root_folder, self.main_folder_queue)

				#if exit after the scan is toggled
				#because why not after all
				#sys.exit()
			except Exception as e:
				self.display_error_function("An exception as occured during the manual scan:\n%s"%e)
				self.manual_scan_value=False
			else:
				self.manual_scan_value=True

		"""
		self.show_message_function(self.manual_scan_value)
		self.show_message_function(type(self.manual_scan_data))
		"""

		for key, value in self.manual_scan_data.items():
			self.show_message_function("%s : %s"%(key, type(value)))

		if type(self.manual_scan_data) != None:
			self.update_list_informations_function()








	def update_list_informations_function(self):
		#get the value of the folder dictionnary
		folder_dictionnary = self.manual_scan_data["GlobalFolderData"]
		folder_list = list(folder_dictionnary.keys())


		self.optionlist_folder.clear_options()

		self.optionlist_folder.add_options(folder_list)
		"""
		for i in range(25):
			self.optionlist_folder.add_option(Option(str(folder_list[i])))
		"""


if __name__ == "__main__":
	app = ASPC_MainApplication()
	app.run()