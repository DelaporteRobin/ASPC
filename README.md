# ASPC - AuSPiCious

A python project to detect / fix performance losses in your project / folder architecture.
The goal is to be able to give you as many informations about the points in your
folder architecture where you are loosing performances and to give you some options
to fix them, at least by returning a full report, based on custom settings you can define
to adapt the scan to your project statements.


> [!IMPORTANT]
> To create the visual side of that application I am using a library
called [Textual](https://textual.textualize.io/), which will allow you to merge the flexibility that a Console can
gives you, while using the same widgets you are used to.


# TASKLIST
- [x] Define the main TUI design for the application
- [x] Scanning the whole pipeline (each folder, files and subfolders)
- [ ] Creating the autorun program for automatic scan
- [ ] Define settings for the scan (to skip specified scan task)
- [ ] Get the previous scan informations when launching the program



# STATISTICS TO DISPLAY ON THE TUI
- [ ] files sorted by size
- [ ] folder sorted by number of subfolders
- [ ] folers by size contained (global size of the project)
- [ ] size of the files contained compared to number of size (compared with average size for folder)
- [ ] heaviest folder in project
- [ ] heaviest files for each extension (compared to extension average size)
- [ ] comparizon by similarities

# STATISTICS FOR THE BACKGROUND PROGRAM
GIVES LIVES STATISTICS ABOUT PROJECT
- [ ] list all folder data changes
- [ ] get the number of time a folder is affected by data changes
- [ ] Compare live statistics with global informations of pipeline
- [ ] update changes about pipeline in the existing data files


> [!WARNING]
> Pack important informations in a file so the TUI can load / update them quickly!