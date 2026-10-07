import logging, typing

from resolvecommon.session import bmd, resolve, fusion
from ..utils import folders
from .callbacks import MPICallbacks

logger     = logging.getLogger(__name__)

ui         = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)

class MPILineEditController:

	def __init__(self, line_edit:object):

		self._line_edit        = line_edit
		self._last_edit_length = len(self._line_edit.Text)

		self._last_folder_uid  = ""
		self._last_subfolders  = list[object]

		self._callbacks:dict[MPICallbacks, list[typing.Callable]] = dict()

		# Register callback types
		for callback in MPICallbacks:
			self._callbacks[callback] = []

	def register_window_handle(self, window_handle:object):
		"""Register `TextEdited` event with dispatcher window handle"""
		
		# TODO: Figure out how to set TextEdited event on the line edit in the constructor?

		window_handle.On[self._line_edit.ID].TextEdited       = self._on_user_modified_path
		window_handle.On[self._line_edit.ID].EditingFinished  = self._on_user_finished_path
#		window_handle.On[self._line_edit.ID].SelectionChanged = self._on_selection_changed

	def set_path_from_folder(self, folder:object):
		"""Set the current path from a given media pool folder object"""

		folder_path    = folders.get_path_from_folder(folder)
		formatted_path = "" if folder_path == "/Master" else folder_path[len("/Master/"):]

		self._set_current_folder(folder)
		self.set_path_from_text("", formatted_path)

	def set_path_from_text(self, base_text:str, autocomplete_text:str=""):
		"""Set the current path from text"""

		self._line_edit.Text   = base_text + autocomplete_text
		self._line_edit.SetSelection(len(self._line_edit.Text), -len(autocomplete_text))

		self._last_edit_length = len(base_text)

		logger.debug("Edit length set to ", self._last_edit_length)

	def register_callback(self, callback:MPICallbacks, callback_function:typing.Callable):

		self._callbacks[callback].append(callback_function)

	def _send_callback(self, callback:MPICallbacks, args:typing.Any=None):

		for cb in self._callbacks[callback]:
			cb(args)

	def _set_current_folder(self, folder:object|None):

		folder_uid = folder.GetUniqueId() if folder else None

		if folder_uid == self._last_folder_uid:
			return

		self._last_folder_uid = folder_uid
		self._last_subfolders = sorted(folder.GetSubFolderList(), key=lambda f: f.GetName()) if folder else []

		logger.debug("Changed folder to %s", folder.GetName() if folder else "[None]")

		self._send_callback(MPICallbacks.CURRENT_FOLDER_CHANGED, folder)
		
		# NOTE: Kinda double-fires
		self._send_callback(MPICallbacks.SUBFOLDERS_CHANGED, self._last_subfolders)

	def _on_selection_changed(self, event:dict):

		# NOTE: Not in use
		# User selection should probably break autocomplete
		self._last_edit_length = len(self._line_edit.Text)
	
	def _on_user_finished_path(self, event:dict):
		"""Reformat/standardize user input"""

		self._line_edit.Text = self._line_edit.Text.strip("/")

	def _on_user_modified_path(self, event:dict):
		"""Test event for media pool browser thing"""

		current_edit_length = len(event["Text"])

		# Add a trailing slash to allow for "root" folders to be split between "" (Master) and the partial folder name
		# NOTE: Yes, that comment made sense to me when I wrote it
		
		sanitized_text:str = "/" + event["Text"] if not event["Text"].startswith("/") else event["Text"]

		# Split input string into base path and "partial" (or... full, really) folder name
		# NOTE: For a trailing slash, partial_folder_name becomes "" which is perfect

		base_path, partial_folder_name = sanitized_text.rsplit("/", 1)
		
		# Try to resolve the base Folder handle from the given path, and query any subfolders therein
		# If any of this fails, something's invalid about the path, so just set subfolders to an empty
		# list so we don't autocomplete anything atoll, and any subfolder listings are cleared out

		try:

			root_folder = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetRootFolder()
			base_folder = folders.get_folder_from_path(base_path, root_folder)

			self._set_current_folder(base_folder)

			filtered_subfolders = list(
				filter(lambda f: f.GetName().startswith(partial_folder_name), self._last_subfolders)
			)
	
		except FileNotFoundError as e:
			
			logger.error("Invalid media pool folder: %s", e)
			
			self._set_current_folder(None)
			filtered_subfolders = []
		
		self._send_callback(MPICallbacks.SUBFOLDERS_CHANGED, filtered_subfolders)

		# If the user is editing text (either backspacin' or editing in the middle), don't autocomplete
		if any([
#			not filtered_subfolders,
			current_edit_length <= self._last_edit_length,
			self._line_edit.CursorPosition < current_edit_length,
		]):
			
#			if not filtered_subfolders:
#				logger.debug("Because no subfolders")
			
			if current_edit_length <= self._last_edit_length:
				logger.debug("Because edit length: current_length=%s, last_length=%s", current_edit_length, self._last_edit_length)
			
			if self._line_edit.CursorPosition < current_edit_length:
				logger.debug("Because cursor position")

			self._last_edit_length = current_edit_length
			return


		next_subfolder_name = filtered_subfolders[0].GetName() if filtered_subfolders else ""

		self.set_path_from_text(event["Text"], next_subfolder_name[len(partial_folder_name):])