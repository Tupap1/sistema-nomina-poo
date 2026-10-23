"""Un concepto es cada línea del desprendible de pago: salario, horas extra, bono, deducción..."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from nomina.dinero import redondear_pesos
from nomina.validaciones import validar_no_negativo


class TipoConcepto(Enum):
    """Define cómo afecta cada concepto el pago del empleado."""

    DEVENGO = "devengo"              # suma al salario bruto
    DEDUCCION = "deduccion"          # se descuenta del salario bruto
    APORTE_AHORRO = "aporte_ahorro"  # sale del salario y se deposita en el fondo de ahorro
    BENEFICIO = "beneficio"          # lo paga la empresa aparte, no hace parte del salario


@dataclass(frozen=True)
class Concepto:
    """Una línea de la liquidación. El valor siempre es positivo; el tipo dice si suma o resta."""

    nombre: str
    valor: Decimal
    tipo: TipoConcepto

    def __post_init__(self):
        valor = redondear_pesos(validar_no_negativo(self.valor, self.nombre))
        # frozen=True no deja asignar normal, por eso se usa object.__setattr__
        object.__setattr__(self, "valor", valor)
