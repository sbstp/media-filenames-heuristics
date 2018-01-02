def min(a, b):
    """
    Min that allows None values.
    """
    if a is None and b is None:
        raise ValueError
    elif a is None:
        return b
    elif b is None:
        return a
    elif a < b:
        return a
    else:
        return b
