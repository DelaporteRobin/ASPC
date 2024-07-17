# ASPC - AuSPiCious

A python project to detect / fix performance losses in your project / folder architecture.
The goal is to be able to give you as many informations about the points in your
folder architecture where you are loosing performances and to give you some options
to fix them, at least by returning a full report, based on custom settings you can define
to adapt the scan to your project statements.


> [!IMPORTANT]
> To create the visual side of that application I am using a library
called [Textual](https://textual.textualize.io/), which will allow you to merge the flexibility that a Console can
give you, while using the same widgets you are used to.


# TASKLIST
- [ ] Define the main TUI design for the application
- [x] Scanning the whole pipeline (each folder, files and subfolders)
- [ ] Creating the autorun program for automatic scan


# STATISTICS TO GIVE BACK AFTER ANALYSIS
- [x] Gives main data about the whole project
	number of files
	average files size
	average folder size
	number of folder
	size of the project
	
- [x] content for each folder
- [x] size for each folder and file
- [x] size classement for files and folders 
- [x] average size for each folder and for the global project
- [x] in a folder, size of a file compared to the filename proximity (file repetition / archiving)
- [x] create a dictionnary for each file extension and sort files by size in it!

- [x] get data about creation / modification date for each file (and calculate the delta)
- [ ] sort folders by size (after running through the whole pipeline)
- [ ] sorted folders by numbers of files / subfolders contained

- [ ] speed test for lightest and heaviest file (for each folder?)


# STATISTICS FOR THE BACKGROUND PROGRAM
GIVES LIVES STATISTICS ABOUT PROJECT
- [ ] list all folder data changes
- [ ] get the number of time a folder is affected by data changes
- [ ] Compare live statistics with global informations of pipeline
- [ ] update changes about pipeline in the existing data files


> [!WARNING]
> Pack important informations in a file so the TUI can load / update them quickly!