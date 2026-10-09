from __future__ import annotations
import logging, typing

if typing.TYPE_CHECKING:
	import DaVinciResolveScript as dvr

from .. import resolve
from ..utils import folders, formatting
from .callbacks import MPICallbacks

_logger     = logging.getLogger(__name__)

class MPIFolderInfo:
	"""Path and subfolder info for a given folder"""

	def __init__(self, ):

		self._folder_handle:dvr.Folder|None = None
		self._folder_path:str   = ""

	def set_folder(self, folder:dvr.Folder) -> bool:
		"""Set the current folder.  Returns `True` if the folder changed since last."""

		if self._folder_handle and self._folder_handle.GetUniqueId() == folder.GetUniqueId():

			_logger.debug("Set current folder ignored because unchanged")
			return False

		self._folder_handle = folder
		self._folder_path   = folders.get_path_from_folder(folder)

		return True

	def clear_folder(self) -> bool:
		"""Clear the current folder.  Returns `True` if this is a change."""

		if not self._folder_handle:
			return False

		self._folder_handle = None
		self._folder_path   = ""

		return True

	def folder(self) -> dvr.Folder|None:

		return self._folder_handle

	def folder_path(self) -> str:

		return self._folder_path

	def subfolders(self) -> list[dvr.Folder]:

		return sorted(
			self._folder_handle.GetSubFolderList(),
			key = lambda f: formatting.format_string_for_natural_sort(f.GetName())
		) if self._folder_handle else []

	def subfolder_paths(self) -> list[str]:

		return [self.folder_path() + "/" + f.GetName() for f in self.subfolders()]
		

class MPILineEditController:

	def __init__(self, line_edit:object):

		self._folder_tracker   = MPIFolderInfo()

		self._line_edit        = line_edit
		self._last_edit_length = len(self._line_edit.Text)

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

	def current_folder_info(self) -> MPIFolderInfo:

		return self._folder_tracker

	def set_path_from_folder(self, folder:object):
		"""Set the current path from a given media pool folder object"""

		self._folder_tracker.set_folder(folder)

		folder_path = self._folder_tracker.folder_path()
		formatted_path = "" if folder_path == "/Master" else folder_path[len("/Master/"):]
		self.set_path_from_text("", formatted_path)

	def set_path_from_text(self, base_text:str, autocomplete_text:str=""):
		"""Set the current path from text"""

		self._line_edit.Text   = base_text + autocomplete_text
		self._line_edit.SetSelection(len(self._line_edit.Text), -len(autocomplete_text))

		self._last_edit_length = len(base_text)

		_logger.debug("Edit length set to ", self._last_edit_length)

	def register_callback(self, callback:MPICallbacks, callback_function:typing.Callable):

		self._callbacks[callback].append(callback_function)

	def _send_callback(self, callback:MPICallbacks, args:typing.Any=None):

		for cb in self._callbacks[callback]:
			cb(args)

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

			if self._folder_tracker.set_folder(base_folder):
				self._send_callback(MPICallbacks.CURRENT_FOLDER_CHANGED, base_folder)

			filtered_subfolders = list(
				filter(lambda f: f.GetName().startswith(partial_folder_name), self._folder_tracker.subfolders())
			)
	
		except FileNotFoundError as e:
			
			_logger.error("Invalid media pool folder: %s", e)
			
			if self._folder_tracker.clear_folder():
				self._send_callback(MPICallbacks.CURRENT_FOLDER_CHANGED, None)

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
				_logger.debug("Because edit length: current_length=%s, last_length=%s", current_edit_length, self._last_edit_length)
			
			if self._line_edit.CursorPosition < current_edit_length:
				_logger.debug("Because cursor position")

			self._last_edit_length = current_edit_length
			return


		next_subfolder_name = filtered_subfolders[0].GetName() if filtered_subfolders else ""

		self.set_path_from_text(event["Text"], next_subfolder_name[len(partial_folder_name):])