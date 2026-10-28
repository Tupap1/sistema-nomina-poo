"""Contrato común de todas las reglas de nómina."""
from abc import ABC, abstractmethod
from enum import IntEnum

from nomina.conceptos import Concepto
from nomina.empleados.base import Empleado
from nomina.liquidacion import Liquidacion


class Fase(IntEnum):
    """Orden en que se aplican las reglas. Importa: las deducciones van sobre el bruto ya con bonos."""

    BONOS = 1         # devengos extra que salen del salario o de las ventas
    DEDUCCIONES = 2   # se calculan sobre el salario bruto completo
    BENEFICIOS = 3    # fondo de ahorro y beneficios que paga la empresa


class Regla(ABC):
    """Una regla mira al empleado y a la liquidación que va armándose, y devuelve conceptos nuevos.

    Si no le aplica al empleado, devuelve una lista vacía. Nunca modifica la liquidación
    directamente; de eso se encarga la calculadora.
    """

    fase: Fase

    @abstractmethod
    def aplicar(self, empleado: Empleado, liquidacion: Liquidacion) -> list[Concepto]:
        """Conceptos que agrega esta regla (vacío si no aplica)."""
