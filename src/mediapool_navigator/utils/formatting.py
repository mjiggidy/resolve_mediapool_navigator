import re

PAT_NATURAL_SORT_SPLIT = re.compile(r"([0-9]+)")
"""Pattern for splitting up natural sorting groups"""

def format_string_for_natural_sort(input_string:str) -> list[str,int]:
	"""Convert a string into chunked strings 'n' ints for natural sorting"""

	return [int(t) if t.isdecimal() else t.lower() for t in PAT_NATURAL_SORT_SPLIT.split(input_string)]