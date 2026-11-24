"""Claves de búsqueda: "Bogotá", "BOGOTA" y "bogota" encuentran lo mismo."""

import unicodedata


def search_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(without_accents.casefold().split())
