import abc

class MPNAbstractWidget(abc.ABC):
	"""An abstract Media Pool Navigator widget"""

	def __init__(self, ui_manager:object):
		
		self._ui = ui_manager

	@abc.abstractmethod
	def layout(self) -> object:
		"""Return a `UIManager` widget"""