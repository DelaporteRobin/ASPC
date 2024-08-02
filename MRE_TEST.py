
from textual.app import App, ComposeResult
from textual.widgets import Markdown, RadioSet, RadioButton, Input, Log, Rule, Collapsible, Checkbox, SelectionList, LoadingIndicator, DataTable, Sparkline, DirectoryTree, Rule, Label, Button, Static, ListView, ListItem, OptionList, Header, SelectionList, Footer, Markdown, TabbedContent, TabPane, Input, DirectoryTree, Select, Tabs
from textual.widgets.option_list import Option, Separator
from textual.widgets.selection_list import Selection
from textual.validation import Function, Number
from textual.screen import Screen 
from textual import events
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual import on





class Application(App):

	def __init__(self):
		super().__init__()


	def compose(self) -> ComposeResult:
		with VerticalScroll():


			with TabbedContent():
				with VerticalScroll():

					self.test_list = ListView(id = "test_list")
					yield self.test_list
					self.mount(self.test_list)


				with VerticalScroll():
					yield Label("hello world")

				


		self.update_function()


	async def on_key(self, event: events.Key) -> None:
		if event.key == "p":
			self.exit()



	def update_function(self):

		item = ListItem(Label("hello world"))
		self.test_list.append(item)

		self.set_timer(2, self.update_function)








if __name__ == "__main__":
	app = Application()
	app.run()