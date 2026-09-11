from .abstract_widget import MPNAbstractWidget

ID_WINDOW_MAIN = "com.glowingpixel.navigator.mainwindow"

ID_TXT_TEST        = "txt_test_thing"
ID_BTN_GO          = "btn_go"
ID_BTN_SET_CURRENT = "btn_set_current"

class MPNMainWindow(MPNAbstractWidget):

	def __init__(self, ui_manager):

		super().__init__(ui_manager)

		self._lbl_master = self._ui.Label({
			"Weight": 0,
			"Text": "Master/",
		})

		self._txt_test = self._ui.LineEdit({
			"ID": ID_TXT_TEST,
			"PlaceholderText": "Media Pool Thing",
			"Events": {"TextEdited":True, "ReturnPressed":True},
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

	def layout(self):
		return self._ui.HGroup([
			self._lbl_master,
			self._txt_test,
			self._btn_set_current,
		])