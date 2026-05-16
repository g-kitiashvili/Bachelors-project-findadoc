from pathlib import Path

import pytest

from pipeline.scrapers.caraps import CarapsScraper


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "caraps"


def _read(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def scraper():
    return CarapsScraper()


def test_extract_returns_doctor_with_single_clinic(scraper):
    record = scraper.extract(
        _read("profile_1.html"), "https://carapsmedline.ge/doctors/giorgi-modebadze"
    )
    assert record is not None
    assert record.source == "caraps"
    assert record.full_name_ka == "გიორგი მოდებაძე"
    assert record.specialty_ka
    assert len(record.clinics) == 1
    assert record.clinics[0].name_ka == "კარაპს მედლაინი"
    assert str(record.photo_url).startswith("https://carapsmedline.ge/upload/doctors/")


def test_extract_second_profile(scraper):
    record = scraper.extract(
        _read("profile_2.html"), "https://carapsmedline.ge/doctors/bela-jugheli"
    )
    assert record is not None
    assert record.full_name_ka == "ბელა ჯუღელი"
    assert len(record.clinics) == 1


def test_extract_returns_none_for_non_profile(scraper):
    assert scraper.extract(_read("non_profile.html"), "https://carapsmedline.ge/") is None


class _GridScraper(CarapsScraper):
    def __init__(self, pages: dict[int, str]) -> None:
        super().__init__()
        self._pages = pages

    def _grid_html(self, page: int) -> str:
        return self._pages.get(page, _read("list_empty.html"))


def test_discover_yields_profile_urls():
    scraper = _GridScraper({1: _read("list.html")})
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert all(u.startswith("https://carapsmedline.ge/doctors/") for u in urls)
    assert "https://carapsmedline.ge/doctors/giorgi-modebadze" in urls


def test_discover_stops_on_empty_page():
    scraper = _GridScraper({1: _read("list.html")})
    urls = list(scraper.discover())
    assert len(urls) >= 1
    assert all(u.startswith("https://carapsmedline.ge/doctors/") for u in urls)


def test_index_urls_not_used(scraper):
    with pytest.raises(NotImplementedError):
        scraper.index_urls()


class _EnFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages

    def get(self, url: str) -> str:
        return self._pages[url]


def test_extract_sets_english_name_and_clinic():
    ka_url = "https://carapsmedline.ge/doctors/giorgi-modebadze"
    en_url = "https://carapsmedline.ge/en/doctors/giorgi-modebadze"
    scraper = CarapsScraper(fetcher=_EnFetcher({en_url: _read("profile_1_en.html")}))
    record = scraper.extract(_read("profile_1.html"), ka_url)
    assert record.full_name_en == "Giorgi Modebadze"
    assert record.clinics[0].name_en == "Caraps Medline"
