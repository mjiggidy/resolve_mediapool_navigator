from __future__ import annotations
import typing

from resolvecommon.session import resolve

if typing.TYPE_CHECKING:
	import DaVinciResolveScript as bmd

def get_path_from_folder(target_folder:bmd.Folder, relative_to:bmd.Folder|None=None, accumulated_path:str="/") -> str:

	start_folder = relative_to or resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetRootFolder()

	accumulated_path += start_folder.GetName() + "/"

	if start_folder.GetUniqueId() == target_folder.GetUniqueId():
		return accumulated_path
	
	for subfolder in start_folder.GetSubFolderList():

		try:
			subfolder_path = get_path_from_folder(target_folder, subfolder, accumulated_path)
		except FileNotFoundError:
			continue
		else:
			return subfolder_path

	raise FileNotFoundError