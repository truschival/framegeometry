"""
Data importer selection and instantiation infrastructure.

Module collects all manufacturer specific classes
"""
from .stevens import StevensImporter

importers = []
importers.append(StevensImporter)

# from giant import GiantImporter


def is_compatible(mfg, model, year, importer):
    """
    Check if a given importer is compatible with mfg, model and year.

    Importers can limit compatibility for mfg names, models and years.
    """
    # MFG_NAMES is a required attribute for all importers
    if mfg not in importer.MFG_NAMES:
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


def create_data_importer(mfg, model, year, *args, **kwargs):
    """
    Select concrete data importer for given manufacturer, model and name.

    kwargs will be forwarded to concrete importer.

    Parameters:
        mfg (str) : manufacturer will be automatically capitalized
        model (str): model name
        year (str): model year
    """
    for imp in importers:
        if is_compatible(mfg, model, year, imp):
            return imp(model, year, **kwargs)
    # if mfg == 'giant':
    #     return GiantImpoerter(model,year)
