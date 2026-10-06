class MPNFolderListController:

	def __init__(self, tree_view:object):

		self._tree_subfolders = tree_view

	def set_folder_list(self, folders:list[object]):

		self._tree_subfolders.Clear()

		for folder in folders:

			tree_item = self._tree_subfolders.NewItem()
			tree_item.Text[0] = folder.GetName()
			self._tree_subfolders.AddTopLevelItem(tree_item)