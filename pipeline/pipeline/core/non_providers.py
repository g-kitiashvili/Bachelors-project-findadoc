"""Non-provider role list. A doctor whose raw specialty matches one of these and
resolves to no canonical specialty is deactivated (status='INACTIVE')."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from pipeline.core.taxonomy import normalize_alias


@dataclass(frozen=True)
class _Rule:
    text: str       # already normalized
    substring: bool


class NonProviderList:
    def __init__(self, rules: list[_Rule]) -> None:
        self._rules = rules

    @classmethod
    def load(cls, yaml_path: Path | str) -> "NonProviderList":
        rows = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8")) or []
        rules = [
            _Rule(text=normalize_alias(row["text"]), substring=(row.get("match") == "substring"))
            for row in rows
        ]
        return cls(rules)

    def matches(self, *texts: str | None) -> bool:
        for text in texts:
            if not text:
                continue
            norm = normalize_alias(text)
            for rule in self._rules:
                if rule.substring and rule.text in norm:
                    return True
                if not rule.substring and rule.text == norm:
                    return True
        return False
