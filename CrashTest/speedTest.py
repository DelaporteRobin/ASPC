import os
import scandir
import time
import threading


class Application:
	def __init__(self):
		self.root_folder = "//Storage01/3D4/TRASH/04_ASSET/ITEM"


		time_start_loop = time.time()
		#self.scan_loop_function()
		time_end_loop = time.time()

		print("Done loop : %s"%(time_end_loop - time_start_loop))

		time_start_thread = time.time()
		self.scan_thread_function()
		time_end_thread = time.time()

		print("Done thread : %s"%(time_end_thread - time_start_thread))



	def scan_loop_function(self):
		i = 0
		for root, dirs, files in scandir.walk(self.root_folder):
			for f in files:
				i += 1
		print("number of files : %s"%i)


	def scan_thread_function(self):
		
		self.item_count = 0
		#get the original content of the folder
		for item in os.listdir(self.root_folder):
			if os.path.isfile(os.path.join(self.root_folder, item))==True:
				self.item_count+=1
			if os.path.isdir(os.path.join(self.root_folder, item))==True:
				x = threading.Thread(target=self.get_folder_content, args=(os.path.join(self.root_folder, item),), daemon=True)
				x.start()
		print(self.item_count)
		

	def get_folder_content(self, folder):
		print("Exploring %s"%folder)
		for root, dirs, files in scandir.walk(folder):
			for f in files:
				self.item_count += 1

		print("Done exploring %s"%folder)

	

	



Application()