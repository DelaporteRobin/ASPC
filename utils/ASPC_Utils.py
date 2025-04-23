# -*- coding: utf-8 -*-


import json
import os
import traceback

from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

from time import sleep	
from datetime import datetime








class ASPC_UTILS:
	def letter_verification_function(self, content):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"
		list_letter = list(letter)
		list_capital = list(letter.upper())
		list_figure = list(figure)
		list_content = list(content)

		for i in range(len(list_content)):
			if (list_content[i] in list_letter) or (list_content[i] in list_capital) or (list_content[i] in list_figure):
				return True
		return False







	def remove_project_function(self, restore:bool | None) -> None:
		project = list(self.project_data.keys())[self.listview_projectlist.index]
		#check if the archive exists for this project
		if restore == True:
			#select all items in the restore file list
			for i in range(len(self.listview_archive_content.children)):
				self.listview_archive_content.index_list.append(i)
			#call the restore archive function
			with self.suspend():
				self.restore_file_from_archive_function(True)
				#ASPC_SNOOP(self.current_project_name)
			self.message_function("ARCHIVE RESTORED!")
			#REMOVE THE ARCHIVE
			try:
				os.remove(self.current_project_data["ARCHIVE_PATH"])
				os.remove(self.current_project_data["ARCHIVE_LOG"])
			except Exception as e:
				self.message_function("Impossible to remove archive zipfile and log", "error")
			else:
				
				self.message_function("Archive zipfile and log removed", "success")
		#remove the project from data file
		del self.project_data[self.current_project_name]
		try:
			with open(os.path.join(os.getcwd(), "data/data.json"), "w") as save_file:
				json.dump(self.project_data, save_file, indent=4)
		except Exception as e:
			self.message_function("Impossible to save back project file", "error")
		else:
			self.message_function("Project file saved", "success")

		self.message_function("PROJECT REMOVED FROM DATA SUCCESSFULLY", "success")
		
		#RELOAD INFORMATIONS AND UPDATE TUI
		self.load_project_data_function()
		self.refresh_project_list_function()

		self.listview_folders.clear()
		self.listview_files.clear()
		self.listview_archive_content.clear()
		self.listview_addarchive_selected.clear()
		#self.load_user_settings_function()





	def load_project_data_function(self):
		self.message_function("\n", "message", False)
		try:
			with open(os.path.join(os.getcwd(), "data/data.json"), "r") as read_content:
				self.project_data = json.load(read_content)
		except Exception as e:
			try:
				self.message_function("Impossible to load project data", "error")
				self.message_function(e, "error", False)
			except AttributeError:
				pass
			return False
		else:
			#self.project_list = []
			try:
				self.message_function("Project data loaded", "success")
			except AttributeError:
				pass



			"""
			try:
				self.app.listview_projectlist.clear()
				#refresh the project list
				for project_name, project_data in self.project_data.items():

					self.project_list.append((os.path.basename(project_name), project_name))
					label = Label(project_name)

					#check if the project still exstis at this location
					if os.path.isdir(project_name)==False:
						label.styles.color = self.theme_variables["text-error"]

					self.app.listview_projectlist.append(ListItem(label))
			except AttributeError:
				self.message_function("Impossible to update project list\n%s"%traceback.format_exc(), "error")
				pass
			except Exception as e:
				self.message_function("Impossible to refresh project list\n%s"%traceback.format_exc(), "error")
				pass
			#return True
			"""






	def refresh_project_list_function(self):
		try:
			self.project_list.clear()
			self.listview_projectlist.clear()

			for project_name, project_data in self.project_data.items():
				self.project_list.append((os.path.basename(project_name), project_name))
				label = Label(project_name)

				if os.path.isdir(project_name)==False:
					label.styles.color = self.theme_variables["text-error"]

				self.listview_projectlist.append(ListItem(label))
		except Exception as e:
			self.message_function("Impossible to refresh project list", "error")
			self.message_function(traceback.format_exc(), "error")

		else:
			self.message_function("Project list updated", "success")









	def load_user_settings_function(self):
		if os.path.isfile(os.path.join(os.getcwd(), "data/data_user.json"))==False:
			self.message_function("Impossible to find user settings", "warning")
			self.create_user_settings_function()
			return
		else:
			try:
				with open(os.path.join(os.getcwd(), "data/data_user.json"), "r") as read_file:
					self.user_settings = json.load(read_file)
			except Exception as e:
				self.message_function("Impossible to load user settings", "error")
				self.message_function(e, "error", False)
				self.create_user_settings_function()
			else:
				self.message_function("User settings loaded successfully!", "success")
				return



	def save_dictionnary_function(self):
		#try to overwrite the current project data
		#in the json file
		try:
			with open(os.path.join(os.getcwd(), "data/data.json"), "w") as save_file:
				json.dump(self.app.project_data, save_file,indent=4)
		except Exception as e:
			self.app.message_function("Impossible to save the data file", "error")
			self.app.message_function(traceback.format_exc(), "error")
		else:
			self.app.message_function("Project data file saved", "success")



	def create_user_settings_function(self):
		self.user_settings = {
			"WIDGETS": {
				"checkbox_file_size":False,
				"checkbox_file_children":True,
				"checkbox_find_folder":False,
				"checkbox_file_gradient":False,
			},
			"COLOR": {
				"notification":"#edff3e",
				"warning":"#ffb33e",
				"important":"#ff4a3e",
				"alert":"#cb0e30",
			}
		}

		self.save_user_settings_function()



	def save_user_settings_function(self):

		try:
			os.makedirs(os.path.join(os.getcwd(), "data"), exist_ok=True)
			with open(os.path.join(os.getcwd(), "data/data_user.json"), "w") as save_file:
				json.dump(self.user_settings, save_file, indent=4)

		except Exception as e:
			self.message_function("Impossible to save user settings", "error")
			self.message_function(e, "error", False)
		else:
			self.message_function("User settings file saved", "success")


