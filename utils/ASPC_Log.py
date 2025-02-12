# -*- coding: utf-8 -*-


from textual.app import App, ComposeResult
from textual.widgets import Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.screen import Screen 
from textual import events
from textual import work
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on

import os

from datetime import datetime





class ASPC_LOG():
	def message_function(self, message="", severity="message",time=True):
		try:
			format_dictionnary = {
				"SEVERITY":severity,
				"CONTENT":str(message),
				"TIME":str(datetime.now())
			}
			if time == False:
				format_dictionnary["TIME"] = False


				self.global_log.append(format_dictionnary)
			try:
				self.call_from_thread(self.add_log_message_function, str(message), severity, time)


			except:
				self.add_log_message_function(str(message), severity, time)
		except Exception as e:
			self.notify(e, timeout=5)
		else:
			if severity in ["error", "warning"]:
				self.notify(str(message), severity=severity, timeout=3)
		


	def add_log_message_function(self, message, severity, time):
		if time == True:
			label = Label("[%s] %s : %s" % (str(severity.upper()), str(datetime.now()), message))
		else:
			label = Label(message)


		if severity.upper() == "SUCCESS":
			color = "text-success"
		elif severity.upper() == "NOTIFICATION":
			color = "text-accent"
		elif severity.upper() == "ERROR":
			color = "text-error"
		elif severity.upper() == "WARNING":
			color = "text-warning"
		else:
			color = "text-primary"
		
		label.styles.color = self.theme_variables[color]


		
		self.listview_log.append(ListItem(label))
		self.listview_log.scroll_end()

