#ASPC main python file
#By Quazar



import os
import sys




"""

FEATURES LISTS FOR THE FIRST VERSION
	from a defined project folder run recurcively in each folder and subfolder
	from each folder get data and store them in a dictionnary created at each project scan

	define the multiprocessing workflow -> creating a queue of folder for multiprocessing
										-> USE SCANDIR TO RUN THROUGH THE FOLDER ARCHITECTURE
	define a process to try the latency of a folder
	define the importance of a folder
		-> get the number of access to that folder to define its importance and to class it
			as main folder
		-> for each folder get :
			number of files
			number of subfolder
			size of each elements
			type of each elements
			last date used?
			recurrence of the element in the subfolder (autosave detection?)

		-> create a latency test
			-> create / copy / delete / edit a file or a content?
			-> create a temp folder where each file will be copied / opened / removed
				-> for each step get the delta

		-> get statistics
			average size for each elements based on settings and other elements in archicture (extension? Name? Location?)



	create a system with threading to dig into folders and create the Queue for multiprocessing?
	I NEED TO CREATE A QUEUE AND TO FIND AN OPTIMIZED WAY!!!


"""



class ASPC_Application:
	def __init__(self):
		print("Hello World, this is ASPC!")






#launch the application
if __name__ == "__main__":
	application = ASPC_Application()
	appliction()