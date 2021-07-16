import json
from urllib.parse import urlencode, parse_qsl


def pref_custom_id(custom_id: str, data: dict):
    """
    Convert dict to string.

    Args:
        custom_id (str): Name of custom_id.
        data (dict): Data you want to convert.

    Raises:
        ValueError: Data can not contain '__'.

    Returns:
        A string custom_id
    """
    data_str = urlencode(data)
    if "__" in data_str:
        raise ValueError("Data can not contain '__'")

    return f"pref_{custom_id}__{data_str}"


def un_pref_custom_id(custom_id: str, data: str):
    """
    Convert string to dict.

    Args:
        custom_id (str): Name of custom_id.
        data (str): String to parse.

    Returns:
        A dict converted from data.
    """
    start = len(custom_id) + 7
    return {i: int(j) if j.isdigit() else j for i, j in parse_qsl(data[start:])}
