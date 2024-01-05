import logging
import os
import subprocess
import sys

logger = logging.getLogger("CA:OpenDIR")


def open_directory(path):
    # Ensure the path is absolute
    path = os.path.abspath(path)

    # Check if the path is a directory
    if not os.path.isdir(path):
        logger.warning("The path %s is not a valid directory.", path)
        return

    # Platform-specific commands
    if sys.platform == "win32":
        os.startfile(path)
    if sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])
