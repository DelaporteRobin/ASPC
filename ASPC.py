#ASPC main python file
#By Quazar



import os
import sys
import colorama
import time
import thrading
import scandir

from termcolor import *

colorama.init()






class ASPC_Application:
	def __init__(self):
		print("Hello World, this is ASPC!")


		self.root_folder = "//Storage01/3D4/TRASH/04_ASSET/ITEM"


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






#launch the application
if __name__ == "__main__":
	application = ASPC_Application
	application()