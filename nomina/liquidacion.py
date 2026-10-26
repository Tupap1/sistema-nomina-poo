"""El resultado de liquidar a un empleado en un periodo: su desprendible de pago."""
from dataclasses import dataclass, field
from decimal import Decimal

from nomina.conceptos import Concepto, TipoConcepto
from nomina.empleados.base import Empleado
from nomina.periodo import Periodo

CERO = Decimal("0")


@dataclass
class Liquidacion:
    """Guarda los conceptos y calcula los totales. No decide reglas, solo suma y resta."""

    empleado: Empleado
    periodo: Periodo
    conceptos: list[Concepto] = field(default_factory=list)

    def agregar(self, conceptos: list[Concepto]) -> None:
        self.conceptos.extend(conceptos)

    def conceptos_de(self, tipo: TipoConcepto) -> list[Concepto]:
        return [c for c in self.conceptos if c.tipo is tipo]

    def total_de(self, tipo: TipoConcepto) -> Decimal:
        return sum((c.valor for c in self.conceptos_de(tipo)), CERO)

    def valor_de(self, nombre: str) -> Decimal:
        """Valor de un concepto por nombre; cero si no aparece en la liquidación."""
        return sum((c.valor for c in self.conceptos if c.nombre == nombre), CERO)

    @property
    def salario_bruto(self) -> Decimal:
        return self.total_de(TipoConcepto.DEVENGO)

    @property
    def total_deducciones(self) -> Decimal:
        return self.total_de(TipoConcepto.DEDUCCION)

    @property
    def aporte_fondo_ahorro(self) -> Decimal:
        return self.total_de(TipoConcepto.APORTE_AHORRO)

    @property
    def beneficios_no_salariales(self) -> Decimal:
        return self.total_de(TipoConcepto.BENEFICIO)

    @property
    def salario_neto(self) -> Decimal:
        """Bruto menos deducciones y menos lo que se va al fondo de ahorro."""
        return self.salario_bruto - self.total_deducciones - self.aporte_fondo_ahorro

    @property
    def total_a_recibir(self) -> Decimal:
        """Salario neto más los beneficios que paga la empresa aparte (bono de alimentación)."""
        return self.salario_neto + self.beneficios_no_salariales
