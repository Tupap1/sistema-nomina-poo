"""Beneficios adicionales: bono de alimentación y fondo de ahorro."""
from typing import Protocol

from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados.base import Empleado
from nomina.liquidacion import Liquidacion
from nomina.periodo import Periodo
from nomina.reglas.base import Fase, Regla
from nomina.validaciones import validar_no_negativo, validar_porcentaje


class BonoDeAlimentacion(Regla):
    """Permanentes (asalariado y comisión): $1.000.000 al mes que paga la empresa.

    Va como beneficio no salarial: se suma a lo que recibe, pero no entra en la base
    de las deducciones.
    """

    fase = Fase.BENEFICIOS
    NOMBRE = "Bono de alimentación"

    def __init__(self, valor=1_000_000):
        self._valor = validar_no_negativo(valor, "bono_alimentacion")

    def aplicar(self, empleado: Empleado, liquidacion: Liquidacion) -> list[Concepto]:
        return [Concepto(self.NOMBRE, self._valor, TipoConcepto.BENEFICIO, "lo cubre la empresa")]


class PuedeAhorrar(Protocol):
    """Empleado que puede decidir si entra o no al fondo de ahorro."""

    @property
    def acepta_fondo_ahorro(self) -> bool: ...

    def tiene_mas_de_anios(self, anios: int, periodo: Periodo) -> bool: ...


class FondoDeAhorro(Regla):
    """Por horas con MÁS de 1 año y que acepte: 2 % del salario se deposita cada mes en el fondo."""

    fase = Fase.BENEFICIOS
    NOMBRE = "Fondo de ahorro"

    def __init__(self, porcentaje="0.02", anios_minimos: int = 1):
        self._porcentaje = validar_porcentaje(porcentaje, "porcentaje_fondo_ahorro")
        self._anios_minimos = anios_minimos

    def aplicar(self, empleado: PuedeAhorrar, liquidacion: Liquidacion) -> list[Concepto]:
        if not empleado.acepta_fondo_ahorro:
            return []
        if not empleado.tiene_mas_de_anios(self._anios_minimos, liquidacion.periodo):
            return []
        return [Concepto(self.NOMBRE, liquidacion.salario_bruto * self._porcentaje, TipoConcepto.APORTE_AHORRO,
                         "2 % del bruto")]
