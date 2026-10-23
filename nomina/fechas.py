"""Cálculos de antigüedad con fechas reales, no con años redondeados a mano."""
from datetime import date


def sumar_anios(fecha: date, anios: int) -> date:
    """Suma años a una fecha. Si cae en 29 de febrero de un año no bisiesto, usa el 28."""
    try:
        return fecha.replace(year=fecha.year + anios)
    except ValueError:
        return fecha.replace(year=fecha.year + anios, day=28)


def tiene_mas_de(anios: int, desde: date, hasta: date) -> bool:
    """True solo si entre 'desde' y 'hasta' hay MÁS de 'anios' años.

    El enunciado dice "más de 5 años", así que cumplir exactamente 5 años ese día
    todavía no cuenta. Desde el día siguiente sí.
    """
    return hasta > sumar_anios(desde, anios)
