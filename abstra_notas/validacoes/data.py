from dateutil.parser import parse
from datetime import date


def normalizar_data(data, optional=False):
    if data is None and optional:
        return None

    if isinstance(data, str):
        return parse(data).date()
    elif isinstance(data, date):
        return data
    else:
        raise ValueError(f"Data inválida. {repr(data)}")
