"""Datos de prueba para probar en el teléfono: un segundo usuario con su equipo rival [SIMULACIÓN].

Solo para la API local de desarrollo (nunca piloto ni producción). Crea el usuario y su equipo en la
misma ciudad, barrio, deporte y modalidad que se indiquen, para encontrarlo en "Buscar rival".

Uso (con el backend corriendo en http://127.0.0.1:8000):
    python dev_tools/seed_test_rival.py Galapa "Villa olimpica" FOOTBALL F5

Credenciales de prueba (solo para la base local; no reutilizar en ningún otro lado):
    correo:     rival.prueba@rival.test
    contraseña: PruebaRival-2026!
"""

import json
import sys
import urllib.error
import urllib.request

API = "http://127.0.0.1:8000/api/v1"
EMAIL, PASSWORD = "rival.prueba@rival.test", "PruebaRival-2026!"


def call(path: str, body: dict[str, object], token: str | None = None) -> dict[str, object]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API}{path}", data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return dict(json.loads(response.read()))
    except urllib.error.HTTPError as error:
        raise SystemExit(f"{path} respondió {error.code}: {error.read().decode()}") from error


def main(city: str, neighborhood: str, sport: str, modality: str) -> None:
    try:
        session = call("/auth/login", {"email": EMAIL, "password": PASSWORD})
        print("El usuario de prueba ya existía; inicié sesión.")
    except SystemExit:
        session = call("/auth/register", {
            "email": EMAIL, "password": PASSWORD, "display_name": "Rival de Prueba", "birth_date": "1995-05-20",
            "role": "COACH", "sports": [sport], "city": city, "neighborhood": neighborhood, "position": None})
        print("Usuario de prueba creado.")
    token = str(session["token"])
    team = call("/teams", {"name": "Rivales de Prueba", "sport_code": sport, "modality_code": modality, "city": city,
                           "neighborhood": neighborhood, "as_coach": True}, token)
    print(f"Equipo creado: {team.get('team', team)}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
