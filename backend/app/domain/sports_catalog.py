"""Catálogo de deportes y modalidades. Se carga de configuración, no está fijo en el código."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Modality:
    code: str
    name: str
    players_per_side: int


@dataclass(frozen=True)
class Sport:
    code: str
    name: str
    modalities: tuple[Modality, ...]


@dataclass(frozen=True)
class SportCatalog:
    sports: tuple[Sport, ...]

    @classmethod
    def load(cls, path: Path) -> "SportCatalog":
        raw = json.loads(path.read_text(encoding="utf-8"))
        sports = tuple(
            Sport(
                code=item["code"],
                name=item["name"],
                modalities=tuple(Modality(**m) for m in item["modalities"]),
            )
            for item in raw["sports"]
        )
        return cls(sports=sports)

    def has_sport(self, code: str) -> bool:
        return any(s.code == code for s in self.sports)

    def has_modality(self, sport_code: str, modality_code: str) -> bool:
        for sport in self.sports:
            if sport.code == sport_code:
                return any(m.code == modality_code for m in sport.modalities)
        return False
