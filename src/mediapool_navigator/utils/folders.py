from __future__ import annotations
import typing
from os import PathLike

import logging

from resolvecommon.session import resolve

if typing.TYPE_CHECKING:
	import DaVinciResolveScript as bmd

def _search_folder_path(target_folder:bmd.Folder, start_folder:bmd.Folder, accumulated_path:str=""):
	"""Accumulate folder paths"""
	
	accumulated_path += "/" + start_folder.GetName()

	if start_folder.GetUniqueId() == target_folder.GetUniqueId():
		return accumulated_path
	
	for subfolder in start_folder.GetSubFolderList():

		try:
			subfolder_path = _search_folder_path(target_folder, subfolder, accumulated_path)
		except FileNotFoundError:
			continue
		else:
			return subfolder_path

	raise FileNotFoundError

def get_path_from_folder(target_folder:bmd.Folder, relative_to:bmd.Folder|None=None) -> str:

	relative_to = relative_to or resolve.GetProjectManager().GetCurrentProject().GetMediaPool().GetRootFolder()

	return _search_folder_path(target_folder, relative_to)


def get_folder_from_path(path:PathLike[str], root_folder:bmd.Folder) -> bmd.Folder:
	
	if not path:
		return root_folder
	
	current_folder = root_folder
	
	for search_folder_name in path.strip("/").split("/"):
		
		logging.getLogger(__name__).debug("In \"%s\" looking for \"%s\"", current_folder.GetName(), search_folder_name)
		
		try:
			current_folder = next(f for f in current_folder.GetSubFolderList() if f.GetName() == search_folder_name)
		
		except StopIteration as e:
		
			logging.getLogger(__name__).debug("Did not find \"%s\" in \"%s\"", search_folder_name, current_folder.GetName())
			raise FileNotFoundError(f"{search_folder_name} not in {current_folder.GetName()}") from e
		
		logging.getLogger(__name__).debug("Found \"%s\" in \"%s\"", search_folder_name, current_folder.GetName())
	
	return current_folder

def get_clips_from_folder(
	folder:bmd.Folder,
	recursive:bool=False,
	ignore_folder:bmd.Folder|None=None
) -> typing.Iterator[bmd.MediaPoolItem]:
	
	if ignore_folder and folder.GetUniqueId() == ignore_folder.GetUniqueId():
		
		logging.getLogger(__name__).debug("Hit an ignored folder: %s", folder.GetName())
		return
	
	yield from iter(folder.GetClipList())

	if recursive:
		for subfolder in folder.GetSubFolderList():
			yield from get_clips_from_folder(subfolder, recursive, ignore_folder=ignore_folder)