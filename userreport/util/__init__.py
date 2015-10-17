class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def convert_to_type(value, value_type, default_value=None):
    """
    Try to convert 'value' to type
    :param value: The value to convert
    :param value_type: The type to convert to eg: int, float, bool
    :param default_value: The default returned value if the conversion fails
    :return:
    """

    try:
        return value_type(value)
    except ValueError:
        return default_value


def convert_to_int(value, default_value=None):
    """
    Try to convert a value to an int
    :param value: The value to convert
    :param default_value: The default returned value if the conversion fails
    :return: The converted value
    """
    return convert_to_type(value, int, default_value)


def convert_to_float(value, default_value=None):
    """
    Try to convert a value to an float
    :param value: The value to convert
    :param default_value: The default returned value if the conversion fails
    :return: The converted value
    """
    return convert_to_type(value, float, default_value)
