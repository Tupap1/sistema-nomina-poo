"""Bonos que suman al salario bruto."""
from decimal import Decimal
from typing import Protocol

from nomina.conceptos import Concepto, TipoConcepto
from nomina.dinero import a_decimal, formatear_pesos
from nomina.empleados.base import Empleado
from nomina.liquidacion import Liquidacion
from nomina.reglas.base import Fase, Regla
from nomina.validaciones import validar_no_negativo, validar_porcentaje


class BonoPorAntiguedad(Regla):
    """Asalariado: 10 % del salario si lleva MÁS de 5 años en la empresa."""

    fase = Fase.BONOS
    NOMBRE = "Bono por antigüedad"

    def __init__(self, porcentaje="0.10", anios_minimos: int = 5):
        self._porcentaje = validar_porcentaje(porcentaje, "porcentaje_bono_antiguedad")
        self._anios_minimos = anios_minimos

    def aplicar(self, empleado: Empleado, liquidacion: Liquidacion) -> list[Concepto]:
        if not empleado.tiene_mas_de_anios(self._anios_minimos, liquidacion.periodo):
            return []
        # El 10 % sale del salario que devenga por su trabajo, no de otros bonos que ya lleve.
        base = sum((c.valor for c in empleado.devengos(liquidacion.periodo)), Decimal("0"))
        return [Concepto(self.NOMBRE, base * self._porcentaje, TipoConcepto.DEVENGO,
                         f"más de {self._anios_minimos} años")]


class TieneVentas(Protocol):
    """Cualquier empleado que reporte ventas en el mes."""

    @property
    def ventas(self) -> Decimal: ...


class BonoPorVentas(Regla):
    """Comisión: 3 % adicional sobre las ventas si superan $20.000.000."""

    fase = Fase.BONOS
    NOMBRE = "Bono por ventas"

    def __init__(self, umbral=20_000_000, porcentaje="0.03"):
        self._umbral = validar_no_negativo(umbral, "umbral_bono_ventas")
        self._porcentaje = validar_porcentaje(porcentaje, "porcentaje_bono_ventas")

    def aplicar(self, empleado: TieneVentas, liquidacion: Liquidacion) -> list[Concepto]:
        ventas = a_decimal(empleado.ventas)
        if ventas <= self._umbral:  # "superan" = estrictamente mayor
            return []
        return [Concepto(self.NOMBRE, ventas * self._porcentaje, TipoConcepto.DEVENGO,
                         f"ventas sobre {formatear_pesos(self._umbral)}")]
