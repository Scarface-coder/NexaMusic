import logging
import glob
from os.path import basename, dirname, isfile

LOGGER = logging.getLogger("Shadow.modules")

LOAD = []     # modules to forcibly load
NO_LOAD = []  # modules to skip

def __list_all_modules():
    """Scan the modules folder and return a list of modules to load."""
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    if LOAD or NO_LOAD:
        to_load = LOAD if LOAD else all_modules
        if NO_LOAD:
            LOGGER.info(f"Not loading: {NO_LOAD}")
            to_load = [m for m in to_load if m not in NO_LOAD]
        return to_load

    return all_modules

ALL_MODULES = __list_all_modules()
LOGGER.info(f"Modules to load: {ALL_MODULES}")

__all__ = ALL_MODULES + ["ALL_MODULES"]