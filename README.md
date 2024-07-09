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
- [ ] Define the folder scan process (to create the Queue and using the Queue)
- [ ] Get a whole bunch of statistics from each folder about itself, its subfolders and files
- [ ] Return a huge data set to the user in graphs and tabs
