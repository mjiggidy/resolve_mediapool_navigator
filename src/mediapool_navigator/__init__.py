import logging

__VERSION__ = "0.3-dev"
URL_GITHUB  = "https://github.com/mjiggidy/resolve_mediapool_navigator/"

if not "bmd" in globals():

	logging.getLogger(__name__).debug("Importing `DaVinciResolveScript`")
	import DaVinciResolveScript as bmd

resolve    = bmd.scriptapp("resolve")
fusion     = bmd.scriptapp("fusion")
ui         = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)