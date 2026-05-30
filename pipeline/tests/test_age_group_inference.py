from pipeline.core.specialty_matcher import infer_age_groups


def test_infer_age_groups_pediatrician_treats_children_only() -> None:
    assert infer_age_groups("პედიატრი", "Pediatrician") == (True, False)


def test_infer_age_groups_neonatologist_treats_children_only() -> None:
    assert infer_age_groups("ნეონატოლოგი", "Neonatologist") == (True, False)


def test_infer_age_groups_childrens_emergency_treats_children_only() -> None:
    assert infer_age_groups("ბავშვთა გადაუდებელი დახმარების ექიმი", None) == (True, False)


def test_infer_age_groups_adult_specialty_treats_adults_only() -> None:
    assert infer_age_groups("კარდიოლოგი", "Cardiologist") == (False, True)


def test_infer_age_groups_mixed_treats_both() -> None:
    assert infer_age_groups("კარდიოლოგი, პედიატრი", "Cardiologist, Pediatrician") == (True, True)


def test_infer_age_groups_no_specialty_defaults_to_adults() -> None:
    assert infer_age_groups(None, None) == (False, True)


def test_infer_age_groups_family_medicine_treats_both() -> None:
    assert infer_age_groups("ოჯახის ექიმი", "Family Doctor") == (True, True)
    assert infer_age_groups("საოჯახო მედიცინა", "Family Medicine") == (True, True)
