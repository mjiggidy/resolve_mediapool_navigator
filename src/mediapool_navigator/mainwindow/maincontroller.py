from __future__ import annotations

from .. import dispatcher, ui
from . import mainwidget
from ..mediapoolinput import mediapoolinput, callbacks
from resolvecommon.session import resolve

from ..utils import folders

class MPNMainController:
	"""Main application controller"""

	def __init__(self, main_widget:mainwidget.MPNMainWindow):

		self._main_widget = main_widget

		self._media_pool_input_controller = mediapoolinput.MPILineEditController(self._main_widget.media_pool_path_input())

		self._media_pool_input_controller.register_callback(callbacks.MPICallbacks.SUBFOLDERS_CHANGED, self._on_subfolders_changed)

		start_folder = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetCurrentFolder()

		if start_folder:

			self._media_pool_input_controller.set_path_from_folder(start_folder)
			

	def register_window_handle(self, window_handle:object):

#		window_handle.On[mainwidget.ID_BTN_GO].Clicked          = self._on_go_button_clicked
		window_handle.On[self._main_widget.button_use_current().ID].Clicked           = self._on_set_current_button_clicked
		window_handle.On[self._main_widget.media_pool_path_input().ID].ReturnPressed  = self._on_go_button_clicked

		self._media_pool_input_controller.register_window_handle(window_handle)

	def _on_subfolders_changed(self, subfolders:list[object]):

		print("---")
		for sub in subfolders:

			print(sub.GetName())

	def _on_set_current_button_clicked(self, event:dict):

		self.set_ready(False)

		current_folder = resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetCurrentFolder()

		if current_folder:
			self._media_pool_input_controller.set_path_from_folder(current_folder)

		self.set_ready(True)
		self._main_widget._txt_media_pool_path.SetFocus("OtherFocusReason")

	def _on_go_button_clicked(self, event:dict):

		mp = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()

		folder_path = self._main_widget._txt_media_pool_path.Text

		try:

			if folder_path.strip():
				folder = folders.get_folder_from_path(folder_path, mp.GetRootFolder())
			else:
				folder = mp.GetRootFolder()
				
			mp.SetCurrentFolder(folder)

		except Exception as e:

			print(e)

	def set_ready(self, is_ready:bool=True):

		self._main_widget.button_use_current().Enabled    = is_ready
		self._main_widget.media_pool_path_input().Enabled = is_ready
		self._main_widget.subfolder_list_view().Enabled   = is_ready