from textual.theme import Theme


DOWNTOWN_THEME = Theme(
	name="downtown",
	primary="#e41d59",
	secondary="#f76120",
	accent="#ff6947",
	foreground="#eacbd5",
	background="#29232e",
	success="#b7c664",
	warning="#cd854c",
	error="#cd5a4c",
	surface="#201b24",
	panel="#1a161d",
	dark=True,
	)

WINE_THEME = Theme(
	name="wine",
	primary="#ffedb5",
	secondary="#591e39",
	accent="#ffd966",
	background="#1b161c",
	foreground="#ffffff",
	surface="#1f1a20",
	panel="#1f1a20",
	success="#58dd31",
	warning="#f77d0b",
	error="#de3e17"
	)

OFFICE_THEME = Theme(
	name="office",
	primary="#a9eeff",
	secondary="#5debe7",
	accent="#a9eeff",
	background="#0e0e0d",
	foreground="#ffffff",
	surface="#1a1a17",
	panel = "#151513",
	success = "#a5df50",
	warning = "#df9036",
	error = "#df3657"
	)

NEON_THEME = Theme(
	name="abyss",
	background="#0d0c0e",
	primary="#67dc9e",
	secondary="#9b5fb3",
	foreground="white",
	accent="#9b5fb3",
	surface="#121013",
	panel="#121013",
	success = "#acf740",
	warning = "#fa9b2f",
	error = "#ff562c"
	)

THEME_REGISTRY = [DOWNTOWN_THEME, WINE_THEME, OFFICE_THEME, NEON_THEME]