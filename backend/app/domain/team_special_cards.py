"""Cartas especiales del equipo (Sprint 23): media del equipo + hazaña del equipo, ganadas para siempre.

Usan los mismos códigos y diseños que las del jugador (`special_cards`). La carta básica del equipo
sale de la media de sus titulares con los rangos de `card_rules.tier`. Las hazañas solo cuentan
partidos con resultado confirmado. Requisitos [SUPUESTO, ajustables con el piloto]; nada se compra.
"""

from collections.abc import Callable
from dataclasses import dataclass

from app.domain.special_cards import FeatGoal, SpecialProgress

GOLEADA = 5  # ganar por 5 goles o más
CITY_TOP = 3


@dataclass(frozen=True)
class TeamFeats:
    wins: int = 0
    goals: int = 0
    clean_sheets: int = 0  # el rival no marcó
    goleadas: int = 0
    best_win_streak: int = 0
    best_unbeaten_streak: int = 0
    cups: int = 0
    leagues: int = 0
    doubles: int = 0  # liga y copa de la misma liga
    city_rank: int | None = None  # puesto por nivel entre los equipos de su ciudad


def feats_from_scores(scores: list[tuple[int, int]], cups: int = 0, leagues: int = 0, doubles: int = 0,
                      city_rank: int | None = None) -> TeamFeats:
    """scores: (goles propios, goles del rival) de cada partido confirmado, del más antiguo al más nuevo."""
    wins = clean = goleadas = streak = unbeaten = best_streak = best_unbeaten = 0
    for mine, theirs in scores:
        won = mine > theirs
        wins += won
        clean += theirs == 0
        goleadas += mine - theirs >= GOLEADA
        streak = streak + 1 if won else 0
        unbeaten = unbeaten + 1 if mine >= theirs else 0
        best_streak, best_unbeaten = max(best_streak, streak), max(best_unbeaten, unbeaten)
    return TeamFeats(wins=wins, goals=sum(m for m, _t in scores), clean_sheets=clean, goleadas=goleadas,
                     best_win_streak=best_streak, best_unbeaten_streak=best_unbeaten, cups=cups,
                     leagues=leagues, doubles=doubles, city_rank=city_rank)


Rule = tuple[str, Callable[[TeamFeats], int], int]


def _wins(n: int) -> Rule:
    return (f"{n} victorias", lambda f: f.wins, n)


def _goals(n: int) -> Rule:
    return (f"{n} goles del equipo", lambda f: f.goals, n)


def _clean(n: int) -> Rule:
    return (f"{n} vallas invictas", lambda f: f.clean_sheets, n)


TEAM_SPECIALS: list[tuple[str, int, list[Rule]]] = [
    ("RUBI", 75, [_wins(10)]),
    ("ESMERALDA", 75, [_goals(50)]),
    ("DIAMANTE", 78, [_clean(5)]),
    ("PADPARADSCHA", 78, [_wins(25)]),
    ("ALEJANDRITA", 80, [("Racha de 5 victorias", lambda f: f.best_win_streak, 5)]),
    ("FANTASIA", 80, [("Una goleada (por 5 o más)", lambda f: f.goleadas, 1)]),
    ("GRANDIDIERITA", 82, [_clean(10)]),
    ("SERENDIBITA", 82, [("10 partidos sin perder", lambda f: f.best_unbeaten_streak, 10)]),
    ("PAINITA", 84, [_goals(200)]),
    ("TAAFFEITA", 85, [_wins(50)]),
    ("DIAMANTE_ROJO", 86, [_wins(100), ("3 goleadas", lambda f: f.goleadas, 3)]),
    ("CORONA", 87, [("Campeón de copa", lambda f: f.cups, 1)]),
    ("PRISMA", 88, [("Campeón de liga", lambda f: f.leagues, 1)]),
    ("GALAXIA", 90, [("Doblete: liga y copa", lambda f: f.doubles, 1)]),
    ("ELITE", 92, [("Top 3 de nivel en su ciudad",
                    lambda f: int(f.city_rank is not None and f.city_rank <= CITY_TOP), 1)]),
]


def progress(feats: TeamFeats) -> list[SpecialProgress]:
    return [SpecialProgress(code, min_media, [FeatGoal(label, min(get(feats), target), target)
                                              for label, get, target in rules])
            for code, min_media, rules in TEAM_SPECIALS]


def needs_city_rank(team_media: int) -> bool:
    return team_media >= TEAM_SPECIALS[-1][1]
