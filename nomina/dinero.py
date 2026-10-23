"""Utilidades para manejar plata sin errores de punto flotante.

Uso Decimal en vez de float porque 0.1 + 0.2 en float no da 0.3 exacto,
y en una nómina un peso de diferencia ya es un reclamo.
"""
from decimal import Decimal, ROUND_HALF_UP

UN_PESO = Decimal("1")


def a_decimal(valor) -> Decimal:
    """Convierte int, str, float o Decimal a Decimal sin perder precisión."""
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        # str() evita arrastrar la representación binaria del float
        return Decimal(str(valor))
    return Decimal(valor)


def redondear_pesos(valor) -> Decimal:
    """Redondea al peso más cercano (en Colombia la nómina se paga sin centavos)."""
    return a_decimal(valor).quantize(UN_PESO, rounding=ROUND_HALF_UP)


def formatear_pesos(valor) -> str:
    """Devuelve el valor con formato colombiano, por ejemplo $ 1.234.567."""
    entero = int(redondear_pesos(valor))
    signo = "-" if entero < 0 else ""
    return f"{signo}$ {abs(entero):,}".replace(",", ".")
