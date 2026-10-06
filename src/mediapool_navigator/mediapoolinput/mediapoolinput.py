from resolvecommon.session import bmd, resolve, fusion
from ..utils import folders

import logging

logger     = logging.getLogger(__name__)

ui         = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)

class TRTMediaPoolInputController:

	def __init__(self, line_edit:object):

		self._line_edit        = line_edit
		self._last_edit_length = len(self._line_edit.Text)
		
		self._last_folder_uid  = ""
		self._last_subfolders  = dict()

	def register_window_handle(self, window_handle:object):
		"""Register `TextEdited` event with dispatcher window handle"""
		
		# TODO: Figure out how to set TextEdited event on the line edit in the constructor?

		window_handle.On[self._line_edit.ID].TextEdited       = self._on_user_modified_path
		window_handle.On[self._line_edit.ID].EditingFinished  = self._on_user_finished_path
#		window_handle.On[self._line_edit.ID].SelectionChanged = self._on_selection_changed

	def set_path_from_folder(self, folder:object):

		folder_path    = folders.get_path_from_folder(folder)
		formatted_path = "" if folder_path == "/Master" else folder_path[len("/Master/"):]

		self._set_current_folder(folder)
		self.set_path_from_text("", formatted_path)


	def _set_current_folder(self, folder:object):

		folder_uid = folder.GetUniqueId()

		if folder_uid == self._last_folder_uid:
			return

		self._last_subfolders = {subfolder.GetName(): subfolder for subfolder in folder.GetSubFolderList()}
		self._last_folder_uid = folder.GetUniqueId()

		logger.debug("Changed folder to %s", folder.GetName())

		self._subfolders_changed_event(self._last_subfolders)

	def set_path_from_text(self, base_text:str, autocomplete_text:str=""):

		self._line_edit.Text   = base_text + autocomplete_text
		self._line_edit.SetSelection(len(self._line_edit.Text), -len(autocomplete_text))

		# NOTE: SelectionChanged updates _last_edit_length, so it's important
		# to set it back here

		self._last_edit_length = len(base_text)
		logger.debug("Edit length set to ", self._last_edit_length)

	def _subfolders_changed_event(self, subfolders:list[object]):

		ui.QueueEvent(self._line_edit, "FolderChanged", {"subfolders":subfolders})

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

			subfolders = sorted(
				filter(lambda f: f.startswith(partial_folder_name), self._last_subfolders)
			)
	
		except Exception as e:
			
			logger.error("Exception: e", e, exc_info=True)
			subfolders = []

		# If the user is editing text (either backspacin' or editing in the middle), don't autocomplete
		if any([
			not subfolders,
			current_edit_length <= self._last_edit_length,
			self._line_edit.CursorPosition < current_edit_length,
		]):
			
			if not subfolders:
				logger.debug("Because no subfolders")
			
			if current_edit_length <= self._last_edit_length:
				logger.debug("Because edit length: current_length=%s, last_length=%s", current_edit_length, self._last_edit_length)
			
			if self._line_edit.CursorPosition < current_edit_length:
				logger.debug("Because cursor position")

			self._last_edit_length = current_edit_length
			return

		self.set_path_from_text(event["Text"], subfolders[0][len(partial_folder_name):])