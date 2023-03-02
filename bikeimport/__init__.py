"""
Data importer selection and instantiation infrastructure.

Module collects all manufacturer specific classes
"""

from .globals import normalize
from .stevens import StevensImporter

importers = []
importers.append(StevensImporter)

from .giant import GiantImporter
importers.append(GiantImporter)

from .cube import CubeImporter
importers.append(CubeImporter)

def is_compatible(mfg, importer):
    """
    Check if a given importer is compatible with mfg, model and year.

    Importers can limit compatibility for mfg names, models and years.
    """
    # MFG_NAME is a required attribute for all importers
    if mfg != normalize(importer.MFG_NAME):
        return False

    return True


def available_importer_names():
    """Return manufacturer names for available importers"""
    mfg_names = []
    for imp in importers:
        mfg_names.append(imp.MFG_NAME)
    return mfg_names

def instantiate_importer(mfg, *args, **kwargs):
    """
    Instantiate a concrete importer for given manufacturer, model and name.

    kwargs will be forwarded to concrete importer.

    Parameters:
        mfg (str) : manufacturer will be normalized
    """

    _mfg = normalize(mfg)
    for imp in importers:
        if is_compatible(_mfg, imp):
            return imp(**kwargs)
    raise KeyError(f"No importer for manufacturer: {_mfg} found")

