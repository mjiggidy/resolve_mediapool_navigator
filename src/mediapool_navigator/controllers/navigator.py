from __future__ import annotations
import typing

from .. import dispatcher, ui
from ..gui import mainwindow

class MPNMainController:
	"""Main application controller"""

	def __init__(self):

		self._gui_window = mainwindow.MPNMainWindow(ui)

		self._handle_window = self._setup_window()
		self._setup_events()
		self._handle_window.Show()

		dispatcher.RunLoop()

	def _setup_window(self) -> object:

		return dispatcher.AddWindow({
			"ID": mainwindow.ID_WINDOW_MAIN,
			"WindowTitle": "Media Pool Navigator",
			"FixedSize": [500,42],
			"Events": {"Close": True},
		}, [self._gui_window.layout()])

	def _setup_events(self):

		self._handle_window.On[mainwindow.ID_WINDOW_MAIN].Close   = self._on_close
		self._handle_window.On[mainwindow.ID_TXT_TEST].TextEdited = self._test_text_changed
		self._handle_window.On[mainwindow.ID_BTN_GO].Clicked      = self._on_go_button_clicked
		self._handle_window.On[mainwindow.ID_TXT_TEST].ReturnPressed = self._on_go_button_clicked

	def _on_close(self, event:dict):

		dispatcher.EndLoop(0)

	def _test_text_changed(self, event:dict):
		"""Test event for media pool browser thing"""

		from resolvecommon.folders import get_folder_from_path
		from resolvecommon.session import resolve

		user_text:str = event["Text"]
		root = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetRootFolder()

		path_normalized = user_text.lstrip("/")

		#print(event)

		if not path_normalized:
			return
		
		if "/" in path_normalized:

			last_sep_index = path_normalized.rfind("/")

			try:
				current_folder = get_folder_from_path(path_normalized[:last_sep_index+1], root)
			except:
				print("invalid source path", path_normalized[:last_sep_index+1])
				return

			partial_folder = path_normalized[last_sep_index+1:]

		else:
			current_folder = root
			partial_folder = path_normalized

		subfolders = sorted(
			filter(lambda f: f.GetName().startswith(partial_folder), current_folder.GetSubFolderList()),
			key=lambda f:f.GetName()
		)

		if subfolders:

			next_subfolder_name = subfolders[0].GetName()

			autocomplete_text = next_subfolder_name[len(partial_folder):]

			full_replace_text = user_text + autocomplete_text

			self._gui_window._txt_test.Text = full_replace_text

			self._gui_window._txt_test.SetSelection(len(user_text), len(full_replace_text))

	def _on_go_button_clicked(self, event:dict):

		from resolvecommon.folders import get_folder_from_path
		from resolvecommon.session import resolve

		mp = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()

		folder_path = self._gui_window._txt_test.Text

		try:

			if folder_path.strip():
				folder = get_folder_from_path(folder_path, mp.GetRootFolder())
			else:
				folder = mp.GetRootFolder()
				
			mp.SetCurrentFolder(folder)

		except Exception as e:

			print(e)