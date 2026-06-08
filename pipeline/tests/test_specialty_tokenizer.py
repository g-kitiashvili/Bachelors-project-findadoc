from pipeline.services.specialty_matcher import tokenize


def test_tokenize_single_token_returns_one_element() -> None:
    assert tokenize("კარდიოლოგი") == ["კარდიოლოგი"]


def test_tokenize_compound_with_comma_returns_two_tokens() -> None:
    assert tokenize("Cardiology, Echocardiography") == ["cardiology", "echocardiography"]


def test_tokenize_compound_with_georgian_da_returns_two_tokens() -> None:
    assert tokenize("კარდიოლოგი და ექიმი") == ["კარდიოლოგი", "ექიმი"]


def test_tokenize_compound_with_slash_returns_two_tokens() -> None:
    assert tokenize("ENT / Audiology") == ["ent", "audiology"]


def test_tokenize_compound_with_hyphen_returns_two_tokens() -> None:
    assert tokenize("მეან-გინეკოლოგი") == ["მეან", "გინეკოლოგი"]


def test_tokenize_none_returns_empty_list() -> None:
    assert tokenize(None) == []


def test_tokenize_empty_string_returns_empty_list() -> None:
    assert tokenize("") == []
