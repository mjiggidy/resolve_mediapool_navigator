from resolvecommon.session import bmd, resolve, fusion
from ..utils import folders

ui         = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)

class TRTMediaPoolInputController:

	def __init__(self, line_edit:object):

		self._line_edit        = line_edit
		self._last_edit_length = 0

		self._window_handle = None

	def register_window_handle(self, window_handle:object):
		"""Register `TextEdited` event with dispatcher window handle"""
		
		# TODO: Figure out how to set TextEdited event on the line edit in the constructor?

		window_handle.On[self._line_edit.ID].TextEdited      = self._on_user_modified_path
		window_handle.On[self._line_edit.ID].EditingFinished = self._on_user_finished_path
		self._window_handle = window_handle

	def set_current_folder(self, folder:object):

		folder_path    = folders.get_path_from_folder(folder)
		formatted_path = "" if folder_path == "/Master" else folder_path[len("/Master/"):]

		self._line_edit.Text = formatted_path
		self._last_edit_length = len(formatted_path)

	def _subfolders_changed_event(self, subfolders:list[object]):

		print("Tryin")
		ui.QueueEvent(self._line_edit, "FolderChanged", {"who": self._line_edit.ID, "what": "FolderChanged", "subfolders":subfolders})
		print("tried")

	def _on_user_finished_path(self, event:dict):
		"""Reformat/standardize user input"""

		self._line_edit.Text = self._line_edit.Text.strip("/")

	def _on_user_modified_path(self, event:dict):
		"""Test event for media pool browser thing"""

		user_text:str   = event["Text"]
		path_normalized = user_text.lstrip("/")

		if not user_text:
			
			self._last_edit_length = 0
			return

		root = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetRootFolder()

		if "/" in path_normalized:

			last_sep_index = path_normalized.rfind("/")

			try:
				current_folder = folders.get_folder_from_path(path_normalized[:last_sep_index+1], root)
			except:
				print("invalid source path", path_normalized[:last_sep_index+1])
				self._last_edit_length = len(user_text)
				return

			partial_folder = path_normalized[last_sep_index+1:]

		else:
			current_folder = root
			partial_folder = path_normalized

		subfolders = sorted(
			filter(lambda f: f.GetName().startswith(partial_folder), current_folder.GetSubFolderList()),
			key=lambda f:f.GetName()
		)

		self._subfolders_changed_event(subfolders)

		if len(user_text) <= self._last_edit_length:
			self._last_edit_length = len(user_text)
			return

		self._last_edit_length = len(user_text)

		if subfolders:

			next_subfolder_name = subfolders[0].GetName()

			autocomplete_text = next_subfolder_name[len(partial_folder):]

			full_replace_text = user_text + autocomplete_text

			self._line_edit.Text = full_replace_text

			self._line_edit.SetSelection(len(user_text), len(full_replace_text))