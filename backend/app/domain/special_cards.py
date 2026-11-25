"""Cartas especiales (Sprint 23): media mínima + hazañas. Se ganan una vez y quedan para siempre.

Las hazañas salen de partidos con resultado confirmado. Los goles con tipo (cabeza, penal, tiro libre,
chilena, olímpico) solo cuentan cuando el capitán o el DT rival los confirma (`goal_claim_service`).
Requisitos [SUPUESTO, ajustables con el piloto]; nada se compra.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta

from app.domain.errors import DomainError

GOAL_KINDS = ("CABEZA", "PENAL", "TIRO_LIBRE", "CHILENA", "OLIMPICO")
CITY_TOP = 3
CLAIM_WINDOW = timedelta(hours=72)  # si el rival no responde, el gol con tipo no cuenta


def validate_kinds(goals: int, kinds: list[str]) -> None:
    """Tipos marcados para los goles de un jugador en la planilla: conocidos y no más que sus goles."""
    if any(k not in GOAL_KINDS for k in kinds):
        raise DomainError("INVALID_GOAL_KIND", "Tipo de gol desconocido.")
    if len(kinds) > goals:
        raise DomainError("GOAL_KINDS_EXCEED_GOALS", "Marcaste más tipos de gol que goles del jugador.")


@dataclass(frozen=True)
class Feats:
    goals: int = 0
    hat_tricks: int = 0  # partidos con 3 goles o más
    pokers: int = 0  # 4 o más
    manitas: int = 0  # 5 o más
    kinds: dict[str, int] = field(default_factory=dict)  # goles con tipo confirmados por el rival
    cup_champion: bool = False
    city_rank: int | None = None  # puesto por media en su ciudad (1 = la mejor)

    def kind(self, name: str) -> int:
        return self.kinds.get(name, 0)

    def goal_types(self) -> int:
        """Tipos de gol distintos; los goles sin tipo cuentan como uno más (normal)."""
        tagged = sum(self.kinds.values())
        return sum(1 for n in self.kinds.values() if n > 0) + (1 if self.goals > tagged else 0)


@dataclass(frozen=True)
class FeatGoal:
    label: str
    current: int
    target: int

    @property
    def done(self) -> bool:
        return self.current >= self.target


Rule = tuple[str, Callable[[Feats], int], int]


def _goals(n: int) -> Rule:
    return (f"{n} goles", lambda f: f.goals, n)


def _kind(label: str, name: str, n: int = 1) -> Rule:
    return (label, lambda f: f.kind(name), n)


_TRIPLETES: Callable[[Feats], int] = lambda f: f.hat_tricks  # noqa: E731

# (código, media mínima, hazañas), de la más fácil a la más difícil
SPECIALS: list[tuple[str, int, list[Rule]]] = [
    ("RUBI", 75, [_goals(10)]),
    ("ESMERALDA", 75, [("3 tripletes", _TRIPLETES, 3)]),
    ("DIAMANTE", 78, [("1 póker (4 goles en un partido)", lambda f: f.pokers, 1)]),
    ("PADPARADSCHA", 78, [_goals(25)]),
    ("ALEJANDRITA", 80, [_kind("Gol de chilena", "CHILENA")]),
    ("FANTASIA", 80, [_kind("Gol olímpico", "OLIMPICO")]),
    ("GRANDIDIERITA", 82, [_kind("3 goles de tiro libre", "TIRO_LIBRE", 3)]),
    ("SERENDIBITA", 82, [("Manita (5 goles en un partido)", lambda f: f.manitas, 1)]),
    ("PAINITA", 84, [_goals(50)]),
    ("TAAFFEITA", 85, [("10 tripletes", _TRIPLETES, 10)]),
    ("DIAMANTE_ROJO", 86, [_kind("Gol de chilena", "CHILENA"), _kind("Gol olímpico", "OLIMPICO"), _goals(100)]),
    ("CORONA", 87, [("Campeón de copa", lambda f: int(f.cup_champion), 1)]),
    ("PRISMA", 88, [("5 tipos de gol distintos", Feats.goal_types, 5)]),
    ("GALAXIA", 90, [_goals(150)]),
    ("ELITE", 92, [("Top 3 de media en tu ciudad",
                    lambda f: int(f.city_rank is not None and f.city_rank <= CITY_TOP), 1)]),
]
CODES = [code for code, _m, _r in SPECIALS]


@dataclass(frozen=True)
class SpecialProgress:
    code: str
    min_media: int
    goals: list[FeatGoal]

    def reached(self, card_media: int) -> bool:
        return card_media >= self.min_media and all(g.done for g in self.goals)


def progress(feats: Feats) -> list[SpecialProgress]:
    return [SpecialProgress(code, min_media, [FeatGoal(label, min(get(feats), target), target)
                                              for label, get, target in rules])
            for code, min_media, rules in SPECIALS]


def needs_city_rank(card_media: int) -> bool:
    """El puesto en la ciudad solo importa si ya tiene la media de Élite (evita la consulta)."""
    return card_media >= SPECIALS[-1][1]


def best(codes: set[str]) -> str | None:
    """La especial más difícil de las que tiene; es la que se muestra en la carta."""
    owned = [c for c in CODES if c in codes]
    return owned[-1] if owned else None
