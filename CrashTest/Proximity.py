import os
import Levenshtein
import colorama

from termcolor import *


colorama.init()

folder = "D:/WORK/LIGHTING/Prospect/maya/autosave/"
folder_content = os.listdir(folder)
file_list = []
for item in folder_content:
	if os.path.isfile(os.path.join(folder,item))==True:
		file_list.append(item)




def comparison_function(comparison, target):
	distance = Levenshtein.distance(target, comparison)
	length = max(len(target), len(comparison))
	similitude = ((length - distance) / length)*100

	#print("%s : [%s ; %s]"%(similitude,target, comparison))
	return similitude

checked_file = []
final_dictionnary = {}


for file in file_list:

	if file not in checked_file:
		i = len(list(final_dictionnary.keys()))
		checked_file.append(file)
		print(colored("TEST PROXIMITY : %s"%file, "green"))
		proxi_list = [file]
		dictionnary_i = 0

		for comparison in file_list:
			if comparison not in checked_file:
				if comparison != file:
					value = comparison_function(comparison,file)
					
					if value > 90:
						checked_file.append(comparison)
						proxi_list.append(comparison)
						#print("%s : %s"%(value,comparison))
		#print(colored("KEY OF THE DICTIONNARY : %s"%i, "yellow"))
		#print(proxi_list)

		final_dictionnary[len(list(final_dictionnary.keys()))] = proxi_list




	

for key, value in final_dictionnary.items():
	print(colored(key, "magenta"))

	for v in value:
		print("		%s"%v)
