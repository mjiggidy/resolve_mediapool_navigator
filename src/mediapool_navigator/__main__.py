from .mainwindow import maincontroller, mainwidget
from . import ui, dispatcher

def _on_main_closed(event:dict):

	dispatcher.ExitLoop(0)

def main():

	main_widget = mainwidget.MPNMainWindow(ui)
	app = maincontroller.MPNMainController(main_widget)

	wnd_main = dispatcher.AddWindow({
			"ID": mainwidget.ID_WINDOW_MAIN,
			"WindowTitle": "Media Pool Navigator Pro!",
			"FixedSize": [500,140],
			"Events": {"Close": True},
		}, [main_widget.layout()])

	wnd_main.On[mainwidget.ID_WINDOW_MAIN].Close = _on_main_closed

	app.register_window_handle(wnd_main)

	wnd_main.Show()

	dispatcher.RunLoop()


if __name__ == "__main__":

	main()