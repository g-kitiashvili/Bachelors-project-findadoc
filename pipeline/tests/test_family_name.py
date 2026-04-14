from pipeline.core.persister import _last_token


def test_last_token_returns_surname() -> None:
    assert _last_token("Giorgi Tsintsadze") == "Tsintsadze"


def test_last_token_georgian_returns_surname() -> None:
    assert _last_token("გიორგი ცინცაძე") == "ცინცაძე"


def test_last_token_single_word_returns_itself() -> None:
    assert _last_token("Madonna") == "Madonna"


def test_last_token_collapses_extra_whitespace() -> None:
    assert _last_token("  Ana   Maria  Beridze  ") == "Beridze"


def test_last_token_none_returns_none() -> None:
    assert _last_token(None) is None
