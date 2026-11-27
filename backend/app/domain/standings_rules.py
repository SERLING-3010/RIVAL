"""Tabla de posiciones: 3 puntos por victoria, 1 por empate (Sprint 8).

Solo se le pasan partidos con resultado confirmado; un partido en disputa no suma (Sprint 0, 4.4.1).
Orden: puntos, diferencia de goles, goles a favor y nombre (sin tildes ni mayúsculas).
"""

from dataclasses import dataclass

from app.domain.text_keys import search_key


@dataclass(frozen=True)
class MatchScore:
    host_id: int
    guest_id: int
    host_goals: int
    guest_goals: int


@dataclass(frozen=True)
class StandingRow:
    team_id: int
    name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


def standings(names: dict[int, str], matches: list[MatchScore]) -> list[StandingRow]:
    acc = {t: [0, 0, 0, 0, 0, 0] for t in names}  # PJ, G, E, P, GF, GC
    for m in matches:
        for team, mine, theirs in ((m.host_id, m.host_goals, m.guest_goals), (m.guest_id, m.guest_goals, m.host_goals)):
            row = acc.setdefault(team, [0, 0, 0, 0, 0, 0])
            row[0] += 1
            row[1 if mine > theirs else 2 if mine == theirs else 3] += 1
            row[4] += mine
            row[5] += theirs
    rows = [
        StandingRow(team_id=t, name=names.get(t, ""), played=r[0], won=r[1], drawn=r[2], lost=r[3],
                    goals_for=r[4], goals_against=r[5], goal_difference=r[4] - r[5], points=3 * r[1] + r[2])
        for t, r in acc.items()
    ]
    return sorted(rows, key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, search_key(r.name)))
