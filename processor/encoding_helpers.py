from ast import literal_eval
from typing import List


def convert_non_ascii_list_to_encodeable_ascii(list: List[str]) -> str:
    python_repr_of_binary_str = str(str(list).encode("utf-8"))
    # Chop off the binary string parts b"  and "
    return python_repr_of_binary_str[2:-1]


def reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(text: str) -> List[str]:
    """Code execution possible. Converts byte string string converted to ascii to a list of utf8 original """
    # assert has list repr beginning and end
    if text == "":
        return []
    assert text[0] == "["
    assert text[-1] == "]"
    bstr_list_escaped = f'b"""{text}"""'
    bstr_list = literal_eval(bstr_list_escaped)
    assert isinstance(bstr_list, bytes)
    # b"['foo', 'bar']"
    # decode from utf-8 encoding # assumption of input bytes
    bstr_list_utf8 = bstr_list.decode("utf-8")
    # eval the str repr of a list as a list
    decoded_list = literal_eval(bstr_list_utf8)
    assert isinstance(decoded_list, list)
    return decoded_list


def convert_non_ascii_string_to_encodeable_ascii(text: str) -> str:
    python_repr_of_binary_str = str(text.encode("utf-8"))
    # Chop off the binary string parts b"  and "
    return python_repr_of_binary_str[2:-1]


def reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(text: str) -> str:
    """Code execution possible. Converts byte string string converted to ascii to a string utf8 original """
    # assert has list repr beginning and end
    try:
        bstr_string_escaped = f'b"{text}"'
        bstr_string = literal_eval(bstr_string_escaped)
    except SyntaxError:
        bstr_string_escaped = "b'" + text + "'"
        bstr_string = literal_eval(bstr_string_escaped)
    assert isinstance(bstr_string, bytes)
    # b"foo"
    # decode from utf-8 encoding # assumption of input bytes
    string_utf8 = bstr_string.decode("utf-8")
    # eval the str repr of a list as a list
    assert isinstance(string_utf8, str)
    return string_utf8
