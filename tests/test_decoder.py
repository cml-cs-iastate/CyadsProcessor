from processor.encoding_helpers import reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish, reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish


def test_keywords_case1():
    test_str = r'''["AP News Video CR Editor\'s Picks", \'English/Natsound\', \'16:9\']'''
    answer = ["AP News Video CR Editor's Picks", 'English/Natsound', '16:9']
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer

def test_empty_keywords_case1():
    test_str = r""
    answer = []
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer

def test_empty_keywords_empty_list():
    test_str = r"[]"
    answer = []
    assert reconstruct_utf8_list_from_str_utf8_bstr_saved_as_latin1_swedish(test_str) == answer


def test_str_reconstruct_case1():
    test_str = r'''Rep. Gowdy on Trump "Spygate" claims: Informants used "all day, every day"'''
    answer = 'Rep. Gowdy on Trump "Spygate" claims: Informants used "all day, every day"'
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer

def test_empty_str_case1():
    test_str = r""
    answer = ""
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer

def test_escaped_str_case1():
    test_str = r"Lawrence: President Donald Trump's \xe2\x80\x98Lie\xe2\x80\x99 Infiltrates Language"
    answer = r"Lawrence: President Donald Trump's ‘Lie’ Infiltrates Language"
    assert reconstruct_utf8_str_from_str_utf8_bstr_also_latin1_swedish(test_str) == answer

