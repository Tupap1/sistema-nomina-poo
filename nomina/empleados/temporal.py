"""Empleado con salario fijo y contrato a término definido."""
from datetime import date

from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados.base import Empleado
from nomina.errores import ContratoInvalidoError
from nomina.periodo import Periodo
from nomina.validaciones import validar_no_negativo


class EmpleadoTemporal(Empleado):
    """Salario fijo mensual mientras dure el contrato. No tiene bonos ni beneficios."""

    def __init__(self, identificacion: str, nombre: str, fecha_ingreso: date,
                 salario_mensual, fecha_fin_contrato: date):
        super().__init__(identificacion, nombre, fecha_ingreso)
        if fecha_fin_contrato < fecha_ingreso:
            raise ContratoInvalidoError("El contrato temporal no puede terminar antes de empezar.")
        self._salario_mensual = validar_no_negativo(salario_mensual, "salario_mensual")
        self._fecha_fin_contrato = fecha_fin_contrato

    @property
    def tipo(self) -> str:
        return "Temporal"

    @property
    def salario_mensual(self):
        return self._salario_mensual

    @property
    def fecha_fin_contrato(self) -> date:
        return self._fecha_fin_contrato

    def tiene_contrato_vigente(self, periodo: Periodo) -> bool:
        """Vigente si el contrato se cruza con el mes: empezó antes del corte y no terminó antes del inicio."""
        return super().tiene_contrato_vigente(periodo) and self._fecha_fin_contrato >= periodo.inicio

    def devengos(self, periodo: Periodo) -> list[Concepto]:
        return [Concepto("Salario básico", self._salario_mensual, TipoConcepto.DEVENGO)]
