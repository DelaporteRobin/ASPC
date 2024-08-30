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


# TASKLIST FOR PROGRAMMER
- BBrother also watching for folder creation in the pipeline (each changes)
- remove the messages when selecting a folder
- display more filters to display informations in the TUI


- Informations to display when selecting a folder
	percentage of the project contained in the folder
	number of items contained in the folder
	compared to the number of items contained in the project

	-> remember to enable similarity feature only for specific kind of files (most of the time useless for textures because of UDIMS)

	-> when selecting a folder, checkbox to highlight childrens

	-> warnings about a folder are stored as markdown for the markdown viewer on the right side

	-> folder searching bug has a bug
	-> file searching bar doesn't search for anything


	-> update in live the live mode window
	-> color files and folder depending of is they exists or not
	-> button to relaunch the live mode exec
	



> [!WARNING]
> Pack important informations in a file so the TUI can load / update them quickly!