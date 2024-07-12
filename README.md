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
- [x] content for each folder
- [x] size for each folder and file
- [x] size classement for files and folders
- [x] average size for each folder and for the global project
- [x] size of the current file compared to the average size for that kind of file
- [ ] in a folder, size of a file compared to the filename proximity (file repetition / archiving)
- [ ] speed test for lightest and heaviest file (for each folder?)

# STATISTICS FOR THE BACKGROUND PROGRAM
- [ ] list all folder data changes
- [ ] get the number of time a folder is affected by data changes

> [!WARNING]
> Pack important informations in a file so the TUI can load / update them quickly!