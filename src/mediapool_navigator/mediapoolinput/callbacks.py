import enum

class MPICallbacks(enum.Enum):

	CURRENT_FOLDER_CHANGED = enum.auto()
	"""The current folder has changed"""
	
	SUBFOLDERS_CHANGED = enum.auto()
	"""The available subfolders list has changed"""

