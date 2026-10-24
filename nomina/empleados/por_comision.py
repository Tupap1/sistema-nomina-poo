"""Empleado con salario base más comisión sobre ventas."""
from datetime import date
from decimal import Decimal

from nomina.conceptos import Concepto, TipoConcepto
from nomina.dinero import formatear_pesos
from nomina.empleados.base import Empleado
from nomina.periodo import Periodo
from nomina.validaciones import validar_no_negativo, validar_porcentaje


class EmpleadoPorComision(Empleado):
    """Salario base + un porcentaje de lo que vendió en el mes."""

    def __init__(self, identificacion: str, nombre: str, fecha_ingreso: date,
                 salario_base, porcentaje_comision, ventas):
        super().__init__(identificacion, nombre, fecha_ingreso)
        self._salario_base = validar_no_negativo(salario_base, "salario_base")
        self._porcentaje_comision = validar_porcentaje(porcentaje_comision, "porcentaje_comision")
        self.ventas = ventas  # pasa por el setter, que valida

    @property
    def tipo(self) -> str:
        return "Por comisión"

    @property
    def salario_base(self) -> Decimal:
        return self._salario_base

    @property
    def porcentaje_comision(self) -> Decimal:
        return self._porcentaje_comision

    @property
    def ventas(self) -> Decimal:
        return self._ventas

    @ventas.setter
    def ventas(self, valor) -> None:
        # Regla del enunciado: las ventas no pueden ser menores a $0.
        self._ventas = validar_no_negativo(valor, "ventas")

    def devengos(self, periodo: Periodo) -> list[Concepto]:
        porcentaje = f"{(self._porcentaje_comision * 100).normalize():f}".replace(".", ",")
        return [
            Concepto("Salario básico", self._salario_base, TipoConcepto.DEVENGO),
            Concepto("Comisión por ventas", self._ventas * self._porcentaje_comision, TipoConcepto.DEVENGO,
                     f"{porcentaje} % de {formatear_pesos(self._ventas)}"),
        ]
