"""Establecimiento de prueba para probar reservas y check-in en el teléfono [SIMULACIÓN].

Solo para la API local de desarrollo. Crea al dueño, el establecimiento, una cancha y una franja que
cubre un partido (desde 30 min antes hasta 90 min después de la hora indicada). La ubicación del
establecimiento NO se fija aquí: la guarda su dueño desde el teléfono ("Guardar: estoy en la cancha").

Uso (con el backend corriendo):
    python dev_tools/seed_test_venue.py Galapa "Villa olimpica" FOOTBALL 2026-11-25T13:00:00+00:00

Credenciales de prueba (solo para la base local; no reutilizar en ningún otro lado):
    correo:     cancha.prueba@rival.test
    contraseña: PruebaCancha-2026!
"""

import sys
from datetime import datetime, timedelta

from seed_test_rival import call

EMAIL, PASSWORD = "cancha.prueba@rival.test", "PruebaCancha-2026!"


def owner_token(city: str, neighborhood: str, sport: str) -> str:
    try:
        session = call("/auth/login", {"email": EMAIL, "password": PASSWORD})
    except SystemExit:
        session = call("/auth/register", {
            "email": EMAIL, "password": PASSWORD, "display_name": "Cancha de Prueba", "birth_date": "1988-03-14",
            "role": "VENUE_OWNER", "sports": [sport], "city": city, "neighborhood": neighborhood,
            "position": None, "accept_terms": True})
    return str(session["token"])


def main(city: str, neighborhood: str, sport: str, kickoff_iso: str) -> None:
    token = owner_token(city, neighborhood, sport)
    kickoff = datetime.fromisoformat(kickoff_iso)
    venue = call("/venues", {"name": "Canchas de Prueba", "address": "Calle 10 # 5-20", "city": city,
                             "neighborhood": neighborhood, "reference_price": "60000"}, token)
    venue_id = venue["venue"]["id"]  # type: ignore[index]
    court = call(f"/venues/{venue_id}/courts", {"name": "Cancha 1", "sport_code": sport, "surface": "Sintética"},
                 token)
    court_id = court["courts"][0]["id"]  # type: ignore[index]
    call(f"/courts/{court_id}/slots", {"starts_at": (kickoff - timedelta(minutes=30)).isoformat(),
                                       "ends_at": (kickoff + timedelta(minutes=90)).isoformat()}, token)
    print(f"Establecimiento {venue_id} creado en {city} con la cancha {court_id} "
          f"y una franja para {kickoff:%d/%m %H:%M} UTC.")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
