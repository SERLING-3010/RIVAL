"""Logros e insignias (Sprint 17): se calculan de datos reales, no se guardan ni se compran.

Cada insignia dice cuándo se ganó (el partido o el check-in que la completó) o cuánto falta.
Solo cuentan partidos con resultado confirmado. No hay insignias de sanciones ni de dinero.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Outcome(StrEnum):
    WIN = "WIN"
    DRAW = "DRAW"
    LOSS = "LOSS"


@dataclass(frozen=True)
class PlayedMatch:
    at: datetime  # cuándo se confirmó el resultado
    outcome: Outcome
    goals: int = 0


@dataclass(frozen=True)
class Badge:
    code: str
    name: str
    description: str
    earned_at: datetime | None
    progress: str | None  # "3/10" mientras no se gana


@dataclass(frozen=True)
class _Def:
    code: str
    name: str
    description: str
    target: int
    counts: Callable[[PlayedMatch], int]


def _count(matches: list[PlayedMatch], d: _Def) -> Badge:
    total = 0
    for m in sorted(matches, key=lambda x: x.at):
        total += d.counts(m)
        if total >= d.target:
            return Badge(d.code, d.name, d.description, m.at, None)
    return Badge(d.code, d.name, d.description, None, f"{min(total, d.target)}/{d.target}")


def _dated(code: str, name: str, description: str, dates: list[datetime], target: int) -> Badge:
    ordered = sorted(dates)
    if len(ordered) >= target:
        return Badge(code, name, description, ordered[target - 1], None)
    return Badge(code, name, description, None, f"{len(ordered)}/{target}")


def _unbeaten(matches: list[PlayedMatch], streak: int) -> Badge:
    run = 0
    for m in sorted(matches, key=lambda x: x.at):
        run = 0 if m.outcome == Outcome.LOSS else run + 1
        if run >= streak:
            return Badge("UNBEATEN_5", "Invicto", f"{streak} partidos seguidos sin perder.", m.at, None)
    return Badge("UNBEATEN_5", "Invicto", f"{streak} partidos seguidos sin perder.", None, f"{run}/{streak}")


def _one(_m: PlayedMatch) -> int:
    return 1


def _win(m: PlayedMatch) -> int:
    return 1 if m.outcome == Outcome.WIN else 0


def _goals(m: PlayedMatch) -> int:
    return m.goals


def _hat_trick(m: PlayedMatch) -> int:
    return 1 if m.goals >= 3 else 0


PLAYER_DEFS = [
    _Def("DEBUT", "Debut", "Jugó su primer partido con resultado confirmado.", 1, _one),
    _Def("MATCHES_10", "10 partidos", "Jugó 10 partidos.", 10, _one),
    _Def("MATCHES_50", "50 partidos", "Jugó 50 partidos.", 50, _one),
    _Def("GOALS_10", "Goleador", "Marcó 10 goles.", 10, _goals),
    _Def("HAT_TRICK", "Triplete", "Marcó 3 goles o más en un partido.", 1, _hat_trick),
    _Def("WINS_10", "10 victorias", "Ganó 10 partidos.", 10, _win),
]
TEAM_DEFS = [
    _Def("FIRST_WIN", "Primera victoria", "Ganó su primer partido.", 1, _win),
    _Def("WINS_10", "10 victorias", "Ganó 10 partidos.", 10, _win),
    _Def("MATCHES_25", "25 partidos", "Jugó 25 partidos.", 25, _one),
]
PUNCTUAL_TARGET = 5


def player_badges(matches: list[PlayedMatch], check_ins: list[datetime], cup_titles: list[datetime]) -> list[Badge]:
    return [_count(matches, d) for d in PLAYER_DEFS] + [
        _dated("PUNCTUAL", "Puntual", f"Hizo check-in en la cancha en {PUNCTUAL_TARGET} partidos.", check_ins,
               PUNCTUAL_TARGET),
        _dated("CUP_CHAMPION", "Campeón de copa", "Jugó la final y la ganó.", cup_titles, 1),
    ]


def team_badges(matches: list[PlayedMatch], cup_titles: list[datetime]) -> list[Badge]:
    return [_count(matches, d) for d in TEAM_DEFS] + [
        _unbeaten(matches, 5),
        _dated("CUP_CHAMPION", "Campeón de copa", "Ganó la copa de su liga.", cup_titles, 1),
    ]


def outcome(mine: int, theirs: int) -> Outcome:
    return Outcome.WIN if mine > theirs else Outcome.DRAW if mine == theirs else Outcome.LOSS
