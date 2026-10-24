"""Empleado que cobra por hora trabajada, con recargo por horas extra."""
from datetime import date
from decimal import Decimal

from nomina.conceptos import Concepto, TipoConcepto
from nomina.dinero import a_decimal, formatear_pesos
from nomina.empleados.base import Empleado
from nomina.periodo import Periodo
from nomina.validaciones import validar_no_negativo

LIMITE_HORAS_ORDINARIAS = Decimal("40")
FACTOR_HORA_EXTRA = Decimal("1.5")


def _horas_legibles(horas: Decimal) -> str:
    """40.0 se muestra como 40 y 42.5 como 42,5."""
    texto = f"{horas.normalize():f}"
    return texto.replace(".", ",")


class EmpleadoPorHoras(Empleado):
    """Cobra tarifa por hora. Lo que pase de 40 horas se paga a 1,5 veces la tarifa."""

    def __init__(self, identificacion: str, nombre: str, fecha_ingreso: date,
                 tarifa_hora, horas_trabajadas, acepta_fondo_ahorro: bool = False,
                 limite_horas_ordinarias=LIMITE_HORAS_ORDINARIAS, factor_hora_extra=FACTOR_HORA_EXTRA):
        super().__init__(identificacion, nombre, fecha_ingreso)
        self._tarifa_hora = validar_no_negativo(tarifa_hora, "tarifa_hora")
        self.horas_trabajadas = horas_trabajadas  # pasa por el setter, que valida
        self._acepta_fondo_ahorro = bool(acepta_fondo_ahorro)
        self._limite = validar_no_negativo(limite_horas_ordinarias, "limite_horas_ordinarias")
        self._factor_extra = validar_no_negativo(factor_hora_extra, "factor_hora_extra")

    @property
    def tipo(self) -> str:
        return "Por horas"

    @property
    def tarifa_hora(self) -> Decimal:
        return self._tarifa_hora

    @property
    def horas_trabajadas(self) -> Decimal:
        return self._horas_trabajadas

    @horas_trabajadas.setter
    def horas_trabajadas(self, horas) -> None:
        # Las horas cambian cada mes, por eso tienen setter; pero nunca pueden ser negativas.
        self._horas_trabajadas = validar_no_negativo(horas, "horas_trabajadas")

    @property
    def acepta_fondo_ahorro(self) -> bool:
        return self._acepta_fondo_ahorro

    @property
    def horas_ordinarias(self) -> Decimal:
        return min(self._horas_trabajadas, self._limite)

    @property
    def horas_extra(self) -> Decimal:
        return max(Decimal("0"), self._horas_trabajadas - self._limite)

    def devengos(self, periodo: Periodo) -> list[Concepto]:
        tarifa_extra = self._tarifa_hora * self._factor_extra
        conceptos = [Concepto(
            "Horas ordinarias",
            self.horas_ordinarias * self._tarifa_hora,
            TipoConcepto.DEVENGO,
            f"{_horas_legibles(self.horas_ordinarias)} h x {formatear_pesos(self._tarifa_hora)}",
        )]
        if self.horas_extra > 0:
            conceptos.append(Concepto(
                "Horas extra",
                self.horas_extra * tarifa_extra,
                TipoConcepto.DEVENGO,
                f"{_horas_legibles(self.horas_extra)} h x {formatear_pesos(tarifa_extra)}",
            ))
        return conceptos
