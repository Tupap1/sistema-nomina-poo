"""Empleado con salario fijo mensual."""
from datetime import date

from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados.base import Empleado
from nomina.periodo import Periodo
from nomina.validaciones import validar_no_negativo


class EmpleadoAsalariado(Empleado):
    """Gana lo mismo cada mes. Su bono por antigüedad lo pone una regla aparte."""

    def __init__(self, identificacion: str, nombre: str, fecha_ingreso: date, salario_mensual):
        super().__init__(identificacion, nombre, fecha_ingreso)
        self._salario_mensual = validar_no_negativo(salario_mensual, "salario_mensual")

    @property
    def tipo(self) -> str:
        return "Asalariado"

    @property
    def salario_mensual(self):
        return self._salario_mensual

    def devengos(self, periodo: Periodo) -> list[Concepto]:
        return [Concepto("Salario básico", self._salario_mensual, TipoConcepto.DEVENGO)]
