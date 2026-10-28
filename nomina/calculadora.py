"""Calcula la nómina de cada empleado aplicando las reglas que le da la política.

La calculadora no sabe qué tipos de empleado existen ni qué bonos hay. Solo sabe:
1. pedirle al empleado sus devengos,
2. aplicar en orden las reglas que le correspondan,
3. validar que el neto no quede negativo.
"""
from operator import attrgetter
from typing import Iterable, Protocol

from nomina.empleados.base import Empleado
from nomina.errores import ContratoNoVigenteError, SalarioNetoNegativoError
from nomina.liquidacion import Liquidacion
from nomina.periodo import Periodo
from nomina.reglas.base import Regla


class FuenteDeReglas(Protocol):
    """Lo único que la calculadora necesita de una política."""

    def reglas_para(self, empleado: Empleado) -> list[Regla]: ...


class CalculadoraNomina:
    def __init__(self, politica: FuenteDeReglas):
        self._politica = politica

    def liquidar(self, empleado: Empleado, periodo: Periodo) -> Liquidacion:
        if not empleado.tiene_contrato_vigente(periodo):
            raise ContratoNoVigenteError(f"{empleado.nombre} no tiene contrato vigente en {periodo}.")

        liquidacion = Liquidacion(empleado, periodo, list(empleado.devengos(periodo)))
        # sorted es estable: dentro de la misma fase se respeta el orden en que se registraron.
        for regla in sorted(self._politica.reglas_para(empleado), key=attrgetter("fase")):
            liquidacion.agregar(regla.aplicar(empleado, liquidacion))

        if liquidacion.salario_neto < 0:
            raise SalarioNetoNegativoError(empleado.nombre, liquidacion.salario_neto)
        return liquidacion

    def liquidar_todos(self, empleados: Iterable[Empleado], periodo: Periodo) -> list[Liquidacion]:
        return [self.liquidar(empleado, periodo) for empleado in empleados]
