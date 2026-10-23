"""Validaciones reutilizables. Cada función valida una sola cosa y devuelve el valor ya convertido."""
from decimal import Decimal

from nomina.dinero import a_decimal
from nomina.errores import PorcentajeInvalidoError, ValorNegativoError


def validar_no_negativo(valor, campo: str) -> Decimal:
    """Lanza ValorNegativoError si el valor es menor que cero."""
    numero = a_decimal(valor)
    if numero < 0:
        raise ValorNegativoError(campo, valor)
    return numero


def validar_porcentaje(valor, campo: str) -> Decimal:
    """Acepta porcentajes como fracción: 0.04 es 4 %. Fuera de 0 a 1 es un error."""
    numero = a_decimal(valor)
    if not Decimal("0") <= numero <= Decimal("1"):
        raise PorcentajeInvalidoError(campo, valor)
    return numero
