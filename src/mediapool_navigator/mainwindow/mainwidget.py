from ..gui.abstract_widget import MPNAbstractWidget

ID_WINDOW_MAIN = "com.glowingpixel.navigator.mainwindow"

ID_CMB_PATH        = "cmb_mediapool_path"
ID_TXT_PATH        = "txt_mediapool_path"
ID_BTN_GO          = "btn_go"
ID_BTN_SET_CURRENT = "btn_set_current"
ID_TREE_SUBFOLDERS = "tree_subfolders"

class MPNMainWindow(MPNAbstractWidget):

	def __init__(self, ui_manager):

		super().__init__(ui_manager)

		font_about = self._ui.Font({"PointSize": 10})

		self._lbl_master = self._ui.Label({
			"Weight": 0,
			"Text": "Master /",
		})

		self._txt_media_pool_path = self._ui.LineEdit({
			"ID": ID_TXT_PATH,
			"PlaceholderText": "Media Pool Thing",
			"Events": {
				"TextEdited": True,
				"EditingFinished": True,
				"ReturnPressed": True,
			},
		})

		self._cmb_media_pool_path = self._ui.ComboBox({
			"ID": ID_CMB_PATH,
			"Editable": True,
			"LineEdit": self._txt_media_pool_path # AHAHAHAHAHA IT WORKED AHAHAHAHAA AAAAAAHAHAHHAAAAA
		})

		self._btn_go = self._ui.Button({
			"ID": ID_BTN_GO,
			"Visible": False,
			"Weight": 0,
			"Text": "Go",
			"Events": {"Clicked", True},
		})

		self._btn_set_current = self._ui.Button({
			"ID": ID_BTN_SET_CURRENT,
			"Weight": 0,
			"Text": "Use Current",
			"Events": {"Clicked": True},
		})

		self._tree_subfolders = self._ui.Tree({
			"ID": ID_TREE_SUBFOLDERS,
			"AlternatingRowColors":True,
			"RootIsDecorated": False,
			"HeaderHidden":True,
			"Events": {
				"ItemActivated": True,
				"ItemClicked": True,
			}
		})

		self._lbl_written_by = self._ui.Label({
			"Weight": 0,
			"Text"  : "Written by Michael Jordan",
			"Font"  : font_about,
			"Alignment": {
				"AlignLight":True,
				"AlignBottom": True,
			},
		})

		self._lbl_info = self._ui.Label({
			"Weight": 1,
			"Font"  : font_about,
			"Alignment": {
				"AlignRight":True,
				"AlignBottom": True,
			},
			"OpenExternalLinks": True,
		})

	def layout(self):
		return self._ui.VGroup([
			self._ui.HGroup({
					"Weight": 0,
				},[
					self._lbl_master,
					self._cmb_media_pool_path,
					self._btn_set_current,
				]
			),
			self._tree_subfolders,

			self._ui.HGroup({
				"Weight": 0,
			},[
				self._lbl_written_by,
				self._lbl_info,
			])
		])

	def media_pool_path_editor(self) -> object:
		"""The media pool path `LineEdit`"""

		return self._cmb_media_pool_path.LineEdit

	def media_pool_path_combo(self) -> object:
		"""The media pool `ComboBox`"""

		return self._cmb_media_pool_path

	def subfolder_list_view(self) -> object:
		"""The subfolder `Tree` view"""

		return self._tree_subfolders

	def button_use_current(self) -> object:
		"""The "Use Current" `Button`"""

		return self._btn_set_current

	def info_label(self) -> object:
		"""The software info label"""

		return self._lbl_info