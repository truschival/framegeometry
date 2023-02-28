"""
Data importer selection and instantiation infrastructure.

Module collects all manufacturer specific classes
"""
from .stevens import StevensImporter

importers = []
importers.append(StevensImporter)

from .giant import GiantImporter
importers.append(GiantImporter)

def is_compatible(mfg, model, year, importer):
    """
    Check if a given importer is compatible with mfg, model and year.

    Importers can limit compatibility for mfg names, models and years.
    """
    # MFG_NAME is a required attribute for all importers
    if mfg != normalize(importer.MFG_NAME):
        return False

    # Only check if importer has a restriction on model names
    try:
        if model not in importer.MODELS:
            return False
    except AttributeError:
        pass

    try:
        if year not in importer.YEARS:
            return False
    except AttributeError:
        pass

    return True


def available_importer_names():
    """Return manufacturer names for available importers"""
    mfg_names = []
    for imp in importers:
        mfg_names.append(imp.MFG_NAME)
    return mfg_names


def normalize(word):
    return word.lower().replace(' ', '-')

def instantiate_importer(mfg, model, year, *args, **kwargs):
    """
    Instantiate a concrete importer for given manufacturer, model and name.

    kwargs will be forwarded to concrete importer.

    Parameters:
        mfg (str) : manufacturer will be normalized
        model (str): model name will be normalized
        year (str): model year
    """

    _mfg = normalize(mfg)
    _model = normalize(model)
    for imp in importers:
        if is_compatible(_mfg, _model, year, imp):
            return imp(_model, year, **kwargs)
    raise KeyError(f"No importer for manufacturer/model {_mfg} {_model} found")
