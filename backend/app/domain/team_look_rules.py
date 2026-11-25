"""Cómo se ve el equipo (Sprint 23): el escudo y el diseño elegido para el cuadro de la media.

El escudo se arma con piezas de RIVAL (forma, dos colores y símbolo); no se suben imágenes, así no
hace falta guardar fotos ni moderarlas. Se guarda como "FORMA|#color1|#color2|SÍMBOLO".
El diseño elegido es una especial que el equipo ya ganó o su carta básica ("BASIC"); sin elección,
se muestra la mejor especial que tenga.
"""

from dataclasses import dataclass

from app.domain.errors import DomainError

SHAPES = ("ESCUDO", "CIRCULO", "ROMBO", "BANDERA")
SYMBOLS = ("INICIALES", "ESTRELLA", "RAYO", "CORONA", "BALON")
COLORS = ("#0B6B3A", "#2BD46B", "#06120C", "#FFFFFF", "#F6DE92", "#C0182F", "#FF7A33", "#1D4ED8", "#0EA5E9",
          "#7B4BB0")
BASIC = "BASIC"


@dataclass(frozen=True)
class Crest:
    shape: str
    primary: str
    secondary: str
    symbol: str

    def encode(self) -> str:
        return "|".join((self.shape, self.primary, self.secondary, self.symbol))


def parse_crest(raw: str) -> Crest:
    parts = raw.split("|")
    if len(parts) != 4:
        raise DomainError("INVALID_CREST", "El escudo no tiene el formato esperado.")
    shape, primary, secondary, symbol = parts
    if shape not in SHAPES or symbol not in SYMBOLS:
        raise DomainError("INVALID_CREST", "Esa forma o ese símbolo no existe.")
    if primary not in COLORS or secondary not in COLORS:
        raise DomainError("INVALID_CREST", "Elige los colores de la paleta de RIVAL.")
    if primary == secondary:
        raise DomainError("INVALID_CREST", "Usa dos colores distintos para que el escudo se vea.")
    return Crest(shape, primary, secondary, symbol)


def available_designs(owned: list[str]) -> list[str]:
    """Lo que se puede elegir: la carta básica y las especiales ganadas, en orden de dificultad."""
    return [BASIC, *owned]


def check_choice(choice: str | None, owned: list[str]) -> None:
    if choice is not None and choice not in available_designs(owned):
        raise DomainError("DESIGN_NOT_OWNED", "Ese diseño todavía no lo ha ganado el equipo.")


def shown_design(choice: str | None, owned: list[str], basic: str, best: str | None) -> str:
    """El código que se dibuja. Si la elección ya no aplica, vuelve a la mejor especial o a la básica."""
    if choice == BASIC:
        return basic
    if choice is not None and choice in owned:
        return choice
    return best or basic
