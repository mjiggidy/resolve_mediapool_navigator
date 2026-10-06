PACKAGE_ID = "com.glowingpixel.navigator"

import sys, pathlib

def workflow_integrations_path() -> pathlib.Path:

	import os

	platform_name = sys.platform.lower()

	if platform_name == "darwin":
		return pathlib.Path("/") / "Library" / "Application Support" / "Blackmagic Design" / "DaVinci Resolve" / "Workflow Integration Plugins"

	elif platform_name.startswith("win"):
		return pathlib.Path(os.environ.get("PROGRAMDATA")) /"Blackmagic Design" / "DaVinci Resolve" / "Support" / "Workflow Integration Plugins"

	else:
		raise OSError(f"{platform_name} is not a supported platform")

PATH_WORKFLOW_INTEGRATION_PLUGINS = workflow_integrations_path()
PATH_LIB = PATH_WORKFLOW_INTEGRATION_PLUGINS / PACKAGE_ID / "lib"

if not pathlib.Path(PATH_LIB).is_dir():

	print("Required library path not found: ", PATH_LIB, file=sys.stderr)
	sys.exit(1)

if str(PATH_LIB) not in sys.path:
	sys.path.insert(0, str(PATH_LIB))

from mediapool_navigator.__main__ import main

try:
	main()

except Exception as e:
	print(f"Quit unexpectedly: {str(e)}", file=sys.stderr)