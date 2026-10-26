"""Calcula la nómina de cada empleado.

Versión 1: funciona, pero las reglas de cada tipo están amarradas aquí con isinstance.
"""
from decimal import Decimal

from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados import (EmpleadoAsalariado, EmpleadoPorComision, EmpleadoPorHoras)
from nomina.errores import ContratoNoVigenteError, SalarioNetoNegativoError
from nomina.liquidacion import Liquidacion

TARIFA_ARL = Decimal("0.00522")


class CalculadoraNomina:
    def liquidar(self, empleado, periodo) -> Liquidacion:
        if not empleado.tiene_contrato_vigente(periodo):
            raise ContratoNoVigenteError(f"{empleado.nombre} no tiene contrato vigente en {periodo}.")
        liq = Liquidacion(empleado, periodo, list(empleado.devengos(periodo)))
        base = liq.salario_bruto

        if isinstance(empleado, EmpleadoAsalariado) and empleado.tiene_mas_de_anios(5, periodo):
            liq.agregar([Concepto("Bono por antigüedad", base * Decimal("0.10"), TipoConcepto.DEVENGO)])
        if isinstance(empleado, EmpleadoPorComision) and empleado.ventas > 20_000_000:
            liq.agregar([Concepto("Bono por ventas", empleado.ventas * Decimal("0.03"), TipoConcepto.DEVENGO)])

        bruto = liq.salario_bruto
        liq.agregar([
            Concepto("Seguridad social y pensión", bruto * Decimal("0.04"), TipoConcepto.DEDUCCION),
            Concepto("ARL", bruto * TARIFA_ARL, TipoConcepto.DEDUCCION),
        ])

        if isinstance(empleado, (EmpleadoAsalariado, EmpleadoPorComision)):
            liq.agregar([Concepto("Bono de alimentación", 1_000_000, TipoConcepto.BENEFICIO)])
        if (isinstance(empleado, EmpleadoPorHoras) and empleado.acepta_fondo_ahorro
                and empleado.tiene_mas_de_anios(1, periodo)):
            liq.agregar([Concepto("Fondo de ahorro", bruto * Decimal("0.02"), TipoConcepto.APORTE_AHORRO)])

        if liq.salario_neto < 0:
            raise SalarioNetoNegativoError(empleado.nombre, liq.salario_neto)
        return liq

    def liquidar_todos(self, empleados, periodo) -> list[Liquidacion]:
        return [self.liquidar(e, periodo) for e in empleados]
