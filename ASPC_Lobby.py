import os
import sys
import time 
import multiprocessing

from rich.console import Console


from functools import partial


from textual.app import App, ComposeResult
from textual.widgets import Markdown, RadioSet, RadioButton, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.validation import Function, Number
from textual.screen import Screen 
from textual import events
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

from datetime import datetime
from pyfiglet import Figlet
from time import sleep

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


		#check for scan settings file
		self.settings = {}
		self.load_settings_function()
		for key, value in self.settings.items():
			print(key, value)

		self.color_dictionnary = {
			"background": "#151416",
			"selected": "gray",
			"secondary": "white",
			"error": "#f06042",

			"heaviest":"#F99461",
			"lightest":"#B1D94D"
		}


		self.font_lobby = Figlet(font="ansi_shadow")
		self.font_title = Figlet(font="delta_corps_priest_1")
		#self.font_title = Figlet(font="bloody")
		self.font_subtitle = Figlet(font="bubble")


		self.manual_scan_data = None

		self.file_dictionnary = {}
		self.folder_dictionnary = {}
		self.current_lobby_filelist = []

		self.folder_list = []
		self.file_list = []

		self.live_folderlist_proxy = None



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



				yield Label(self.font_lobby.renderText("ASPC"), id="label_title")
				
				#collapsible containing all the scan settings
				#saved into a JSON Files
				#coming in the next updates as soon as the whole
				#system of statistics in working

				self.root_folder_input = Input(placeholder="Root folder path", type="text", id="input_folder_path")
				yield self.root_folder_input

				with Collapsible(title="MANUAL SCAN SETTINGS", classes="collapsible_manual_scan"):
					#yield Static("All the settings that can be changed to customize the manual scan\nComing soon...")
					"""
					LIST OF THE SETTINGS
						path of the root folder
						save json file
						root folder
						speedtest ?
						speedtest threshold for heaviest file?
						number of multiprocessing (cpu count?)
					"""
					yield Static("Max number of process during scan")
					self.input_process_number = Input(id="input_process_number", type="integer", validate_on=["submitted"], placeholder="Process number", validators = [Number(minimum=1, maximum=multiprocessing.cpu_count())])
					yield self.input_process_number

					with RadioSet(id = "radio_scan_settings"):
						self.radio_core = RadioButton("Number of Core")
						self.radio_custom = RadioButton("Custom")

						yield self.radio_core
						yield self.radio_custom

					self.checkbox_savejson = Checkbox("Save json file after scan", id="checkbox_savejson")
					self.checkbox_speedtest = Checkbox("Use speedtest during scan", id="checkbox_speedtest")
					self.checkbox_threshold = Checkbox("Use speedtest threshold", id="checkbox_threshold")

					yield self.checkbox_savejson
					yield self.checkbox_speedtest
					yield self.checkbox_threshold

					


				yield Button("Launch manual Scan", id="button_launch")
				yield Button("Trigger live mode", id="button_live")
				#yield Button("TEST BUTTON", id="test_button")


			with Vertical(classes="main_rightcolumn"):
				with TabbedContent():
					#with TabPane("Classement"):
					with Horizontal(classes="classement_horizontal"):

						
						with Vertical(classes="folder_column"):
							with Collapsible(title="Folder settings", id="folder_collapsible"):
								self.folder_searchbar = Input(placeholder="Search for ...", type="text", id="input_folder_searchbar")
								yield self.folder_searchbar
								with RadioSet(id="radio_folder_options"):
									yield RadioButton("Sort by size")
									yield RadioButton("Sort by size contained")
									yield RadioButton("Number of subfolders contained")
									yield RadioButton("Number of files contained")
									yield RadioButton("Ratio of the project contained")

							self.optionlist_folder = OptionList(id="optionlist_folder", wrap=False)
							self.optionlist_folder.border_title = "FOLDER LIST"
							yield self.optionlist_folder

						with Vertical(classes="files_column"):
							"""
							self.optionlist_files = OptionList(id="optionlist_files",wrap=False)
							self.optionlist_files.border_title = "FILE LIST"
							yield self.optionlist_files
							"""
							with Collapsible(title="File settings", id = "file_collapsible"):
								self.extension_list = OptionList(id="optionlist_extension")
								yield self.extension_list
								self.extension_list.border_title = "Extension list"
							self.listview_files = ListView(id="listview_files")
							self.listview_files.border_title = "FILE LIST"
							yield self.listview_files


						with Vertical(classes="files_stat_column"):
							self.markdown_folder_info = Markdown(id="markdown_folder_info")
							#self.markdown_folder_info.border_title = "FOLDER STATS"
							yield self.markdown_folder_info

							self.markdown_file_info = Markdown(id="markdown_file_info")
							#self.markdown_file_info.border_title = "FILE STATS"
							yield self.markdown_file_info
					#with TabPane("Live project statistics"):
						"""
						additionnal informations
							start of the live mode


						display a list (updated in real time)
						modified folder by number of time

						display last date of modification (list of modification)
						"""
					with Horizontal(classes="live_row"):
						with Vertical(classes="live_column_folder"):

							
							#yield Button("trigger", id = "trigger_live")
							self.live_folderlist = ListView(id = "list_folderlist")
							self.live_folderlist.border_title = "Folder list"
							yield self.live_folderlist
							#self.mount(self.live_folderlist)
							"""
							self.live_folderlist = ListView(id="list_folderlist")
							self.live_folderlist.border_title = "Folder activity"
							yield self.live_folderlist
							"""

						with Vertical(classes="live_info_column"):
							self.markdown_live_info = Markdown(id="markdown_live_info")
							self.markdown_live_info.border_title = "Folder data"
							yield self.markdown_live_info


	async def on_mount(self) -> None:
		self.apply_settings_function()
		#self.check_for_live_mode_function()
		self.check_for_live_mode_function()







	def check_for_live_mode_function(self):
		#check if the live mode is enabled
		if self.check_live_is_enabled_function()==True:
			#get the log of the folder
			#get the settings of the current live mode
			#get the log file linked to the current live mode
			if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"Data/Live_settings.json"))==True:
				#load settings of the current live 
				try:
					with open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"Data/Live_settings.json"), "r") as read_file:
						live_settings = json.load(read_file)
				except:
					self.show_error_function("Impossible to load live mode settings")
				else:
					self.show_message_function("Live mode settings recovered")
					
					#get data from live mode settings
					live_project_path = live_settings["projectPath"]
					live_log_path = live_settings["logPath"]

					#check if the log file exists
					#launch the thread to read it real time
					if os.path.isfile(live_log_path)==True:
						self.read_live_worker(live_log_path, live_project_path)
						#read_live_log = threading.Thread(target=self.read_live_worker, args=(live_log_path, live_project_path,), daemon=True)
						#read_live_log.start()
						self.read_live_worker(live_log_path, live_project_path)
						self.show_message_function("Read live mode log activated")
					else:
						self.show_error_function("Impossible to get the live mode log")



	def read_live_worker(self,log_path=None,project_path=None):
		


		#try to read the content of the live log
		try:
			with open(log_path, "r") as read_log:
				content = json.load(read_log)
		except Exception as e:
			self.show_error_function("Impossible to read log!")
			return
		else:
			if content != self.live_folderlist_proxy:
				#clear the list view
				#add the new options
				list_keys = list(content.keys())
				list_values = list(content.values())

				#get the min values
				min_value = min(list_values)
				#get the max values
				max_value = max(list_values)

				min_values_index = list_values.index(min_value)
				max_values_index = list_values.index(max_value)
				#


		

				self.live_folderlist.clear()

				for key, value in content.items():
					label = Label("%s | %s"%(str(value), str(key)))
					list_item = ListItem(label)
					self.live_folderlist.append(list_item)
					
					#IT IS A DIRECTORY
					#self.show_message_function(os.path.isdir(key))
					if (os.path.splitext(key)[1] == "") and os.path.isdir(key)==False:
						label.styles.color = self.color_dictionnary["error"]

					else:
						if os.path.isfile(key)==True:
							label.styles.color = self.color_dictionnary["error"]


				#color the heaviest and lowest values



				#update the proxy value
				self.live_folderlist_proxy = content
		
		
		

		self.set_timer(2, partial(self.read_live_worker, log_path, project_path))
	








	def apply_settings_function(self):
		self.checkbox_savejson.value = self.settings["Manual"]["saveJson"]
		self.checkbox_speedtest.value = self.settings["Manual"]["executeSpeedTest"]
		self.checkbox_threshold.value = self.settings["Manual"]["speedTestThreshold"]
		self.input_process_number.value = str(self.settings["Manual"]["numberOfProcess"])
		self.root_folder_input.value = str(self.settings["Manual"]["rootFolder"])

		

		if self.settings["Manual"]["numberOfProcessMode"] == "custom":
			self.input_process_number.value = self.settings["Manual"]["numberOfProcess"]
			self.input_process_number.disabled = False
			self.radio_custom.value = True
			self.radio_core.value = False
		else:
			self.input_process_number.disabled = True
			self.radio_custom.value = False
			self.radio_core.value = True
			self.input_process_number.value =str( multiprocessing.cpu_count())




	async def on_key(self, event: events.Key) -> None:
		if event.key == "p":
			self.exit()








	def on_input_submitted(self, event:Input.Submitted) -> None:
		manual = self.settings["Manual"]
		#self.show_message_function("hello world")
		if event.input.id == "input_process_number":
			#get the value and update settings
			
			manual["numberOfProcess"] = self.query_one("#input_process_number").value
			self.save_settings_function()
		if event.input.id == "input_folder_path":
			manual["rootFolder"] = self.query_one("#input_folder_path").value
			self.save_settings_function()
		

		if event.input.id == "input_folder_searchbar":
			searchbar_content = str(self.query_one("#input_folder_searchbar").value).lower()

			self.optionlist_folder.clear_options()

			if searchbar_content != "":
				#update the folder list
				result_folder_list = []
				for folder in self.folder_list:
					if searchbar_content in folder.lower():
						result_folder_list.append(folder)
				
				self.optionlist_folder.add_options(result_folder_list)
			else:
				self.optionlist_folder.add_options(self.folder_list)







	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "trigger_live":
			self.read_live_worker()
		if event.button.id == "button_launch":
			self.launch_process_function()

		if event.button.id == "button_live":
			project = self.query_one("#input_folder_path").value
			if os.path.isdir(project) == False:
				self.show_error_function("Impossible to launch live mode\nFolder doesn't exists!")
			else:
				self.create_live_mode_config_function(project)





	def on_checkbox_changed(self, event:Checkbox.Changed) -> None:
		if event.checkbox.id in ["checkbox_savejson", "checkbox_speedtest", "checkbox_threshold"]:
			manual = self.settings["Manual"]
			manual["saveJson"] = self.query_one("#checkbox_savejson").value 
			manual["speedTestThreshold"] = self.query_one("#checkbox_threshold").value
			manual["executeSpeedTest"] = self.query_one("#checkbox_speedtest").value
			self.settings["Manual"] = manual 

			self.save_settings_function()
			#self.show_message_function("Settings saved")




	def on_radio_set_changed(self, event:RadioSet.Changed) -> None:
		if event.radio_set.id == "radio_scan_settings":
			#get the value
			radio_button = self.query_one("#radio_scan_settings").pressed_index
			manual = self.settings["Manual"]
			if radio_button == 0:
				manual["numberOfProcessMode"] = "core"
				self.input_process_number.disabled = True
				self.input_process_number.value = str(multiprocessing.cpu_count())
			else:
				manual["numberOfProcessMode"] = "custom"
				self.input_process_number.disabled = False
			self.settings["Manual"] = manual
			self.save_settings_function()
			#self.show_message_function("Settings saved")
			


	



	def on_list_view_selected(self,event:ListView.Selected) -> None:
		#self.show_message_function("hello world")
		#get the index of the item selected
		if event.list_view.id == "listview_files":
			selection = self.query_one("#listview_files").index
			self.show_message_function(self.current_lobby_filelist[selection])

			#get all informations about the given file
			final_markdown = self.create_markdown_for_file_function(self.current_lobby_filelist[selection])
			self.markdown_file_info.update(final_markdown)



	


	def on_option_list_option_selected(self, event: OptionList.OptionHighlighted) -> None:
		if event.option_list.id == "optionlist_folder":

			#get the list of files for that folder in the dictionnary
			#get the selected folder
			folder_selection = self.query_one("#optionlist_folder").highlighted
			#get the name of the folder
			folder_selected = self.folder_list[folder_selection]
			#get the files in that folder
			try:
				file_list = self.folder_dictionnary[folder_selected]["fileList"]
			except:
				#remove all colors
				for i in range(len(self.listview_files.children)):
					#self.listview_files.children[i].styles.background = self.color_dictionnary["background"]
					self.listview_files.children[i].styles.background = self.design["dark"].background
				self.show_error_function("No file contained in this folder")
			else:
				#get the markdown for the current folder to display stats
				final_markdown = self.create_markdown_for_folder_function(folder_selected)
				self.markdown_folder_info.update(final_markdown)

				#add the file list to the current file list
				self.listview_files.clear()
				self.current_lobby_filelist = []
				for file in file_list:
					self.current_lobby_filelist.append(file)
					list_item = ListItem(Label(os.path.basename(file)))
					self.listview_files.append(list_item)

					if file == self.folder_dictionnary[folder_selected]["minFileSize"][0]:
						#list_item.styles.background = self.color_dictionnary["lightest"]
						list_item.styles.background = self.color_dictionnary["lightest"]
					if file == self.folder_dictionnary[folder_selected]["maxFileSize"][0]:
						list_item.styles.background = self.color_dictionnary["heaviest"]
						#list_item.styles.background = self.color_dictionnary["heaviest"]

		if event.option_list.id == "optionlist_extension":
			#get the file linked to that extension
			extension_selection = self.query_one("#optionlist_extension").highlighted 
			extension_selected = list(self.extension_dictionnary.keys())[extension_selection]
			extension_data = self.extension_dictionnary[extension_selected]

			file_list = extension_data["fileList"]

			#remove the content of the file list
			#replace it by the filelist
			self.listview_files.clear()
			for file in file_list:
				label = Label(file)
				self.listview_files.append(ListItem(label))












	def create_markdown_for_folder_function(self, filepath):
		final_markdown="""
## General informations on folder
Folder : %s\n
"""%filepath
		#get general informations about the folder
		try:
			folder_size = self.get_size_mo_function(self.folder_dictionnary[filepath]["folderSize"])
			folder_size_contained = self.get_size_mo_function(self.folder_dictionnary[filepath]["fileContainedSize"])
			file_number = self.folder_dictionnary[filepath]["filesNumber"]
			subfolder_number = (self.folder_dictionnary[filepath]["subfolderNumber"])
			
		except:
			final_markdown+= """
> [!CAUTION] 
> Impossible to get global folder informations\n
"""
		else:
			final_markdown+= """
Folder size: %s Mo\n
Folder size (files contained) : %s Mo\n
Number of files in folder : %s\n
Number of subfolder : %s\n
"""%(folder_size,folder_size_contained,file_number,subfolder_number)


		final_markdown+="""
## Speed test informations
"""
		#get informations about file size
		try:
			speedtest_heavy = self.folder_dictionnary[filepath]["speedTest"]["heavy"]["speedTestDelta"]
			speedtest_light = self.folder_dictionnary[filepath]["speedTest"]["light"]["speedTestDelta"]

			lightest_file = self.folder_dictionnary[filepath]["minFileSize"][0]
			lightest_file_size = self.folder_dictionnary[filepath]["minFileSize"][1]

			heaviest_file = self.folder_dictionnary[filepath]["maxFileSize"][0]
			heaviest_file_size = self.folder_dictionnary[filepath]["maxFileSize"][1]
		except:
			final_markdown+="""
> [!CAUTION]
> Impossible to get data about speedtest for this folder
"""
		else:
			final_markdown += """
Speed test for lightest file : %s\n
Lightest file : %s\n
Lightest file size : %s\n
\n
Speed test for heaviest file : %s\n
Heaviest file : %s\n
Heaviest file size : %s\n

"""%(speedtest_light,lightest_file, lightest_file_size, speedtest_heavy, heaviest_file, heaviest_file_size)
		

		return final_markdown







	def create_markdown_for_file_function(self, filepath):
		final_markdown = """
"""
		#check if it possible to get all informations about the given
		#file in the dictionnary created by the manual scan
		file_date_data = self.manual_scan_data["GlobalDateData"][filepath]
		file_size = self.file_dictionnary[filepath]
		file_size_position = list(self.file_dictionnary.keys()).index(filepath)

		final_markdown+="""
## Extension data\n
"""
		try:
			#GET EXTENSION INFORMATIONS ABOUT THE FILE
			extension_dictionnary = self.extension_dictionnary[os.path.splitext(filepath)[1]]
			extension_average_size = extension_dictionnary["fileSizeAverage"]
			extension_file_position = list(extension_dictionnary["fileList"].keys()).index(filepath)
			#self.show_message_function("%s / %s"%(file_size, extension_average_size))
			#self.show_message_function("%s / %s"%())


		except:
			self.show_error_function("Impossible to gather data about file extension")
			final_markdown+= """
> [!CAUTION]
> Impossible to get data from file extension!\n
"""
		else:
			extension_markdown = """
Number of files with this extension : %s\n
Average size for that extension : %s Mo\n
Size of the current file : %s Mo\n

> [!IMPORTANT]
> on %s file(s) this file is the %sth heaviest\n
"""%(extension_dictionnary["fileCount"],self.get_size_mo_function(extension_average_size),self.get_size_mo_function(file_size),extension_dictionnary["fileCount"],extension_file_position)
		
		final_markdown+= extension_markdown

		
		final_markdown+="""
\n## Date data
"""
		try:
			#GET DATE INFORMATIONS ABOUT THE FILE
			creation_date = datetime.fromtimestamp(file_date_data["creationDate"])
			last_date = datetime.fromtimestamp(file_date_data["modificationDate"])
			current_date = datetime.fromtimestamp(time.time())
			date_difference = (current_date - last_date).days
			creation_date_format = "%s/%s/%s"%(creation_date.year, creation_date.month, creation_date.day)
			modification_date_format = "%s/%s/%s"%(last_date.year, last_date.month, last_date.day)
		except:
			final_markdown+="""
> [!CAUTION]
> Impossible to get date data\n
"""
		else:
			final_markdown+="""
Date of creation : %s\n
Last time modified : %s\n
Modified for the last time %s day(s) ago\n
"""%(creation_date_format, modification_date_format, date_difference)
		#creation_date_format = "%s/%s/%s"%(creation_date.tm_year, creation_date.tm_mon, creation_date.tm_mday)
		#self.show_message_function(creation_date_format)

		#self.show_message_function("%s : %s"%(filepath, self.file_dictionnary[filepath]))


		return final_markdown
		


			




	def launch_process_function(self):
		self.root_folder = self.root_folder_input.value
		if os.path.isdir(self.root_folder) == False:
			self.show_error_function("Impossible to launch scan\nFolder doesn't exists!")
			return

		#self.queue_size_limit = 50000
		self.main_data_set_dictionnary = {}
		self.main_log_list = []


		#IMPORT THE MULTIPROCESSING CLASS 
		self.sa = ASPC_SearchingApplication()

		
		
		self.manual_scan_value = None
		with self.suspend():
			self.display_notification_function("Starting folder : %s"%self.root_folder)
			try:
				self.main_folder_queue = self.sa.file_queue_init_function(self.root_folder)
				#x = threading.Thread(target=self.sa.file_queue_init_function, args=(self.root_folder,), daemon=True)
				#x.start()
				#x.join()
				self.show_message_function("done")
				#print(self.main_folder_queue)

				self.manual_scan_data = self.sa.get_data_init(self.root_folder, self.main_folder_queue, self.settings)
				#sys.exit()
				#if exit after the scan is toggled
				#because why not after all
				#sys.exit()
			except Exception as e:
				self.display_error_function("An exception as occured during the manual scan:\n%s"%e)
				self.manual_scan_value=False
			else:
				self.manual_scan_value=True

			"""
			for key, value in self.manual_scan_data.items():
				print(key, value)
			"""
		

			if type(self.manual_scan_data) != None:
				self.update_list_informations_function()

















	def update_list_informations_function(self):
		#get the value of the folder dictionnary
		self.folder_dictionnary = self.manual_scan_data["GlobalFolderData"]
		self.folder_list = list(self.folder_dictionnary.keys())

		self.file_dictionnary = self.manual_scan_data["GlobalFileData"]
		self.filename_list = list(self.file_dictionnary.keys())
		self.filesize_list = list(self.file_dictionnary.values())

		self.extension_dictionnary = self.manual_scan_data["GlobalExtensionData"]




		#CLEAR OPTIONS
		self.optionlist_folder.clear_options()
		self.listview_files.clear()

		#ADD OPTIONS

		self.optionlist_folder.add_options(self.folder_list)



		#ADD EXTENSION
		extension_list = list(self.extension_dictionnary.keys())
		self.extension_list.clear_options()
		self.extension_list.add_options(extension_list)
		
		"""
		for i in range(len(self.filename_list)):
			new_item = ListItem(Label(self.filename_list[i]))
			self.listview_files.append(new_item)
		"""

if __name__ == "__main__":
	app = ASPC_MainApplication()
	app.run()