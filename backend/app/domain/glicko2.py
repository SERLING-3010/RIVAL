"""Glicko-2 (Glickman, 2013) para el nivel de los equipos (ADR-005, Sprint 10).

Además del nivel mide la incertidumbre (RD) y la volatilidad: un equipo nuevo tiene RD alta,
así que sus primeros resultados lo mueven mucho y el sistema sabe que aún no es confiable.
"""

import math
from dataclasses import dataclass

SCALE = 173.7178
TAU = 0.5
EPSILON = 0.000001


@dataclass(frozen=True)
class Rating:
    rating: float = 1500.0
    rd: float = 350.0
    volatility: float = 0.06


@dataclass(frozen=True)
class GameResult:
    opponent: Rating
    score: float  # 1 victoria, 0,5 empate, 0 derrota


def _g(phi: float) -> float:
    return 1 / math.sqrt(1 + 3 * phi * phi / (math.pi * math.pi))


def _expected(mu: float, mu_j: float, phi_j: float) -> float:
    return 1 / (1 + math.exp(-_g(phi_j) * (mu - mu_j)))


def _new_volatility(sigma: float, phi: float, v: float, delta: float) -> float:
    """Paso 5 del artículo: algoritmo de Illinois para la nueva volatilidad."""
    a = math.log(sigma * sigma)

    def f(x: float) -> float:
        ex = math.exp(x)
        return ex * (delta**2 - phi**2 - v - ex) / (2 * (phi**2 + v + ex) ** 2) - (x - a) / TAU**2

    big_a = a
    if delta**2 > phi**2 + v:
        big_b = math.log(delta**2 - phi**2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        big_b = a - k * TAU
    f_a, f_b = f(big_a), f(big_b)
    while abs(big_b - big_a) > EPSILON:
        big_c = big_a + (big_a - big_b) * f_a / (f_b - f_a)
        f_c = f(big_c)
        if f_c * f_b <= 0:
            big_a, f_a = big_b, f_b
        else:
            f_a /= 2
        big_b, f_b = big_c, f_c
    return math.exp(big_a / 2)


def update(current: Rating, games: list[GameResult]) -> Rating:
    mu, phi = (current.rating - 1500) / SCALE, current.rd / SCALE
    if not games:
        return Rating(current.rating, math.sqrt(phi**2 + current.volatility**2) * SCALE, current.volatility)
    v_inv, delta_sum = 0.0, 0.0
    for game in games:
        mu_j, phi_j = (game.opponent.rating - 1500) / SCALE, game.opponent.rd / SCALE
        e = _expected(mu, mu_j, phi_j)
        v_inv += _g(phi_j) ** 2 * e * (1 - e)
        delta_sum += _g(phi_j) * (game.score - e)
    v = 1 / v_inv
    sigma = _new_volatility(current.volatility, phi, v, v * delta_sum)
    phi_star = math.sqrt(phi**2 + sigma**2)
    new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
    new_mu = mu + new_phi**2 * delta_sum
    return Rating(rating=new_mu * SCALE + 1500, rd=new_phi * SCALE, volatility=sigma)
