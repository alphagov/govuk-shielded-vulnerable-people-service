import bleach


def sanitise_input(value):
    return bleach.clean(value, tags=[], strip=True) if value is not None else value
