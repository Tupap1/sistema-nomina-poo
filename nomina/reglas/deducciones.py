"""Deducciones que se restan del salario bruto."""
from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados.base import Empleado
from nomina.liquidacion import Liquidacion
from nomina.reglas.base import Fase, Regla
from nomina.validaciones import validar_no_negativo, validar_porcentaje


def _porcentaje_legible(porcentaje) -> str:
    return f"{(porcentaje * 100).normalize():f}".replace(".", ",") + " %"


class DeduccionPorcentual(Regla):
    """Descuenta un porcentaje del salario bruto. Sirve para seguridad social, pensión y ARL."""

    fase = Fase.DEDUCCIONES

    def __init__(self, nombre: str, porcentaje):
        self._nombre = nombre
        self._porcentaje = validar_porcentaje(porcentaje, nombre)

    def aplicar(self, empleado: Empleado, liquidacion: Liquidacion) -> list[Concepto]:
        return [Concepto(self._nombre, liquidacion.salario_bruto * self._porcentaje, TipoConcepto.DEDUCCION,
                         f"{_porcentaje_legible(self._porcentaje)} del bruto")]


class DeduccionFija(Regla):
    """Descuenta un valor fijo, por ejemplo una libranza o un embargo.

    El enunciado no la pide, pero muestra cómo se agrega una deducción nueva sin tocar
    la calculadora, y es la forma de probar la regla de "neto no negativo".
    """

    fase = Fase.DEDUCCIONES

    def __init__(self, nombre: str, valor):
        self._nombre = nombre
        self._valor = validar_no_negativo(valor, nombre)

    def aplicar(self, empleado: Empleado, liquidacion: Liquidacion) -> list[Concepto]:
        return [Concepto(self._nombre, self._valor, TipoConcepto.DEDUCCION)]
